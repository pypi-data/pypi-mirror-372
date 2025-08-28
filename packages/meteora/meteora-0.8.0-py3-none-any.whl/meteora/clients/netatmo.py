"""Netatmo client."""

import logging as lg
import webbrowser
from collections.abc import Mapping, Sequence

import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj
from requests_cache import CacheMixin
from requests_oauthlib import OAuth2Session
from shapely import geometry
from tqdm import tqdm

from meteora import settings, utils
from meteora.clients.base import BaseJSONClient
from meteora.mixins import StationsEndpointMixin, VariablesHardcodedMixin
from meteora.utils import DateTimeType, KwargsType, RegionType, VariablesType

# to show a progress bar in pandas/geopandas apply
tqdm.pandas()

# API endpoints
BASE_URL = "https://api.netatmo.com"
OAUTH2_TOKEN_ENDPOINT = f"{BASE_URL}/oauth2/token"
AUTHORIZATION_ENDPOINT = f"{BASE_URL}/oauth2/authorize"
STATIONS_ENDPOINT = f"{BASE_URL}/api/getpublicdata"
TS_ENDPOINT = f"{BASE_URL}/api/getmeasure"
REDIRECT_URI = "https://dev.netatmo.com/apps"

# useful constants
STATIONS_GDF_ID_COL = "id"
# there is no label for time on the returned json for `ts_df`, we generate them
TS_DF_STATIONS_ID_COL = "station_id"
TS_DF_TIME_COL = "time"
VARIABLES_ID_COL = "code"
VARIABLES_LABEL_COL = "description"

# DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

# note that Netatmo's nomeclature changes depending on the API endpoint: in
# `getpublicdata` (which can be used to get the list of stations with their latest
# observations), precipitation is "rain_live" whereas in `getmeasure` (which is used to
# get past measurements of a given station and module) it is "rain". Similarly, wind
# speed and direction are "wind_strength" and "wind_angle" in `getpublicdata` but
# "windstrength" and "windangle" in `getmeasure`.
# From the `getmeasure` endpoint documentation at
# https://dev.netatmo.com/apidocumentation/weather#getmeasure, we have:
# - Temperature data (°C) = {temperature, min_temp, max_temp, date_min_temp,
#   date_max_temp}
# - Humidity data (%) = {humidity, min_hum, max_hum, date_min_hum, date_max_hum}
# - CO2 data (ppm) = {co2, min_co2, max_co2, date_min_co2, date_max_co2}
# - Pressure data (bar) = {pressure, min_pressure, max_pressure, date_min_pressure,
#   date_max_pressure}
# - Noise data (db) = {noise, min_noise, max_noise, date_min_noise, date_max_noise}
# - Rain data (mm) = {rain, min_rain, max_rain, sum_rain, date_min_rain, date_max_rain}
# - Wind data (km/h, °) = {windstrength, windangle, guststrength, gustangle,
#   date_min_gust, date_max_gust}
VARIABLES_DICT = {
    "temperature": "Temperature",
    "humidity": "Humidity",
    "pressure": "Pressure",
    "rain": "Rain",
    "windstrength": "Wind speed",
    "windangle": "Wind direction",
}
ECV_DICT = {
    # "precipitation": "rain_live",
    "preciptation": "rain",
    # pressure
    "pressure": "pressure",
    # temperature
    "temperature": "temperature",
    # water vapour
    "relative_humidity": "humidity",
    # wind
    # "surface_wind_speed": "wind_strength",
    # "surface_wind_direction": "wind_angle",
    "wind_speed": "windstrength",
    "wind_direction": "windangle",
}

# Netatmo stations can have up to three modules: The NAMain module is for pressure,
# NAModule1 for temperature and humidity, NAModule2 for wind and NAModule3 for rain.
# The dict below maps the variable names (in Netatmo's API nomenclature) to the module
# types.
MODULE_VAR_DICT = {
    "NAMain": ["pressure"],
    "NAModule1": ["temperature", "humidity"],
    "NAModule2": ["windstrength", "windangle"],
    "NAModule3": ["rain"],
}

