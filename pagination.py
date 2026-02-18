"""
pagination.py
Handles Planet API pagination with dynamic spatial/temporal tiling.
Automatically splits large AOIs or long date ranges into smaller requests.
"""

import math
import logging
import requests
from shapely.geometry import Polygon
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

# Thresholds for auto-tiling
MAX_AOI_DEG2 = 10.0        # Max AOI area in deg² before spatial tiling
MAX_DAYS = 30               # Max days before temporal tiling

def estimate_scene_count(aoi_area_deg2: float, days: int, density: float = 1.0) -> int:
    """
    Estimate number of scenes for a given AOI and date range.
    Args:
        aoi_area_deg2: AOI area in degrees²
        days: Number of days in query
        density: Scenes per deg² per day (default 1.0)
    Returns:
        Estimated scene count
    """
    return math.ceil(aoi_area_deg2 * days * density)


def should_tile(aoi_area_deg2: float, days: int) -> Tuple[bool, bool]:
    """
    Decide whether spatial or temporal tiling is required.
    Args:
        aoi_area_deg2: AOI area in deg²
        days: Number of days in query
    Returns:
        Tuple[bool, bool]: (spatial_tiling, temporal_tiling)
    """
    spatial = aoi_area_deg2 > MAX_AOI_DEG2
    temporal = days > MAX_DAYS
    return spatial, temporal


def paginate_search(session: requests.Session, search_url: str) -> List[Dict]:
    """
    Paginate through Planet API search results.
    Args:
        session: Authenticated requests.Session
        search_url: URL for the first search page
    Returns:
        List of results (dicts)
    """
    results: List[Dict] = []
    next_url = search_url
    page_num = 1

    while next_url:
        try:
            resp = session.get(next_url)
            resp.raise_for_status()
            page = resp.json()
        except requests.RequestException as e:
            logger.error(f"Request failed at page {page_num}: {e}")
            break

        features = page.get("features", [])
        logger.info(f"Fetched page {page_num} with {len(features)} features")
        results.extend(features)
        next_url = page.get("_links", {}).get("_next")
        page_num += 1

    return results
