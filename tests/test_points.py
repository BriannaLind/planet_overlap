from shapely.geometry import Point
from planet_overlap.geometry import normalize_geometry

def test_point_buffer():
    pt = Point(0, 0)
    poly = normalize_geometry(pt, 0.01)
    assert poly.geom_type == "Polygon"
    assert poly.area > 0
