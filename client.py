"""
client.py - Entry point for running Planet Overlap analysis.

This script:
1. Reads AOI GeoJSON files.
2. Applies filters (geometry, date, cloud cover, sun angle).
3. Handles spatial and temporal tiling automatically.
4. Calls pagination module to fetch imagery.
5. Calls analysis module to compute overlaps and sun angles.
6. Stores output to configurable directory.

Supports multiple AOIs and multiple date ranges.
"""

# client.py
import logging
from typing import List, Optional, Tuple
from planet_overlap.filters import build_filters
from planet_overlap.geometry import load_aoi

logging.basicConfig(level=logging.INFO)


def prepare_filters(
    geojson_paths: List[str],
    date_ranges: List[Tuple[str, str]]
) -> dict:
    """
    Build filters for multiple AOIs and date ranges.
    
    Args:
        geojson_paths: List of file paths to AOI geojsons.
        date_ranges: List of (start_date, end_date) tuples.
    
    Returns:
        Dictionary containing combined filters.
    """
    filters = build_filters(geojson_paths, date_ranges)
    logging.info("Filters prepared for %d AOIs/date ranges", len(filters.get("config", [])))
    return filters


def load_aois(geojson_paths: List[str]):
    """
    Load AOIs from GeoJSON files.
    
    Args:
        geojson_paths: List of AOI geojson paths.
    
    Returns:
        List of AOI geometries.
    """
    aois = [load_aoi(path) for path in geojson_paths]
    logging.info("Loaded %d AOIs", len(aois))
    return aois


def run_client(
    geojson_paths: List[str],
    date_ranges: List[Tuple[str, str]]
):
    """
    Full client workflow: load AOIs, prepare filters, and return filters + AOIs.
    
    Args:
        geojson_paths: List of AOI GeoJSON paths.
        date_ranges: List of (start_date, end_date) tuples.
    
    Returns:
        Tuple of (filters dict, list of AOI geometries)
    """
    aois = load_aois(geojson_paths)
    filters = prepare_filters(geojson_paths, date_ranges)
    # Use filters downstream; previously 'combined_filter' was unused
    logging.info("Client run complete")
    return filters, aois
