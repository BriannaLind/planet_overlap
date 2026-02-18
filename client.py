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

import os
import logging
from typing import List, Optional

from planet_overlap import filters, pagination, analysis, geometry

# Configure logging for progress tracking
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_client(
    aoi_files: List[str],
    start_dates: List[str],
    end_dates: List[str],
    output_dir: str = "./outputs",
    cloud_max: float = 0.5,
    min_sun_angle: float = 0.0,
    spatial_tile_threshold_km2: float = 10000,
    temporal_tile_threshold_days: int = 30
) -> None:
    """
    Main function to execute Planet Overlap workflow.

    Parameters
    ----------
    aoi_files : List[str]
        Paths to one or more AOI GeoJSON files.
    start_dates : List[str]
        Start dates corresponding to each AOI (format 'YYYY-MM-DD').
    end_dates : List[str]
        End dates corresponding to each AOI (format 'YYYY-MM-DD').
    output_dir : str
        Directory where output files will be saved.
    cloud_max : float
        Maximum cloud cover allowed (0-1).
    min_sun_angle : float
        Minimum sun angle allowed in degrees.
    spatial_tile_threshold_km2 : float
        Max AOI area before spatial tiling is applied.
    temporal_tile_threshold_days : int
        Max date range before temporal tiling is applied.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")

    # Read and buffer AOIs
    logging.info("Reading AOIs...")
    aois = []
    for file in aoi_files:
        try:
            aoi_geom = geometry.read_geojson(file)
            buffered_aoi = geometry.buffer_points(aoi_geom)
            aois.append(buffered_aoi)
        except Exception as e:
            logging.error(f"Failed to read or buffer AOI {file}: {e}")
            continue

    # Loop through each AOI and date range
    for i, aoi in enumerate(aois):
        start = start_dates[i]
        end = end_dates[i]

        logging.info(f"Processing AOI {i+1}/{len(aois)}: {file}, {start} to {end}")

        # Build filters
        geo_filter = filters.geometry_filter(aoi)
        date_filter = filters.date_filter(start, end)
        cloud_filter = filters.cloud_filter(cloud_max)
        sun_filter = filters.sun_angle_filter(min_sun_angle)

        combined_filter = filters.combine_filters(
            [geo_filter, date_filter, cloud_filter, sun_filter]
        )

        # Determine if tiling is needed
        area_km2 = geometry.compute_area_km2(aoi)
        date_range_days = filters.compute_date_range_days(start, end)

        spatial_tiles = [aoi]
        temporal_tiles = [(start, end)]

        if area_km2 > spatial_tile_threshold_km2:
            spatial_tiles = geometry.spatial_tile(aoi)
            logging.info(f"AOI exceeds {spatial_tile_threshold_km2} km², applying spatial tiling: {len(spatial_tiles)} tiles")

        if date_range_days > temporal_tile_threshold_days:
            temporal_tiles = filters.temporal_tile(start, end)
            logging.info(f"Date range exceeds {temporal_tile_threshold_days} days, applying temporal tiling: {len(temporal_tiles)} intervals")

        # Fetch imagery and analyze for each tile
        for s_tile in spatial_tiles:
            for t_start, t_end in temporal_tiles:
                logging.info(f"Fetching imagery for tile and date range: {t_start} to {t_end}")
                try:
                    items = pagination.fetch_items(
                        geometry=s_tile,
                        start_date=t_start,
                        end_date=t_end,
                        cloud_max=cloud_max
                    )
                    analysis_results = analysis.compute_overlap(items, min_sun_angle)
                    analysis.save_results(analysis_results, output_dir)
                    logging.info(f"Saved results for tile ({t_start}-{t_end})")
                except Exception as e:
                    logging.error(f"Failed processing tile/date {t_start}-{t_end}: {e}")
                    continue

    logging.info("Planet Overlap workflow completed successfully.")
