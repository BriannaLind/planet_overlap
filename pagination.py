"""
pagination.py
Handles Planet API searches with automatic tiling (spatial & temporal), progress tracking,
and robust error handling. Integrates with filters.py to build dynamic filters.
"""

import os
import requests
import math
import time
from typing import List, Tuple, Dict, Any
from shapely.geometry import Polygon, box
from datetime import datetime, timedelta

from .filters import build_filters

# -------------------------
# Configuration thresholds
# -------------------------
SPATIAL_TILE_AREA_THRESHOLD_KM2 = 50000  # e.g., 50,000 km² (~size of Massachusetts)
TEMPORAL_TILE_DAYS_THRESHOLD = 30       # if date range > 30 days, apply temporal tiling
MAX_RETRIES = 5
RETRY_DELAY = 10  # seconds

# -------------------------
# Spatial tiling
# -------------------------
def tile_aoi(aoi: Polygon, tile_size_deg: float = 1.0) -> List[Polygon]:
    """
    Split AOI polygon into smaller tiles (default 1° x 1°) for large areas.

    Args:
        aoi (Polygon): Input AOI.
        tile_size_deg (float): Tile size in degrees (lat/lon).

    Returns:
        List[Polygon]: List of polygon tiles covering AOI.
    """
    minx, miny, maxx, maxy = aoi.bounds
    tiles = []

    x_steps = math.ceil((maxx - minx) / tile_size_deg)
    y_steps = math.ceil((maxy - miny) / tile_size_deg)

    for i in range(x_steps):
        for j in range(y_steps):
            tile = box(
                minx + i * tile_size_deg,
                miny + j * tile_size_deg,
                min(minx + (i + 1) * tile_size_deg, maxx),
                min(miny + (j + 1) * tile_size_deg, maxy)
            )
            # Only keep tiles that intersect AOI
            intersection = tile.intersection(aoi)
            if intersection.area > 0:
                tiles.append(intersection)
    return tiles


# -------------------------
# Temporal tiling
# -------------------------
def tile_dates(start: datetime, end: datetime, max_days: int = TEMPORAL_TILE_DAYS_THRESHOLD) -> List[Tuple[datetime, datetime]]:
    """
    Split date range into smaller slices if longer than max_days.

    Args:
        start (datetime): Start date.
        end (datetime): End date.
        max_days (int): Maximum number of days per slice.

    Returns:
        List[Tuple[datetime, datetime]]: List of date tuples.
    """
    total_days = (end - start).days + 1
    if total_days <= max_days:
        return [(start, end)]

    slices = []
    current_start = start
    while current_start <= end:
        current_end = min(current_start + timedelta(days=max_days - 1), end)
        slices.append((current_start, current_end))
        current_start = current_end + timedelta(days=1)
    return slices


# -------------------------
# Planet API pagination
# -------------------------
def fetch_planet_data(
    session: requests.Session,
    aois: List[Polygon],
    date_ranges: List[Tuple[datetime, datetime]],
    max_cloud: float = 0.5,
    min_sun_angle: float = 0.0,
    item_types: List[str] = ["PSScene4Band"],
    page_size: int = 250
) -> Tuple[List[str], List[Dict], List[Dict]]:
    """
    Fetch Planet imagery metadata with automatic tiling.

    Args:
        session (requests.Session): Authenticated Planet API session.
        aois (List[Polygon]): List of AOIs.
        date_ranges (List[Tuple[datetime, datetime]]): List of start/end date ranges.
        max_cloud (float): Maximum cloud fraction.
        min_sun_angle (float): Minimum sun elevation in degrees.
        item_types (List[str]): Planet item types to query.
        page_size (int): Results per page.

    Returns:
        Tuple[List[str], List[Dict], List[Dict]]: ids, geometries, properties
    """
    ids: List[str] = []
    geometries: List[Dict] = []
    properties: List[Dict] = []

    total_requests = len(aois) * len(date_ranges)
    request_count = 0

    for aoi in aois:
        # Apply spatial tiling if AOI area is large (> threshold)
        # Approximate area in km² (assuming 1° ~ 111 km)
        approx_area_km2 = (aoi.bounds[2] - aoi.bounds[0]) * (aoi.bounds[3] - aoi.bounds[1]) * 111 ** 2
        if approx_area_km2 > SPATIAL_TILE_AREA_THRESHOLD_KM2:
            tiles = tile_aoi(aoi)
        else:
            tiles = [aoi]

        for tile in tiles:
            for start, end in tile_dates(date_ranges[0][0], date_ranges[-1][1]):
                request_count += 1
                print(f"[{request_count}/{total_requests}] Requesting tile {tile.bounds} for {start.date()} to {end.date()}")

                filter_json = build_filters(
                    aois=[tile],
                    date_ranges=[(start, end)],
                    max_cloud=max_cloud,
                    min_sun_angle=min_sun_angle
                )

                search_request = {
                    "name": f"tile_{request_count}",
                    "item_types": item_types,
                    "filter": filter_json
                }

                # POST search
                try:
                    response = None
                    for attempt in range(MAX_RETRIES):
                        try:
                            response = session.post("https://api.planet.com/data/v1/searches/", json=search_request)
                            response.raise_for_status()
                            break
                        except requests.RequestException as e:
                            print(f"Retry {attempt+1}/{MAX_RETRIES} due to {e}")
                            time.sleep(RETRY_DELAY)
                    if response is None:
                        print(f"Failed request for tile {tile.bounds}, skipping.")
                        continue

                    search_id = response.json()["id"]
                    # Fetch paginated results
                    next_url = f"https://api.planet.com/data/v1/searches/{search_id}/results?_page_size={page_size}"
                    while next_url:
                        page = session.get(next_url).json()
                        ids += [f['id'] for f in page['features']]
                        geometries += [f['geometry'] for f in page['features']]
                        properties += [f['properties'] for f in page['features']]
                        next_url = page["_links"].get("_next")
                except Exception as e:
                    print(f"Error fetching data for tile {tile.bounds}: {e}")

    return ids, geometries, properties