# default values
GETMEASURE_SCALE = "30min"
GETMEASURE_LIMIT = 1024
# ACHTUNG: boolean request parameters need to be in lowercase otherwise the API will
# return an error
# GETMEASURE_OPTIMIZE = "true"
GETMEASURE_REAL_TIME = False

# for API limits regarding the number of stations in large regions
WINDOW_SIZE = 0.1  # degrees
TEN_SECONDS_REQUESTS_LIMIT = 50  # requests
HOURLY_REQUESTS_LIMIT = 500  # requests
# to convert the "scale" parameter in `getmeasure` to a pandas frequency alias
# https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases
SCALE_TO_FREQ_DICT = {
    "30min": "30min",
    "1hour": "h",
    "3hours": "3h",
    "1day": "D",
    "1week": "W",
    "1month": "ME",
}

PAUSE = 1
TIMEOUT = 180


# utils
## auth
def _browser_fetch_token(session, client_secret):
    auth_url, state = session.authorization_url(AUTHORIZATION_ENDPOINT)
    # TODO: automate getting the auth code? e.g., stackoverflow.com/questions/76783429
    webbrowser.open(auth_url)
    auth_code = input("Enter authorization code: ")
    _ = session.fetch_token(
        # self.session.auto_refresh_url,
        OAUTH2_TOKEN_ENDPOINT,
        client_secret=client_secret,
        code=auth_code,
    )


class CachedOAuth2Session(CacheMixin, OAuth2Session):
    """Session with features from both CachedSession and OAuth2Session."""

    def get(
        self, url: str, params: KwargsType, *, headers: KwargsType, **kwargs: KwargsType
    ):
        """Send get request, cache only non-empty responses and retry for empty ones."""
        response = CacheMixin.get(self, url, params, headers=headers, **kwargs)
        # ACHTUNG: this is Netatmo-specific
        response_json = response.json()
        if "body" in response_json:
            pass
        elif "error" in response_json:
            error_code = response_json["error"].get("code", None)
            if error_code == 1:
                # Access token is missing
                _browser_fetch_token(self, self._client_secret)
                # retry
                return self.get(url, params, headers=headers, **kwargs)
            # elif error_code == 26
            # {'error': {'code': 26, 'message': 'User usage reached'}}
            elif error_code == 9:
                # {'error': {'code': 9, 'message': 'Device not found'}}
                pass
            else:
                msg = f"Received {response_json} for {url} with parameters {params}"
                if settings.NETATMO_ON_GET_ERROR == "log":
                    utils.log(
                        msg,
                        level=lg.WARNING,
                    )
                else:  # if settings.NETATMO_ON_GET_ERROR == "raise":
                    raise ValueError(msg)
        return response


