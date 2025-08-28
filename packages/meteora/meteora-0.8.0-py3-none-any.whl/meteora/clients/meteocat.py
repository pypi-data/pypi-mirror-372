"""Meteocat client."""

from collections.abc import Mapping

import pandas as pd
import pyproj

from meteora import settings
from meteora.clients.base import BaseJSONClient
from meteora.mixins import (
    APIKeyHeaderMixin,
    StationsEndpointMixin,
    VariablesEndpointMixin,
)
from meteora.utils import DateTimeType, KwargsType, RegionType, VariablesType

# API endpoints
BASE_URL = "https://api.meteo.cat/xema/v1"
STATIONS_ENDPOINT = f"{BASE_URL}/estacions/metadades"
VARIABLES_ENDPOINT = f"{BASE_URL}/variables/mesurades/metadades"
TS_ENDPOINT = f"{BASE_URL}/variables/mesurades"

# useful constants
STATIONS_GDF_ID_COL = "codi"
TS_DF_STATIONS_ID_COL = "codi"
TS_DF_TIME_COL = "data"
# VARIABLES_NAME_COL = "nom"
VARIABLES_ID_COL = "codi"
ECV_DICT = {
    # precipitation
    "precipitation": 35,  # "Precipitació",
    # pressure
    "pressure": 34,  # "Pressió atmosfèrica",
    # radiation budget
    "radiation_shortwave": 39,  # "Radiació UV",
    # temperature
    "temperature": 32,  # "Temperatura",
    # water vapour
    "relative_humidity": 33,  # "Humitat relativa",
    # wind
    "wind_speed": 46,  # "Velocitat del vent a 2 m (esc.)",
    "wind_direction": 47,  # "Direcció de vent 2 m (m. 1)",
}


