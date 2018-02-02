import os
import tempfile

from shapely import wkt
from shapely.geometry import MultiPoint, Point
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import orient

from ncsg import cf
from ncsg.cf import loads_from_netcdf
from ncsg.constants import NetcdfVariable
from ncsg.geometry.base import CFGeometryCollection
from ncsg.test.base import AbstractNCSGTest


class Test(AbstractNCSGTest):
    def test_loads_from_netcdf(self):
        for dim, wkts in self.fixture_wkt.items():
            for geom_type, wktvalue in wkts.items():
                geom = wkt.loads(wktvalue)
                coll = cf.from_shapely(geom)
                path = self.get_temporary_file_path('{}_{}.nc'.format(dim, geom_type))
                coll.write_netcdf(path)
                loaded_coll = loads_from_netcdf(path)[0]
                self.assertTrue(geom.almost_equals(loaded_coll.as_shapely()[0]))
                self.assertTrue(coll.as_shapely()[0].almost_equals(loaded_coll.as_shapely()[0]))
                self.assertEqual(loaded_coll, coll)

        # Test with a target.
        wktvalue = self.fixture_wkt['2d']['point']
        geom = wkt.loads(wktvalue)
        coll = cf.from_shapely(geom)
        path = self.get_temporary_file_path('target.nc')
        coll.write_netcdf(path)
        loaded = loads_from_netcdf(path, target=NetcdfVariable.GEOMETRY_CONTAINER)[0]
        self.assertEqual(coll, loaded)


class TestPoint(AbstractNCSGTest):
    def test_from_shapely_point_3d(self):
        geoms = [Point(1, 2, 10), Point(3, 4, 11), Point(5, 6, 12)]
        coll = cf.from_shapely(geoms)
        self.assertEqual(len(coll.geoms), 3)
        self.assertIsNotNone(coll.geoms[0][0]['z'])

    def test_to_shapely_point_2d(self):
        geom = [{'x': [30], 'y': [10]}]

        pt = cf.to_shapely('point', geom)
        desired = wkt.loads(self.fixture_wkt['2d']['point'])
        self.assertEqual(pt, desired)

        # Test this will be converted to a multipart if requested.
        mpt = cf.to_shapely('point', geom, 'multipoint')
        self.assertIsInstance(mpt, MultiPoint)

    def test_to_shapely_point_3d(self):
        geom = [{'x': [30], 'y': [10], 'z': [100]}]

        pt = cf.to_shapely('point', geom)
        desired = wkt.loads(self.fixture_wkt['3d']['point'])
        self.assertEqual(pt, desired)

    def test_to_shapely_point_2d_multipart(self):
        geom = [{'x': [10], 'y': [40]},
                {'x': [40], 'y': [30]},
                {'x': [20], 'y': [20]},
                {'x': [30], 'y': [10]}]

        mpt = cf.to_shapely('point', geom)
        desired = wkt.loads(self.fixture_wkt['2d']['multipoint'])
        self.assertEqual(mpt, desired)

    def test_to_shapely_point_3d_multipart(self):
        geom = [{'x': [10], 'y': [40], 'z': [100]},
                {'x': [40], 'y': [30], 'z': [200]},
                {'x': [20], 'y': [20], 'z': [300]},
                {'x': [30], 'y': [10], 'z': [400]}]

        mpt = cf.to_shapely('point', geom)
        desired = wkt.loads(self.fixture_wkt['3d']['multipoint'])
        self.assertEqual(mpt, desired)


class TestLineString(AbstractNCSGTest):
    def test_from_shapely_linestring_2d_multipart(self):
        geom = wkt.loads(self.fixture_wkt['2d']['multilinestring'])
        coll = cf.from_shapely(geom)
        self.assertEqual(len(coll.geoms), 1)
        self.assertEqual(len(coll.geoms[0]), 2)
        self.assertEqual(len(coll.geoms[0][0]['x']), 3)

    def test_to_shapely_linestring_2d(self):
        geom = [{'x': [30, 10, 40], 'y': [10, 30, 40]}]

        ls = cf.to_shapely('line', geom)
        desired = wkt.loads(self.fixture_wkt['2d']['linestring'])
        self.assertEqual(ls, desired)

    def test_to_shapely_linestring_3d(self):
        geom = [{'x': [30, 10, 40], 'y': [10, 30, 40], 'z': [100, 200, 300]}]

        ls = cf.to_shapely('line', geom)
        desired = wkt.loads(self.fixture_wkt['3d']['linestring'])
        self.assertEqual(ls, desired)

    def test_to_shapely_linestring_2d_multipart(self):
        geom = [{'x': [10, 20, 10], 'y': [10, 20, 40]},
                {'x': [40, 30, 40, 30], 'y': [40, 30, 20, 10]}]

        mls = cf.to_shapely('line', geom)
        desired = wkt.loads(self.fixture_wkt['2d']['multilinestring'])
        self.assertEqual(mls, desired)

    def test_to_shapely_linestring_3d_multipart(self):
        geom = [{'x': [10, 20, 10], 'y': [10, 20, 40], 'z': [100, 200, 300]},
                {'x': [40, 30, 40, 30], 'y': [40, 30, 20, 10], 'z': [100, 200, 300, 400]}]

        mls = cf.to_shapely('line', geom)
        desired = wkt.loads(self.fixture_wkt['3d']['multilinestring'])
        self.assertEqual(mls, desired)


