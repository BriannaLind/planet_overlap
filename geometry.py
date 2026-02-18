import logging
import geopandas as gpd
from shapely.geometry import shape, box
from shapely.ops import unary_union
from shapely.geometry.base import BaseGeometry
from typing import List


def normalize_geometry(geom: BaseGeometry, point_buffer_deg: float) -> BaseGeometry:
    """
    Convert Points/MultiPoints to buffered polygons.
    """

    if geom.geom_type in ["Point", "MultiPoint"]:
        logging.info(f"Buffering {geom.geom_type} to polygon")
        return geom.buffer(point_buffer_deg)

    if geom.geom_type in ["Polygon", "MultiPolygon"]:
        return geom

    raise ValueError(f"Unsupported geometry type: {geom.geom_type}")


def load_aois(aoi_files: List[str], point_buffer_deg: float = 0.001) -> List[BaseGeometry]:
    """
    Load AOIs from GeoJSON files and normalize geometries.
    """

    geometries = []

    for file in aoi_files:
        gdf = gpd.read_file(file)

        if gdf.empty:
            raise ValueError(f"AOI file {file} is empty.")

        for geom in gdf.geometry:
            geometries.append(normalize_geometry(geom, point_buffer_deg))

    logging.info(f"Loaded {len(geometries)} AOI geometries")
    return geometries


def generate_tiles(geometries: List[BaseGeometry], tile_size_deg: float):
    """
    Generate bounding box grid tiles over AOI union.
    """

    union_geom = unary_union(geometries)
    minx, miny, maxx, maxy = union_geom.bounds

    tiles = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            tiles.append(
                box(x, y,
                    min(x + tile_size_deg, maxx),
                    min(y + tile_size_deg, maxy))
            )
            y += tile_size_deg
        x += tile_size_deg

    logging.info(f"Generated {len(tiles)} tiles")
    return tiles