class MeteocatClient(
    APIKeyHeaderMixin,
    StationsEndpointMixin,
    VariablesEndpointMixin,
    BaseJSONClient,
):
    """Meteocat client.

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
    api_key : str
        Meteocat API key.
    sjoin_kwargs : dict, optional
        Keyword arguments to pass to the `geopandas.sjoin` function when filtering the
        stations within the region. If None, the value from `settings.SJOIN_KWARGS` is
        used.
    """

    # geom constants
    X_COL = "coordenades.longitud"
    Y_COL = "coordenades.latitud"
    CRS = pyproj.CRS("epsg:4326")

    # API endpoints
    _stations_endpoint = STATIONS_ENDPOINT
    _variables_endpoint = VARIABLES_ENDPOINT
    _ts_endpoint = TS_ENDPOINT

    # data frame labels constants
    _stations_gdf_id_col = STATIONS_GDF_ID_COL
    _ts_df_stations_id_col = TS_DF_STATIONS_ID_COL
    _ts_df_time_col = TS_DF_TIME_COL
    # _variables_name_col = VARIABLES_NAME_COL
    _variables_id_col = VARIABLES_ID_COL
    _ecv_dict = ECV_DICT

    def __init__(
        self, region: RegionType, api_key: str, **sjoin_kwargs: KwargsType
    ) -> None:
        """Initialize Meteocat client."""
        self.region = region
        self._api_key = api_key
        if sjoin_kwargs is None:
            sjoin_kwargs = settings.SJOIN_KWARGS.copy()
        self.SJOIN_KWARGS = sjoin_kwargs

        # need to call super().__init__() to set the cache
        super().__init__()

    def _stations_df_from_content(self, response_content: Mapping) -> pd.DataFrame:
        return pd.json_normalize(response_content)

    def _variables_df_from_content(self, response_content: Mapping) -> pd.DataFrame:
        return pd.json_normalize(response_content)

    def _ts_df_from_content(self, response_content: Mapping):
        # process response
        response_df = pd.json_normalize(response_content)
        # filter stations
        response_df = response_df[response_df["codi"].isin(self.stations_gdf.index)]
        # extract json observed data, i.e.,  the "variables" column into a list of data
        # frames and concatenate them into a single data frame
        ts_df = pd.concat(
            response_df.apply(
                lambda row: pd.DataFrame(row["variables"][0]["lectures"]), axis=1
            ).tolist()
        )
        # add the station id column matching the observations
        ts_df[self._ts_df_stations_id_col] = (
            response_df[self._ts_df_stations_id_col]
            .repeat(
                response_df.apply(
                    lambda row: len(row["variables"][0]["lectures"]), axis=1
                )
            )
            .values
        )
        # TODO: values_col as class-level constant?
        values_col = "valor"
        # # convert to a wide data frame
        # ts_df = long_df.pivot_table(
        #     index=self._time_col, columns=self._stations_id_col, values=values_col
        # )
        # # set the index name
        # ts_df.index.name = settings.TIME_NAME
        # # convert the index from string to datetime
        # ts_df.index = pd.to_datetime(ts_df.index)
        # ACHTUNG: do not sort the index here
        # note that we are renaming a series
        return ts_df.assign(
            **{self._ts_df_time_col: pd.to_datetime(ts_df[self._ts_df_time_col])}
        ).set_index([self._ts_df_stations_id_col, self._ts_df_time_col])[values_col]

    # def _get_date_ts_df(
    #     self,
    #     variable_id: int,
    #     date: datetime.date,
    # ) -> pd.DataFrame:
    #     """Get time series data frame for a given day.

    #     Parameters
    #     ----------
    #     variable_id : int
    #         Meteocat variable code.
    #     date : datetime.date
    #         datetime.date instance for the requested data period.

    #     Returns
    #     -------
    #     ts_df : pd.DataFrame
    #         Data frame with a time series of measurements (rows) at each station
    #         (columns).

    #     """
    #     # # process date arg
    #     # if isinstance(date, str):
    #     #     date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    #     # request url
    #     request_url = (
    #         f"{self._ts_endpoint}"
    #         f"/{variable_id}/{date.year}/{date.month:02}/{date.day:02}"
    #     )
    #     response_content = self._get_content_from_url(request_url)
    #     return self._ts_df_from_content(response_content).rename(variable_id)

    def _ts_df_from_endpoint(self, ts_params: Mapping) -> pd.DataFrame:
        # the API only allows returning data for a given day and variable so we have to
        # iterate over the date range and variables to obtain data for all days
        date_range = pd.date_range(
            start=ts_params["start"], end=ts_params["end"], freq="D"
        )
        return pd.concat(
            [
                pd.concat(
                    [
                        # self._get_date_ts_df(variable_id, date)
                        self._ts_df_from_content(
                            self._get_content_from_url(
                                f"{self._ts_endpoint}/{variable_id}/"
                                f"{date.year}/{date.month:02}/{date.day:02}"
                            )
                        ).rename(variable_id)
                        for variable_id in ts_params["variable_ids"]
                    ],
                    axis="columns",
                    ignore_index=False,
                )
                for date in date_range
            ],
            axis="index",
            ignore_index=False,
        )

    def get_ts_df(
        self,
        variables: VariablesType,
        start: DateTimeType,
        end: DateTimeType,
    ) -> pd.DataFrame:
        """Get time series data frame.

        Parameters
        ----------
        variables : str, int or list-like of str or int
            Target variables, which can be either a Meteocat variable code (integer or
            string) or an essential climate variable (ECV) following the Meteora
            nomenclature (string).
        start, end : datetime-like, str, int, float
            Values representing the start and end of the requested data period
            respectively. Accepts any datetime-like object that can be passed to
            pandas.Timestamp.

        Returns
        -------
        ts_df : pandas.DataFrame
            Long form data frame with a time series of measurements (second-level index)
            at each station (first-level index) for each variable (column).
        """
        ts_df = self._get_ts_df(
            variables,
            start=start,
            end=end,
        )
        # filter time range to avoid including a full day after
        # TODO: dry with Agrometeo, perhaps a global approach in the base client
        time_ser = ts_df.index.get_level_values(settings.TIME_COL).to_series()
        tz = time_ser.dt.tz
        return ts_df.loc[
            (
                slice(None),
                time_ser.between(
                    pd.Timestamp(start, tz=tz),
                    pd.Timestamp(end, tz=tz),
                    inclusive="both",
                ),
            ),
            :,
        ]