class NetatmoConnect:
    """NetatmoConnect."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        redirect_uri: str | None = None,
        token: dict | None = None,
        use_cache: bool | None = None,
    ) -> None:
        """Netatmo connection.

        Parameters
        ----------
        client_id : str
            Client ID.
        client_secret : str
            Client secret.
        redirect_uri : str, optional
            Redirect URI for the Netatmo app, used for the "Authorization code" grant
            type authentication (by default). Ignored if `token` is provided.
        token : dict, optional
            Token dictionary with the keys "access_token" and "refresh_token".
        use_cache : bool, optional
            Whether to use the cache. If None, the value from `settings.USE_CACHE` will
            be used.
        """
        # super(NetatmoConnect, self).__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = "read_station"
        if token is None:
            if redirect_uri is None:
                redirect_uri = REDIRECT_URI

        if use_cache is None:
            use_cache = settings.USE_CACHE
        self.oauth_kwargs = {
            "client_id": client_id,
            "scope": self.scope,
            "redirect_uri": redirect_uri,
            # "token": token,
            # "auto_refresh_url": OAUTH2_TOKEN_ENDPOINT,
            # "auto_refresh_kwargs": dict(
            #     grant_type="refresh_token",
            #     refresh_token=token["refresh_token"],
            #     client_id=self.client_id,
            #     client_secret=self.client_secret,
            #  )
        }
        if use_cache:
            self.cache_kwargs = {
                "cache_name": settings.CACHE_NAME,
                "backend": settings.CACHE_BACKEND,
                "expire_after": settings.CACHE_EXPIRE,
            }
            session = CachedOAuth2Session(
                token=token, **self.cache_kwargs, **self.oauth_kwargs
            )
            # TODO: better way to get the client secret in `CachedOAuth2Session`?
            session._client_secret = client_secret
        else:
            session = OAuth2Session(
                token=token,
                **self.oauth_kwargs,
            )
            if session.token:
                # session.token is either None or {}
                _browser_fetch_token(session, client_secret)
        self._session = session


## response/data processing


def _process_station_record(station_record: dict) -> dict:
    """Transform a single station record (API JSON) into a flat dictionary.

    The target flat dictionaries have up to six metadata keys (i.e., station id,
    longitude, latitude and the id of each of the available modules - up to three) and
    then a key for each measured variable with its latest observation as value.

    Parameters
    ----------
    station_record : dict
        Input dictionary of station metadata and observations as returned by the Netatmo
        API.

    Returns
    -------
    obs_dict: dict
        Flat dictionary of station metadata and observations.

    """
    # station metadata
    # id
    station_dict = {
        "id": station_record["_id"],
        # "geometry": geometry.Point(*station_record["place"]["location"]),
    }

    # location info
    place_dict = station_record["place"].copy()
    # unpack lat/lon
    station_dict.update(
        {key: val for key, val in zip(["lon", "lat"], place_dict.pop("location"))}
    )
    station_dict.update(place_dict)

    # module types
    module_types = station_record["module_types"]
    # add the module ids
    station_dict.update(
        {module_types[module_id]: module_id for module_id in module_types}
    )
    # note that NAMain (for pressure) is omitted in "module_types" so we have to get
    # them from "measures"
    # ACHTUNG: note that we are already iterating `station_record["measures"]` below to
    # get the latest observations, so it may be more efficient to merge the two loops
    for module_key, module_value_dict in station_record["measures"].items():
        try:
            if "pressure" in module_value_dict["type"]:
                station_dict["NAMain"] = module_key
        except KeyError:
            # this corresponds to the NAModule3 (rain) which does not have a "type" key
            pass

    # station observations
    # NOTE: in the "modules" and "module_types" of station_record, there is the info
    # about the sensors, i.e., NAMain is for pressure (omitted in "module_types"),
    # NAModule1 is for temperature and humidity, NAModule2 is for wind, NAModule3 is for
    # rain. It may be more efficient to use this information to query the
    # station_record["measures"].
    def get_module1_value_dict(record):
        res_dict = record["res"]
        values = res_dict[list(res_dict.keys())[0]]

        return {val: values[i] for i, val in enumerate(record["type"])}

    get_value_dict = {
        "NAMain": lambda record: {"pressure": next(iter(record["res"].values()))[0]},
        "NAModule1": get_module1_value_dict,
        "NAModule2": lambda record: {
            wind_var: record[wind_var] for wind_var in ["wind_strength", "wind_angle"]
        },
        "NAModule3": lambda record: {"rain_live": record["rain_live"]},
    }

    for module_key, module_value_dict in station_record["measures"].items():
        station_dict.update(
            get_value_dict[module_types.get(module_key, "NAMain")](module_value_dict)
        )

    return station_dict


class NetatmoClient(StationsEndpointMixin, VariablesHardcodedMixin, BaseJSONClient):
    """Netatmo client.

    Parameters
    ----------
    region : str, Sequence, GeoSeries, GeoDataFrame, PathLike, or IO
        The region to process. This can be either:

        -  A string with a place name (Nominatim query) to geocode.
        -  A sequence with the west, south, east and north bounds.
        -  A geometric object, e.g., shapely geometry, or a sequence of geometric
           objects. In such a case, the value will be passed as the `data` argument of
           the GeoSeries constructor, and needs to be in the same CRS as the one used by
           the client's class (i.e., the `CRS` class attribute).
        -  A geopandas geo-series or geo-data frame.
        -  A filename or URL, a file-like object opened in binary ('rb') mode, or a Path
           object that will be passed to `geopandas.read_file`.
    client_id, client_secret : str
        Client ID and secret of the Netatmo API, used to authenticate the client, i.e.,
        to obtain and refresh tokens.
    redirect_uri : str, optional
        Redirect URI for the Netatmo app, used for the "Authorization code" grant type
        authentication (by default). Ignored if `token` is provided. If None, the value
        from `settings.REDIRECT_URI` is used.
    token : dict, optional
        Token dictionary with the keys "access_token" and "refresh_token".
    window_size : numeric, optional
        Window size (square side, in degrees) to split the region into non-overlapping
        windows (to bypass Netatmo API limits). If None, the value from
        `clients.netatmo.WINDOW_SIZE` is used.
    sjoin_kwargs : dict, optional
        Keyword arguments to pass to the `geopandas.sjoin` function when filtering the
        stations within the region. If None, the value from `settings.SJOIN_KWARGS` is
        used.
    """

    # geom constant
    X_COL = "lon"
    Y_COL = "lat"
    CRS = pyproj.CRS("epsg:4326")

    # _datetime_format = DATETIME_FORMAT

    # API endpoints
    _stations_endpoint = STATIONS_ENDPOINT
    _ts_endpoint = TS_ENDPOINT

    # data frame labels constants
    _stations_gdf_id_col = STATIONS_GDF_ID_COL
    _ts_df_stations_id_col = TS_DF_STATIONS_ID_COL
    _ts_df_time_col = TS_DF_TIME_COL
    _variables_id_col = VARIABLES_ID_COL
    _variables_label_col = VARIABLES_LABEL_COL
    _variables_dict = VARIABLES_DICT
    _ecv_dict = ECV_DICT

    def __init__(
        self,
        region: RegionType,
        client_id: str,
        client_secret: str,
        *,
        redirect_uri: str | None = None,
        token: str | None = None,
        window_size: float | None = None,
        **sjoin_kwargs: KwargsType,
    ) -> None:
        """Initialize Netatmo client."""
        # ACHTUNG: CRS must be set before region
        self.region = region

        # to avoid API limits regarding the number of stations, we need to split the
        # region
        if window_size is None:
            window_size = WINDOW_SIZE
        # start: split the region into windows
        # TODO: DRY as part of some mixin?
        grid_x, grid_y = np.meshgrid(
            np.arange(
                self.region.total_bounds[0], self.region.total_bounds[2], window_size
            ),
            np.arange(
                self.region.total_bounds[1], self.region.total_bounds[3], window_size
            ),
            indexing="xy",
        )
        # vectorize the grid as a geo series
        flat_grid_x = grid_x.flatten()
        flat_grid_y = grid_y.flatten()
        self.region_window_gser = gpd.GeoSeries(
            pd.DataFrame(
                {
                    "xmin": flat_grid_x,
                    "ymin": flat_grid_y,
                    "xmax": flat_grid_x + window_size,
                    "ymax": flat_grid_y + window_size,
                }
            ).apply(lambda row: geometry.box(*row), axis=1),
            crs=self.CRS,
        )
        # end: split the region into windows

        if sjoin_kwargs is None:
            sjoin_kwargs = {}
        self.SJOIN_KWARGS = sjoin_kwargs

        # station data/metadata columns to keep
        self._stations_df_columns = [
            self._stations_gdf_id_col,
            self.X_COL,
            self.Y_COL,
            "timezone",
            "country",
            "altitude",
            "city",
            "street",
            "NAMain",
            "NAModule1",
            "NAModule2",
            "NAModule3",
        ]

        # # need to call super().__init__() to set the cache
        # super().__init__()
        # the Netatmo client is different because it uses OAuth2 managed via the
        # NetatmoConnect class, therefore we will not call the super init method
        # but rather manage it here
        # TODO: approach to get API keys from env vars in all clients
        # self.conn = NetatmoConnect(
        #     client_id, client_secret, redirect_uri=redirect_uri, token=token
        # )
        # TODO: for netatmo, API limit is raises code 403 -> manage it
        self._session = NetatmoConnect(
            client_id, client_secret, redirect_uri=redirect_uri, token=token
        )._session

    def _get_stations_df(self) -> pd.DataFrame:
        # use this to drop the measurements
        # we need the module ids to then query for the observations
        def _station_records_from_window(window):
            params = dict(
                lon_sw=window.bounds[0],
                lat_sw=window.bounds[1],
                lon_ne=window.bounds[2],
                lat_ne=window.bounds[3],
            )
            response_json = self._get_content_from_url(
                self._stations_endpoint,
                params=params,
            )
            if "body" in response_json:
                return response_json
            else:
                # TODO: log returned error in response
                # e.g., {'error': {'code': 2, 'message': 'Invalid access token'}}
                # TODO: retry?
                utils.log(
                    f"No stations returned for bounding box: {params}",
                    level=lg.WARNING,
                )
                return None

        _stations_df = pd.concat(
            [
                pd.DataFrame(
                    [
                        _process_station_record(station_record)
                        for station_record in response_json["body"]
                    ],
                )
                for response_json in self.region_window_gser.progress_apply(
                    # for response_json, _ in self.region_window_gser.apply(
                    # lambda window: self._perform_request(
                    #     STATIONS_ENDPOINT,
                    #     data=dict(
                    #         lon_sw=window.bounds[0],
                    #         lat_sw=window.bounds[1],
                    #         lon_ne=window.bounds[2],
                    #         lat_ne=window.bounds[3],
                    #     ),
                    # )
                    # we can use the cache to get the stations (note that the same
                    # endpoint is used to get the latest observations)
                    lambda window: self._get_content_from_url(
                        self._stations_endpoint,
                        params=dict(
                            lon_sw=window.bounds[0],
                            lat_sw=window.bounds[1],
                            lon_ne=window.bounds[2],
                            lat_ne=window.bounds[3],
                        ),
                    )
                )
            ],
            axis="rows",
            ignore_index=True,
        )

        # use groupby-first to drop the duplicated stations
        return (
            _stations_df[_stations_df.columns.intersection(self._stations_df_columns)]
            .groupby(self._stations_gdf_id_col)
            .first()
            .reset_index()
        )

    def _ts_params(
        self,
        variable_ids: Sequence,
        start: DateTimeType,
        end: DateTimeType,
        scale: str | None,
        limit: int | None,
        optimize: bool | None,
        real_time: bool | None,
    ) -> dict:
        # process `getmeasure` parameters
        if scale is None:
            scale = GETMEASURE_SCALE
        if limit is None:
            limit = GETMEASURE_LIMIT
        # if optimize is None:
        #     optimize = GETMEASURE_OPTIMIZE
        if real_time is None:
            real_time = GETMEASURE_REAL_TIME

        return dict(
            variable_ids=variable_ids,
            date_begin=start,
            date_end=end,
            scale=scale,
            limit=limit,
            optimize=optimize,
            real_time=real_time,
        )

    def _ts_df_from_endpoint(self, ts_params: Mapping) -> pd.DataFrame:
        # we can only query one module at a time, which means that (i) we can only query
        # one station at a time and (ii) for that station, we can only query the
        # variables measured by a single module at a time, i.e., pressure in "NAMain",
        # temperature and humidity in "NAModule1", wind in "NAModule2", and rain in
        # "NAModule3".
        # we first define this dict, i.e., the subset of `MODULE_VAR_DICT` but only for
        # the needed modules/variables
        _ts_params = ts_params.copy()
        variable_ids = _ts_params.pop("variable_ids")
        module_var_dict = {module_type: [] for module_type in MODULE_VAR_DICT}
        for module_type, module_vars in MODULE_VAR_DICT.items():
            for variable_id in variable_ids:
                if variable_id in module_vars:
                    module_var_dict[module_type].append(variable_id)
            if not module_var_dict[module_type]:
                del module_var_dict[module_type]

        # get the time range and split it into chunks based on the "limit" and "scale"
        # parameters
        scale = _ts_params["scale"]
        limit = _ts_params["limit"]
        # use pop to remove the date_begin and date_end keys from the dict (they will be
        # added to each chunk's request)
        time_range = pd.date_range(
            pd.Timestamp(_ts_params.pop("date_begin")),
            pd.Timestamp(_ts_params.pop("date_end")),
            freq=SCALE_TO_FREQ_DICT[scale],
        )
        if len(time_range) >= limit:
            utils.log(
                f"The queried time range ({len(time_range)}) and scale ({scale}) exceed"
                f" the limit of measurements per request ({limit}). The requests will "
                f"be split into chunks of {limit} periods.",
                level=lg.INFO,
            )
        # times must be in Unix time
        time_range_chunks = [
            (chunk_range[0].timestamp(), chunk_range[-1].timestamp())
            for chunk_range in np.array_split(
                time_range, np.ceil(len(time_range) / limit)
            )
        ]

        # get the number of requests and warn (if needed) about API limits
        n_requests = sum(
            [
                len(self.stations_gdf[module_type].dropna()) * len(time_range_chunks)
                for module_type in module_var_dict
            ]
        )
        if n_requests > HOURLY_REQUESTS_LIMIT:
            utils.log(
                f"Number of requests ({n_requests}) exceeds the hourly limit "
                f"({HOURLY_REQUESTS_LIMIT}).",
                level=lg.WARNING,
            )
        ts_dfs = []

        def _process_response_chunk(response_chunk, module_vars):
            chunk_df = pd.DataFrame(response_chunk["value"], columns=module_vars)
            try:
                return chunk_df.assign(
                    **{
                        self._ts_df_time_col: pd.date_range(
                            start=pd.to_datetime(response_chunk["beg_time"], unit="s"),
                            periods=len(response_chunk["value"]),
                            freq=f"{response_chunk['step_time']}s",
                        ),
                    }
                )
            except KeyError:
                # assume that only one observation was returned, so there are only the
                # "beg_time" and "value" keys
                return chunk_df.assign(
                    time=pd.to_datetime(response_chunk["beg_time"], unit="s"),
                )

        n_nodata_modules = 0
        with tqdm(total=n_requests) as pbar:
            for module_type, module_vars in module_var_dict.items():
                _params = dict(type=",".join(module_vars)) | _ts_params
                for station_id, module_id in (
                    self.stations_gdf[module_type].dropna().items()
                ):
                    _params["device_id"] = station_id
                    _params["module_id"] = module_id
                    for start, end in time_range_chunks:
                        _params["date_begin"] = start
                        _params["date_end"] = end

                        response_json = self._get_content_from_url(
                            self._ts_endpoint,
                            params=_params,
                        )

                        try:
                            response_data = response_json["body"]
                            if response_data == []:
                                # TODO: is this logging level too verbose?
                                utils.log(
                                    f"The request for station {station_id} and module"
                                    f" {module_id} returned no data. This suggests "
                                    "that the module was not set up at the time of "
                                    "the requested date range.",
                                    level=lg.INFO,
                                )
                                n_nodata_modules += 1
                            else:
                                ts_dfs.append(
                                    pd.concat(
                                        [
                                            _process_response_chunk(
                                                response_chunk, module_vars
                                            )
                                            for response_chunk in response_data
                                        ],
                                        ignore_index=True,
                                    ).assign(
                                        **{self._ts_df_stations_id_col: station_id}
                                    )
                                )
                        except TypeError:
                            # print("typeerror", response_json)
                            # TODO: manage this error
                            pass
                        except IndexError:
                            # print("indexerror", response_json)
                            # TODO: manage this error
                            pass
                        # TODO: except TokenExpiredError
                        # from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
                        except KeyError:
                            if response_json["error"]["message"] == "Device not found":
                                # print(response_json["error"])
                                # TODO: manage this error
                                pass
                            else:
                                log_msg = (
                                    "API limit reached, returning records for"
                                    f" {len(ts_dfs)} modules"
                                )
                                if n_nodata_modules > 0:
                                    log_msg += (
                                        f" (plus {n_nodata_modules} modules with no "
                                        "records for the requested time range)."
                                    )
                                else:
                                    log_msg += "."
                                utils.log(
                                    log_msg,
                                    level=lg.WARNING,
                                )
                                if ts_dfs:
                                    # TODO: DRY with the return statement at the end of
                                    # the method
                                    return pd.concat(
                                        ts_dfs, ignore_index=True
                                    ).set_index(
                                        [
                                            self._ts_df_stations_id_col,
                                            self._ts_df_time_col,
                                        ]
                                    )
                                else:
                                    # return empty data frame
                                    # TODO: catch the subsequent KeyError in
                                    # `BaseClient._rename_variables_cols` and raise a
                                    # more informative message
                                    return pd.DataFrame()
                        pbar.update(1)

        if n_nodata_modules > 0:
            utils.log(
                "Number of modules with no records for the requested time range: "
                f"{n_nodata_modules} (out of {n_requests}).",
                level=lg.INFO,
            )

        return pd.concat(ts_dfs, ignore_index=True).set_index(
            [self._ts_df_stations_id_col, self._ts_df_time_col]
        )

    def get_ts_df(
        self,
        variables: VariablesType,
        start: DateTimeType,
        end: DateTimeType,
        *,
        scale: str | None = None,
        limit: int | None = None,
        real_time: bool | None = None,
    ) -> pd.DataFrame:
        """Get time series data frame.

        Parameters
        ----------
        variables : str, int or list-like of str or int
            Target variables, which can be either a Netatmo variable code (integer or
            string) or an essential climate variable (ECV) following the Meteora
            nomenclature (string).
        start, end : datetime-like, str, int, float
            Values representing the start and end of the requested data period
            respectively. Accepts any datetime-like object that can be passed to
            pandas.Timestamp.
        scale : {"30min", "1hour", "3hours", "1day", "1week", "1month"}, optional
            Temporal scale of the measurements. If None, returns the finest scale, i.e.,
            "30min" (30 minutes).
        limit : int, optional
            Maximum number of time steps to return. If None, the maximum number allowed
            by the Netatmo API (1024) is used.
        real_time : bool, optional
            A value of True returns the exact timestamps. Otherwise, when scale is
            different than the maximum, i.e., 30 minutes, timestamps are offset by half
            of the scale. If None, the default value of False is used (in line with the
            Netatmo API).

        Returns
        -------
        ts_df : pandas.DataFrame
            Long form data frame with a time series of measurements (second-level index)
            at each station (first-level index) for each variable (column).
        """
        return self._get_ts_df(
            variables=variables,
            start=start,
            end=end,
            scale=scale,
            limit=limit,
            optimize=True,  # avoid writing a parsers for each format
            real_time=real_time,
        )
