import pytest
from shapely import wkt
from shapely.geometry import Point, MultiPoint, LineString

from ..... import GeometryContainer, Geometry, Part
from ..... convert.shapely_io.shapely_writer import geom_to_shapely
from .... base import AbstractNcgeomTest


class TestShapelyWriter(AbstractNcgeomTest):
    def test_to_shapely(self):
        x = [10, 5, 0]
        y = [0, 5, 0]
        line = Geometry('line', Part(x, y))
        shp = geom_to_shapely(line)
        self.assertEqual(list(shp.coords), [(10, 0), (5, 5), (0, 0)])
        self.assertEqual(shp.geom_type, 'LineString')


class TestPoint(AbstractNcgeomTest):
    def test_to_shapely_point_2d(self):
        geom = Geometry('point', Part([30], [10]))

        pt = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['2d']['point'])
        self.assertEqual(pt, desired)

        # Test this will be converted to a multipart if requested.
        mpt = geom.to_shapely('MultiPoint')
        self.assertIsInstance(mpt, MultiPoint)


    def test_to_shapely_point_3d(self):
        geom = Geometry('point', Part([30], [10], [100]))

        pt = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['3d']['point'])
        self.assertEqual(pt, desired)


    def test_to_shapely_point_2d_multipart(self):
        parts = [Part(10, 40),
                 Part(40, 30),
                 Part(20, 20),
                 Part(30, 10)]
        geom = Geometry('point', parts)

        mpt = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['2d']['multipoint'])
        self.assertEqual(mpt, desired)


    def test_to_shapely_point_3d_multipart(self):
        parts = [Part(10, 40, 100),
                 Part(40, 30, 200),
                 Part(20, 20, 300),
                 Part(30, 10, 400)]
        geom = Geometry('point', parts)

        mpt = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['3d']['multipoint'])
        self.assertEqual(mpt, desired)


class TestLineString(AbstractNcgeomTest):
    def test_to_shapely_linestring_2d(self):
        parts = [Part([30, 10, 40], [10, 30, 40])]
        geom = Geometry('line', parts)

        ls = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['2d']['linestring'])
        self.assertEqual(ls, desired)

    def test_to_shapely_linestring_3d(self):
        parts = [Part([30, 10, 40], [10, 30, 40], [100, 200, 300])]
        geom = Geometry('line', parts)

        ls = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['3d']['linestring'])
        self.assertEqual(ls, desired)

    def test_to_shapely_linestring_2d_multipart(self):
        parts = [Part([10, 20, 10], [10, 20, 40]),
                 Part([40, 30, 40, 30], [40, 30, 20, 10])]
        geom = Geometry('line', parts)

        mls = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['2d']['multilinestring'])
        self.assertEqual(mls, desired)

    def test_to_shapely_linestring_3d_multipart(self):
        parts = [Part([10, 20, 10], [10, 20, 40], [100, 200, 300]),
                 Part([40, 30, 40, 30], [40, 30, 20, 10], [100, 200, 300, 400])]
        geom = Geometry('line', parts)

        mls = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['3d']['multilinestring'])
        self.assertEqual(mls, desired)


class TestPolygon(AbstractNcgeomTest):
    def test_to_shapely_polygon_2d(self):
        parts = [Part([30, 40, 20, 10], [10, 40, 40, 20])]
        geom = Geometry('polygon', parts)

        p = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['2d']['polygon'])
        self.assertEqual(p, desired)


    def test_to_shapely_polygon_2d_hole(self):
        parts = [Part([35, 45, 15, 10], [10, 45, 40, 20]),
                 Part([20, 35, 30, 20], [30, 35, 20, 30], is_hole=True)]
        geom = Geometry('polygon', parts)

        p = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['2d']['polygon_hole'])
        self.assertEqual(p, desired)


    def test_to_shapely_polygon_2d_multipart_hole(self):
        parts = [Part([40, 20, 45], [40, 45, 30]),
                 Part([20, 10, 10, 30, 45], [35, 30, 10, 5, 20]),
                 Part([30, 20, 20], [20, 15, 25], is_hole=True)]
        geom = Geometry('polygon', parts)

        p = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['2d']['multipolygon_hole'])
        self.assertEqual(p, desired)


    def test_to_shapely_polygon_2d_multipart_holes(self):
        parts = [Part([0, 20, 20, 0], [0, 0, 20, 20]),
                 Part([1, 10, 19], [1, 5, 1], is_hole=True),
                 Part([5, 7, 9], [15, 19, 15], is_hole=True),
                 Part([11, 13, 15], [15, 19, 15], is_hole=True),
                 Part([5, 9, 7], [25, 25, 29]),
                 Part([11, 15, 13], [25, 25, 29])]
        geom = Geometry('polygon', parts)

        p = geom.to_shapely()
        desired = wkt.loads(self.fixture_wkt['2d']['multipolygons_holes'])
        self.assertEqual(p, desired)
