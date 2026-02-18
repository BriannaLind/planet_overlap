from datetime import datetime, timedelta
from shapely.geometry import Polygon, Point
from typing import List, Tuple, Union

# Thresholds
POLYGON_AREA_THRESHOLD_KM2 = 2500  # AOI > 2500 km² triggers spatial tiling
DATE_RANGE_THRESHOLD_DAYS = 30     # Polygons: split if range >30 days
POINT_DATE_THRESHOLD_DAYS = 3 * 365  # Points: split if range >3 years (~1095 days)
MAX_SCENES_PER_REQUEST = 500       # Max scenes per slice

def estimate_scene_count(days: int, avg_scenes_per_day: float = 1.0) -> int:
    """Estimate the number of scenes for a given number of days."""
    return int(days * avg_scenes_per_day)

def tile_dates(start: datetime, end: datetime, is_point: bool = False) -> List[Tuple[datetime, datetime]]:
    """
    Break a date range into smaller slices if it exceeds thresholds.

    Args:
        start: start datetime
        end: end datetime
        is_point: True if the input is a point, False for polygons/AOIs

    Returns:
        List of (start, end) tuples
    """
    total_days = (end - start).days + 1
    slices = []

    # Determine threshold
    threshold_days = POINT_DATE_THRESHOLD_DAYS if is_point else DATE_RANGE_THRESHOLD_DAYS
    if total_days <= threshold_days:
        return [(start, end)]

    # Split into slices
    slice_length = min(threshold_days, total_days)
    current_start = start
    while current_start <= end:
        current_end = min(current_start + timedelta(days=slice_length - 1), end)
        slices.append((current_start, current_end))
        current_start = current_end + timedelta(days=1)
    return slices

def tile_aoi(geom: Union[Polygon, Point]) -> List[Polygon]:
    """
    Split a polygon into ~1°x1° tiles if AOI is large.
    Points are returned as buffered polygons automatically.

    Args:
        geom: AOI polygon or point

    Returns:
        List of Polygons for API requests
    """
    if isinstance(geom, Point):
        # buffer a small area around the point (~0.01 degrees)
        return [geom.buffer(0.01)]

    # Check area (approximation using degrees -> km²)
    lon_min, lat_min, lon_max, lat_max = geom.bounds
    area_km2 = (lon_max - lon_min) * (lat_max - lat_min) * 111**2
    if area_km2 <= POLYGON_AREA_THRESHOLD_KM2:
        return [geom]

    # Split polygon into 1°x1° tiles
    tiles = []
    lat = lat_min
    while lat < lat_max:
        lon = lon_min
        while lon < lon_max:
            tile = Polygon([
                (lon, lat),
                (min(lon+1, lon_max), lat),
                (min(lon+1, lon_max), min(lat+1, lat_max)),
                (lon, min(lat+1, lat_max))
            ])
            tiles.append(tile.intersection(geom))
            lon += 1
        lat += 1
    return tiles

def fetch_planet_data(session, aois: List[Union[Polygon, Point]],
                      date_ranges: List[Tuple[datetime, datetime]],
                      max_cloud: float = 0.5,
                      min_sun_angle: float = 0.0):
    """
    Main entry point to fetch Planet data, automatically tiling AOIs or temporal ranges
    when thresholds are exceeded.

    Returns:
        ids, geometries, properties
    """
    ids, geometries, properties = [], [], []

    for geom in aois:
        is_point = isinstance(geom, Point)
        aoi_tiles = tile_aoi(geom)

        for tile in aoi_tiles:
            for start, end in date_ranges:
                date_slices = tile_dates(start, end, is_point=is_point)

                for s_start, s_end in date_slices:
                    # Call the Planet API here (simplified)
                    # response = session.get(..., params={geom: tile, dates: s_start->s_end})
                    # Extract ids, geometries, properties
                    # For demonstration, we'll append mock data
                    ids.append(f"scene_{s_start.strftime('%Y%m%d')}")
                    geometries.append(tile.__geo_interface__)
                    properties.append({'cloud_cover': max_cloud, 'sun_angle': min_sun_angle})

    return ids, geometries, properties
