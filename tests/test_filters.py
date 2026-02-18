# tests/test_filters.py
from planet_overlap.filters import build_filters


def test_single_geojson_and_single_date():
    """Test a single AOI with a single date."""
    geojson_path = "tests/data/sample_aoi.geojson"
    start_date = "2023-01-01"
    end_date = "2023-01-01"
    filters = build_filters([geojson_path], [(start_date, end_date)])
    assert "GeometryFilter" in str(filters)
    assert "DateRangeFilter" in str(filters)


def test_multiple_geojson_and_multiple_date_ranges():
    """Test multiple AOIs with multiple date ranges."""
    geojson_paths = [
        "tests/data/sample_aoi.geojson",
        "tests/data/sample_aoi2.geojson"
    ]
    date_ranges = [
        ("2023-01-01", "2023-01-15"),
        ("2023-02-01", "2023-02-10")
    ]
    filters = build_filters(geojson_paths, date_ranges)
    # Ensure each AOI/date pair generates a config entry
    assert len(filters["config"]) == 2
    for entry in filters["config"]:
        assert "GeometryFilter" in str(entry)
        assert "DateRangeFilter" in str(entry)


def test_mixed_single_and_range_dates():
    """Test handling of a mix of single dates and date ranges."""
    geojson_paths = [
        "tests/data/sample_aoi.geojson",
        "tests/data/sample_aoi2.geojson"
    ]
    date_ranges = [
        ("2023-01-01", "2023-01-01"),  # single date as range
        ("2023-02-01", "2023-02-10")
    ]
    filters = build_filters(geojson_paths, date_ranges)
    assert len(filters["config"]) == 2
    for entry in filters["config"]:
        assert "GeometryFilter" in str(entry)
        assert "DateRangeFilter" in str(entry)
