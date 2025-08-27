"""access polygons describing New Zealand coastlines.
"""

import sys

if sys.version_info >= (3, 10):
    from importlib.resources import files
else:
    # importlib_resources provides functionality of standard library's
    # importlib.resources backported to older versions of python
    from importlib_resources import files
from typing import Tuple
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np

# EPSG:4326 - WGS 84, latitude/longitude coordinate system based on the Earth's
# center of mass, used by the Global Positioning System among others.
LATLON = "EPSG:4326"  # https://epsg.io/4326


def _geopackage_to_gpd_geodataframe(fname: str) -> gpd.GeoDataFrame:
    """return a geopandas GeoDataFrame containing the NZ coastline

    helper function for get_NZ_coastlines()
    """
    gdf = gpd.read_file(fname).to_crs(LATLON)
    return gdf


def _clip_to_bbox(
    gdf: gpd.GeoDataFrame, bbox: Tuple[float, float, float, float]
) -> gpd.GeoDataFrame:
    """clip a geopandas.geodataframe to a bounding box

    ARGS:
        gdf: the geopandas.GeoDataFrame to be clipped
        bbox: optional 4-tuple of floats specifying a bounding box. If
            specified, the coastlines will be clipped to the bounding box. The
            box is specified in form [LL lon, LL lat, UR lon, UR lat ]. LL =
            lower left, UR = upper right.

    RETURNS:
        gdf, clipped to the rectangle specified by bbox
    """
    bboxx = [bbox[0], bbox[2]]
    bboxy = [bbox[1], bbox[3]]
    bbox = Polygon(
        [
            (bboxx[0], bboxy[0]),
            (bboxx[0], bboxy[1]),
            (bboxx[1], bboxy[1]),
            (bboxx[1], bboxy[0]),
            (bboxx[0], bboxy[0]),
        ]
    )
    gdf_bbox = gpd.GeoDataFrame({"geometry": [bbox]}, crs=LATLON)
    gdf_cropped = gpd.clip(gdf, gdf_bbox)
    return gdf_cropped


def get_NZ_coastlines(
    include_chatham_islands: bool = False,
    include_kermadec_islands: bool = False,
    bbox: Tuple[float, float, float, float] = (None, None, None, None),
) -> gpd.GeoDataFrame:
    """return a geopandas.GeoDataFrame containing the NZ coastline.

    The reasoning behind the options to exclude the Chatham Islands and Kermadec
    islands: The `Chatham Islands
    <https://en.wikipedia.org/wiki/Chatham_Islands>`_ and the `Kermadec Islands
    <https://en.wikipedia.org/wiki/Kermadec_Islands>`_ sit east of 180 degrees E
    longitude. When plotting the full contents of the New Zealand coastlines
    dataset some plotting packages' default options (e.g. matplotlib) produce a
    horizontal axis spanning the full range of longitudes in the dataset:
    roughly -177 deg E to 177 deg E. This produces a plot with the Chathams and
    Kermadecs as a small spec at 177 deg E on the far right and the rest of New
    Zealand as a marginally larger spec at -177 deg E on the far left, and blank
    space everywhere else. The default options to :py:func:`get_NZ_coastlines`
    allow plotting the North and South Islands of New Zealand in a more useful
    way using default plotting options.

    ARGS:
        include_chatham_islands: if true, include the coastline of the Chatham
            Islands in the returned geodataframe.
        include_kermadec_islands: if true, include the coastline of the Kermadec
            Islands in the returned geodataframe.
        bbox: optional 4-tuple of floats specifying a bounding box. If
            specified, the coastlines will be clipped to the bounding box. The
            box is specified in form [LL lon, LL lat, UR lon, UR lat ]. LL =
            lower left, UR = upper right.

    RETURNS:
        a `geopandas.GeoDataFrame
        <https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe>`_
        object containing multipolygons representing New Zealand's coastlines.

    """
    fname = files("nzgeom.data").joinpath(
        "coastlines/nz-coastlines-and-islands-polygons-topo-150k.gpkg"
    )
    gdf = _geopackage_to_gpd_geodataframe(fname)
    if not include_kermadec_islands:
        # testing for "!= True" (rather than "== False") gets both False
        # (grp_name does not contain Kermadec) and None (grp_name was not set at
        # all)
        gdf = gdf.loc[gdf["grp_name"].str.contains("Kermadec") != True]
    if not include_chatham_islands:
        gdf = gdf.loc[gdf["grp_name"].str.contains("Chatham") != True]
    if np.all([val is not None for val in bbox]):
        print(f"clipping to bounding box {bbox}")
        gdf = _clip_to_bbox(gdf, bbox)
    return gdf
