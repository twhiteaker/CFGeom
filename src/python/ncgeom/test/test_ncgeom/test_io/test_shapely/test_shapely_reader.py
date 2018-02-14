import pytest
from shapely import wkt
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import orient

from ncgeom import GeometryContainer
from ncgeom.test.base import AbstractNcgeomTest
from ncgeom.io.shapely_io.shapely_reader import shapely_to_container


class TestShapelyReader(AbstractNcgeomTest):
    def test_shapely_to_container(self):
        line = LineString([(0, 0), (1, 1)])
        container = shapely_to_container(line)
        self.assertEqual(container.geom_type, 'line')
        geom = container.geoms[0]
        self.assertEqual(geom.parts[0].x, [0, 1])


class TestPoint(AbstractNcgeomTest):
    def test_from_shapely_point_3d(self):
        geoms = [Point(1, 2, 10), Point(3, 4, 11), Point(5, 6, 12)]
        coll = shapely_to_container(geoms)
        self.assertEqual(len(coll.geoms), 3)
        self.assertIsNotNone(coll.geoms[0].parts[0].z)


class TestLineString(AbstractNcgeomTest):
    def test_from_shapely_linestring_2d_multipart(self):
        geom = wkt.loads(self.fixture_wkt['2d']['multilinestring'])
        coll = shapely_to_container(geom)
        self.assertEqual(len(coll.geoms), 1)
        self.assertEqual(len(coll.geoms[0].parts), 2)
        self.assertEqual(len(coll.geoms[0].parts[0].x), 3)


class TestPolygon(AbstractNcgeomTest):
    def test_from_shapely_polygon(self):
        for d in ['2d', '3d']:
            poly1 = wkt.loads(self.fixture_wkt[d]['polygon'])
            poly2 = wkt.loads(self.fixture_wkt[d]['polygon_hole'])

            geoms = [orient(poly1, sign=-1.0), poly2]
            res = shapely_to_container(geoms)
            self.assertIsInstance(res, GeometryContainer)

            for ctr, geom in enumerate(res.geoms):
                loaded = geom.to_shapely()
                self.assertTrue(loaded.almost_equals(geoms[ctr]))
