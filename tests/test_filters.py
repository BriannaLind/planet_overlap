import pytest
from datetime import datetime
from planet_overlap.filters import build_filters

def test_single_geojson_and_date():
    geojson_path = "tests/data/sample_aoi.geojson"
    start_date = "2023-01-01"
    end_date = "2023-01-01"
    filters = build_filters([geojson_path], [start_date])
    assert "GeometryFilter" in str(filters)
    assert "DateRangeFilter" in str(filters)

def test_multiple_geojson_and_date_ranges():
    geojson_paths = ["tests/data/sample_aoi.geojson", "tests/data/sample_aoi2.geojson"]
    start_dates = ["2023-01-01", "2023-02-01"]
    end_dates = ["2023-01-15", "2023-02-10"]
    filters = build_filters(geojson_paths, list(zip(start_dates, end_dates)))
    assert len(filters['config']) == 2