class TestPolygon(AbstractNCSGTest):
    def test_from_shapely_polygon(self):
        for d in ['2d', '3d']:
            poly1 = wkt.loads(self.fixture_wkt[d]['polygon'])
            poly2 = wkt.loads(self.fixture_wkt[d]['polygon_hole'])

            geoms = [orient(poly1, sign=-1.0), poly2]
            res = cf.from_shapely(geoms)
            self.assertIsInstance(res, CFGeometryCollection)

            for ctr, geom in enumerate(res.geoms):
                loaded = cf.to_shapely('polygon', geom)
                if ctr == 0:
                    desired = orient(geoms[0])
                else:
                    desired = geoms[ctr]
                self.assertTrue(loaded.almost_equals(desired))

    def test_from_shapely_polygon_other(self):
        p1 = 'POLYGON ((0 0, 6 0, 3 6, 0 0), (2 1, 3 2, 4 1, 2 1))'
        p2 = 'POLYGON ((4 6, 7 0, 10 6, 4 6))'
        mp = MultiPolygon([wkt.loads(p1), wkt.loads(p2)])

        for cra in [False, True]:
            # Test with a single multipolygon.
            res = cf.from_shapely(mp)
            path = os.path.join(tempfile.gettempdir(), '_ncsg_test_output_.nc')
            res.write_netcdf(path, cra=cra)
            # self.ncdump(path, header=False)
            os.remove(path)

            # Test with multiple polygons.
            res = cf.from_shapely([mp, wkt.loads(p1), wkt.loads(p2)])
            path = os.path.join(tempfile.gettempdir(), '_ncsg_test_output_.nc')
            res.write_netcdf(path, cra=cra)
            # self.ncdump(path, header=False)
            os.remove(path)

    def test_to_shapely_polygon_2d(self):
        geom = [{'x': [30, 40, 20, 10], 'y': [10, 40, 40, 20]}]

        p = cf.to_shapely('polygon', geom)
        desired = wkt.loads(self.fixture_wkt['2d']['polygon'])
        self.assertEqual(p, desired)

    def test_to_shapely_polygon_2d_hole(self):
        geom = [{'x': [35, 45, 15, 10], 'y': [10, 45, 40, 20], 'ring_type': 0},
                {'x': [20, 35, 30, 20], 'y': [30, 35, 20, 30], 'ring_type': 1}]

        p = cf.to_shapely('polygon', geom)
        desired = wkt.loads(self.fixture_wkt['2d']['polygon_hole'])
        self.assertEqual(p, desired)

    def test_to_shapely_polygon_2d_multipart_hole(self):
        geom = [{'x': [40, 20, 45], 'y': [40, 45, 30], 'ring_type': 0},
                {'x': [20, 10, 10, 30, 45], 'y': [35, 30, 10, 5, 20], 'ring_type': 0},
                {'x': [30, 20, 20], 'y': [20, 15, 25], 'ring_type': 1}]

        p = cf.to_shapely('polygon', geom)
        desired = wkt.loads(self.fixture_wkt['2d']['multipolygon_hole'])
        self.assertEqual(p, desired)

    def test_to_shapely_polygon_2d_multipart_holes(self):
        geom = [{'x': [0, 20, 20, 0], 'y': [0, 0, 20, 20], 'ring_type': 0},
                {'x': [1, 10, 19], 'y': [1, 5, 1], 'ring_type': 1},
                {'x': [5, 7, 9], 'y': [15, 19, 15], 'ring_type': 1},
                {'x': [11, 13, 15], 'y': [15, 19, 15], 'ring_type': 1},
                {'x': [5, 9, 7], 'y': [25, 25, 29], 'ring_type': 0},
                {'x': [11, 15, 13], 'y': [25, 25, 29], 'ring_type': 0}]

        p = cf.to_shapely('polygon', geom)
        desired = wkt.loads(self.fixture_wkt['2d']['multipolygons_holes'])
        self.assertEqual(p, desired)
