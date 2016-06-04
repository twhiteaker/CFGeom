from shapely import wkt

from ncsg import cf
from ncsg.constants import NCSG_MULTIPART_BREAK_VALUE, NCSG_HOLE_BREAK_VALUE
from ncsg.test.base import AbstractNCSGTest


class TestPoint(AbstractNCSGTest):
    def test_loads_point_2d(self):
        cindex = [1]
        x = [30]
        y = [10]

        pt = cf.loads(cindex, x, y, start_index=1)
        desired = wkt.loads(self.fixture_wkt['2d']['point'])
        self.assertEqual(pt, desired)

    def test_loads_point_3d(self):
        cindex = [0]
        x = [30]
        y = [10]
        z = [100]

        pt = cf.loads(cindex, x, y, z=z)
        desired = wkt.loads(self.fixture_wkt['3d']['point'])
        self.assertEqual(pt, desired)

    def test_loads_point_2d_multipart(self):
        cindex = [0, NCSG_MULTIPART_BREAK_VALUE, 1, NCSG_MULTIPART_BREAK_VALUE, 2, NCSG_MULTIPART_BREAK_VALUE, 3]
        x = [10, 40, 20, 30]
        y = [40, 30, 20, 10]

        mpt = cf.loads(cindex, x, y)
        desired = wkt.loads(self.fixture_wkt['2d']['multipoint'])
        self.assertEqual(mpt, desired)

    def test_loads_point_3d_multipart(self):
        cindex = [0, NCSG_MULTIPART_BREAK_VALUE, 1, NCSG_MULTIPART_BREAK_VALUE, 2, NCSG_MULTIPART_BREAK_VALUE, 3]
        x = [10, 40, 20, 30]
        y = [40, 30, 20, 10]
        z = [100, 200, 300, 400]

        mpt = cf.loads(cindex, x, y, z=z)
        desired = wkt.loads(self.fixture_wkt['3d']['multipoint'])
        self.assertEqual(mpt, desired)


class TestLineString(AbstractNCSGTest):
    def test_loads_linestring_2d(self):
        cindex = [0, 1, 2]
        x = [30, 10, 40]
        y = [10, 30, 40]

        ls = cf.loads(cindex, x, y, geom_type='LineString')
        desired = wkt.loads(self.fixture_wkt['2d']['linestring'])
        self.assertEqual(ls, desired)

    def test_loads_linestring_3d(self):
        cindex = [0, 1, 2]
        x = [30, 10, 40]
        y = [10, 30, 40]
        z = [100, 200, 300]

        ls = cf.loads(cindex, x, y, z=z, geom_type='LineString')
        desired = wkt.loads(self.fixture_wkt['3d']['linestring'])
        self.assertEqual(ls, desired)

    def test_loads_linestring_2d_multipart(self):
        cindex = [0, 1, 2, NCSG_MULTIPART_BREAK_VALUE, 3, 4, 5, 6]
        x = [10, 20, 10, 40, 30, 40, 30]
        y = [10, 20, 40, 40, 30, 20, 10]

        mls = cf.loads(cindex, x, y, geom_type='linestring')
        desired = wkt.loads(self.fixture_wkt['2d']['multilinestring'])
        self.assertEqual(mls, desired)

    def test_loads_linestring_3d_multipart(self):
        cindex = [0, 1, 2, NCSG_MULTIPART_BREAK_VALUE, 3, 4, 5, 6]
        x = [10, 20, 10, 40, 30, 40, 30]
        y = [10, 20, 40, 40, 30, 20, 10]
        z = [100, 200, 300, 100, 200, 300, 400]

        mls = cf.loads(cindex, x, y, z=z, geom_type='linestring')
        desired = wkt.loads(self.fixture_wkt['3d']['multilinestring'])
        self.assertEqual(mls, desired)


class TestPolygon(AbstractNCSGTest):
    def test_loads_polygon_2d(self):
        cindex = [0, 1, 2, 3, 0]
        x = [30, 40, 20, 10]
        y = [10, 40, 40, 20]

        p = cf.loads(cindex, x, y, geom_type='polygon')
        desired = wkt.loads(self.fixture_wkt['2d']['polygon'])
        self.assertEqual(p, desired)

    def test_loads_polygon_2d_hole(self):
        cindex = [0, 1, 2, 3, NCSG_HOLE_BREAK_VALUE, 4, 5, 6, 4]
        x = [35, 45, 15, 10, 20, 35, 30]
        y = [10, 45, 40, 20, 30, 35, 20]

        p = cf.loads(cindex, x, y, geom_type='polygon')
        desired = wkt.loads(self.fixture_wkt['2d']['polygon_hole'])
        self.assertEqual(p, desired)

    def test_loads_polygon_2d_multipart_hole(self):
        cindex = [0, 1, 2, 3, NCSG_MULTIPART_BREAK_VALUE, 4, 5, 6, 7, 8, 9, NCSG_HOLE_BREAK_VALUE, 10, 11, 12, 13]
        x = [40, 20, 45, 40, 20, 10, 10, 30, 45, 20, 30, 20, 20, 30]
        y = [40, 45, 30, 40, 35, 30, 10, 5, 20, 35, 20, 15, 25, 20]

        p = cf.loads(cindex, x, y, geom_type='polygon')
        desired = wkt.loads(self.fixture_wkt['2d']['multipolygon_hole'])
        self.assertEqual(p, desired)
