"""Region mixins."""

import geopandas as gpd
from pyogrio.errors import DataSourceError
from shapely import geometry
from shapely.geometry.base import BaseGeometry

from meteora.utils import CRSType, KwargsType, RegionType

try:
    import osmnx as ox
except ImportError:
    ox = None


class RegionMixin:
    """Mixin class to add a `region` attribute to a class."""

    @property
    def region(self) -> gpd.GeoDataFrame | None:
        """The region as a GeoDataFrame."""
        return self._region

    @region.setter
    def region(
        self,
        region: RegionType,
    ):
        self._region = self._process_region_arg(region, crs=getattr(self, "CRS", None))

    def _process_region_arg(
        self,
        region: RegionType,
        *,
        crs: CRSType | None = None,
        **geocode_to_gdf_kwargs: KwargsType,
    ) -> gpd.GeoDataFrame | None:
        """Process the region argument.

        Parameters
        ----------
        region : str, Sequence, GeoSeries, GeoDataFrame, PathLike, or IO
            The region to process. This can be either:
            -  A string with a place name (Nominatim query) to geocode.
            -  A sequence with the west, south, east and north bounds.
            -  A geometric object, e.g., shapely geometry, or a sequence of geometric
               objects. In such a case, the value is passed as the `data` argument of
               the GeoSeries constructor, and needs to be in the same CRS as the one
               used by the client's class (i.e., the `CRS` class attribute).
            -  A geopandas geo-series or geo-data frame.
            -  A filename or URL, a file-like object opened in binary ('rb') mode, or a
               Path object that will be passed to `geopandas.read_file`.
        crs : str, dict or pyproj.CRS, optional
            The coordinate reference system (CRS) of the provided region. It can be any
            CRS-like object accepted by geopandas. Ignored if `region` is a string
            corresponding to a place name, a geopandas geo-series or geo-data frame with
            its CRS attribute set or a filename, URL or file-like object.
        geocode_to_gdf_kwargs : dict, optional
            Keyword arguments to pass to `geocode_to_gdf` if `region` is a string
            corresponding to a place name (Nominatim query).

        Returns
        -------
        gdf : GeoDataFrame
            The processed region as a GeoDataFrame, in the CRS used by the client's
            class. A value of None is returned when passing a place name (Nominatim
            query) but osmnx is not installed.
        """
        # crs : Any, optional
        # Coordinate Reference System of the provided `region`. Ignored if `region` is a
        # string corresponding to a place name, a geopandas geo-series or geo-data frame
        # with its CRS attribute set or a filename, URL or file-like object. Can be
        # anything accepted by `pyproj.CRS.from_user_input()`, such as an authority
        # string (eg “EPSG:4326”) or a WKT string.

        if not isinstance(region, gpd.GeoDataFrame):
            # naive geometries
            if not isinstance(region, gpd.GeoSeries) and (
                hasattr(region, "__iter__")
                and not isinstance(region, str)
                or isinstance(region, BaseGeometry)
            ):
                # if region is a sequence (other than a string)
                # use the hasattr to avoid AttributeError when region is a BaseGeometry
                if hasattr(region, "__len__"):
                    if len(region) == 4 and isinstance(region[0], (int, float)):
                        # if region is a sequence of 4 numbers, assume it's a bounding
                        # box
                        region = geometry.box(*region)
                # otherwise, assume it's a geometry or sequence of geometries that can
                # be passed as the `data` argument of the GeoSeries constructor
                region = gpd.GeoSeries(region, crs=self.CRS)
            if isinstance(region, gpd.GeoSeries):
                # if we have a GeoSeries, convert it to a GeoDataFrame so that we can
                # use the same code
                region = gpd.GeoDataFrame(
                    geometry=region, crs=getattr(region, "crs", self.CRS)
                )
            else:
                # at this point, we assume that this is either file-like or a Nominatim
                # query
                try:
                    region = gpd.read_file(region)
                except (DataSourceError, AttributeError):
                    #             if ox is None:
                    #                 lg.warning(
                    #                     """
                    # Using a Nominatim query as `region` argument requires osmnx.
                    # You can install it using conda or pip.
                    # """
                    #                 )
                    #                 return

                    if geocode_to_gdf_kwargs is None:
                        geocode_to_gdf_kwargs = {}
                    region = ox.geocode_to_gdf(region, **geocode_to_gdf_kwargs).iloc[:1]

        return region.to_crs(self.CRS)
