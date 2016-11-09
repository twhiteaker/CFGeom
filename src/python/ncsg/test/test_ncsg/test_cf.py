import os
import tempfile

from shapely import wkt
from shapely.geometry import MultiPoint, Point
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import orient

from ncsg import cf
from ncsg.cf import loads_from_netcdf
from ncsg.constants import BreakValue, OuterRingOrder, ClosureConvention, NetcdfVariable
from ncsg.cra import ContinuousRaggedArray
from ncsg.geometry.base import CFGeometryCollection
from ncsg.test.base import AbstractNCSGTest


class Test(AbstractNCSGTest):
    def test_loads_from_netcdf(self):
        for dim, wkts in self.fixture_wkt.items():
            for geom_type, wktvalue in wkts.items():
                geom = wkt.loads(wktvalue)
                coll = cf.from_shapely(geom.geom_type, geom)
                path = self.get_temporary_file_path('{}_{}.nc'.format(dim, geom_type))
                coll.write_netcdf(path)
                loaded_coll = loads_from_netcdf(path)[0]
                self.assertTrue(geom.almost_equals(loaded_coll.as_shapely()[0]))
                self.assertTrue(coll.as_shapely()[0].almost_equals(loaded_coll.as_shapely()[0]))
                self.assertEqual(loaded_coll, coll)

        # Test with a target.
        wktvalue = self.fixture_wkt['2d']['point']
        geom = wkt.loads(wktvalue)
        coll = cf.from_shapely(geom.geom_type, geom)
        path = self.get_temporary_file_path('target.nc')
        coll.write_netcdf(path)
        loaded = loads_from_netcdf(path, target=NetcdfVariable.COORDINATE_INDEX)[0]
        self.assertEqual(coll, loaded)


class TestContinuousRaggedArray(AbstractNCSGTest):
    def test_as_vlen(self):
        for start_index in [0, 1]:
            value = [[1, 2, 3], [4], [5, 6, 7, 8]]
            cra_base = ContinuousRaggedArray.from_vlen(value, start_index=start_index)
            cra = ContinuousRaggedArray(cra_base.value, cra_base.stops, start_index=start_index)
            self.assertEqual(cra.as_vlen(), value)

    def test_from_vlen(self):
        value = [[1, 2, 3], [4], [5, 6, 7, 8]]
        cra = ContinuousRaggedArray.from_vlen(value)
        desired = []
        for ii in value:
            desired += ii
        self.assertEqual(cra.value, desired)
        self.assertEqual(cra.stops, [2, 3, 7])

        cra = ContinuousRaggedArray.from_vlen(value, start_index=1)
        self.assertEqual(cra.stops, [3, 4, 8])


class TestStartIndex(AbstractNCSGTest):
    def test_start_index_point_2d_multipart(self):
        cindex = [1, BreakValue.MULTIPART, 2, BreakValue.MULTIPART, 3, BreakValue.MULTIPART, 4]
        x = [10, 40, 20, 30]
        y = [40, 30, 20, 10]

        mpt = cf.to_shapely('multipoint', cindex, x, y, start_index=1)
        desired = wkt.loads(self.fixture_wkt['2d']['multipoint'])
        self.assertEqual(mpt, desired)

    
class TestPoint(AbstractNCSGTest):
    def test_from_shapely_point_3d(self):
        geoms = [Point(1, 2, 10), Point(3, 4, 11), Point(5, 6, 12)]
        coll = cf.from_shapely('Point', geoms, multipart_break=None)
        self.assertIsNone(coll.multipart_break)
        self.assertEqual(len(coll.cindex), 3)
        self.assertIsNotNone(coll.z)
        # coll.describe(cra=True, header=False)

    def test_loads_point_2d(self):
        cindex = [1]
        x = [30]
        y = [10]

        pt = cf.to_shapely('point', cindex, x, y, start_index=1)
        desired = wkt.loads(self.fixture_wkt['2d']['point'])
        self.assertEqual(pt, desired)

        # Test this will be converted to a multipart if requested.
        mpt = cf.to_shapely('multipoint', cindex, x, y, start_index=1)
        self.assertIsInstance(mpt, MultiPoint)

    def test_loads_point_3d(self):
        cindex = [0]
        x = [30]
        y = [10]
        z = [100]

        pt = cf.to_shapely('point', cindex, x, y, z=z)
        desired = wkt.loads(self.fixture_wkt['3d']['point'])
        self.assertEqual(pt, desired)

    def test_loads_point_2d_multipart(self):
        cindex = [0, BreakValue.MULTIPART, 1, BreakValue.MULTIPART, 2, BreakValue.MULTIPART, 3]
        x = [10, 40, 20, 30]
        y = [40, 30, 20, 10]

        mpt = cf.to_shapely('multipoint', cindex, x, y)
        desired = wkt.loads(self.fixture_wkt['2d']['multipoint'])
        self.assertEqual(mpt, desired)

    def test_loads_point_3d_multipart(self):
        cindex = [0, BreakValue.MULTIPART, 1, BreakValue.MULTIPART, 2, BreakValue.MULTIPART, 3]
        x = [10, 40, 20, 30]
        y = [40, 30, 20, 10]
        z = [100, 200, 300, 400]

        mpt = cf.to_shapely('multipoint', cindex, x, y, z=z)
        desired = wkt.loads(self.fixture_wkt['3d']['multipoint'])
        self.assertEqual(mpt, desired)


class TestLineString(AbstractNCSGTest):
    def test_from_shapely_linestring_2d_multipart(self):
        geom = wkt.loads(self.fixture_wkt['2d']['multilinestring'])
        coll = cf.from_shapely('multilinestring', geom)
        self.assertEqual(len(coll.cindex[0]), 8)
        self.assertEqual(len(coll.x), 7)

    def test_loads_linestring_2d(self):
        cindex = [0, 1, 2]
        x = [30, 10, 40]
        y = [10, 30, 40]

        ls = cf.to_shapely('LineString', cindex, x, y)
        desired = wkt.loads(self.fixture_wkt['2d']['linestring'])
        self.assertEqual(ls, desired)

    def test_loads_linestring_3d(self):
        cindex = [0, 1, 2]
        x = [30, 10, 40]
        y = [10, 30, 40]
        z = [100, 200, 300]

        ls = cf.to_shapely('linestring', cindex, x, y, z=z)
        desired = wkt.loads(self.fixture_wkt['3d']['linestring'])
        self.assertEqual(ls, desired)

    def test_loads_linestring_2d_multipart(self):
        cindex = [0, 1, 2, BreakValue.MULTIPART, 3, 4, 5, 6]
        x = [10, 20, 10, 40, 30, 40, 30]
        y = [10, 20, 40, 40, 30, 20, 10]

        mls = cf.to_shapely('multilinestring', cindex, x, y)
        desired = wkt.loads(self.fixture_wkt['2d']['multilinestring'])
        self.assertEqual(mls, desired)

    def test_loads_linestring_3d_multipart(self):
        cindex = [0, 1, 2, BreakValue.MULTIPART, 3, 4, 5, 6]
        x = [10, 20, 10, 40, 30, 40, 30]
        y = [10, 20, 40, 40, 30, 20, 10]
        z = [100, 200, 300, 100, 200, 300, 400]

        mls = cf.to_shapely('multilinestring', cindex, x, y, z=z)
        desired = wkt.loads(self.fixture_wkt['3d']['multilinestring'])
        self.assertEqual(mls, desired)


class TestPolygon(AbstractNCSGTest):
    def test_from_shapely_polygon(self):
        for d in ['2d', '3d']:
            poly1 = wkt.loads(self.fixture_wkt[d]['polygon'])
            poly2 = wkt.loads(self.fixture_wkt[d]['polygon_hole'])

            geoms = [orient(poly1, sign=-1.0), poly2, MultiPolygon([poly1, poly2])]
            res = cf.from_shapely('polygon', geoms)
            # res.describe()
            self.assertEqual(res.outer_ring_order, OuterRingOrder.CCW)
            self.assertEqual(res.closure_convention, ClosureConvention.CLOSED)
            self.assertIsInstance(res, CFGeometryCollection)

            for ctr, c in enumerate(res.cindex):
                loaded = cf.to_shapely('polygon', c, res.x, res.y, z=res.z, multipart_break=res.multipart_break,
                                       hole_break=res.hole_break)
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
            res = cf.from_shapely('polygon', mp)
            path = os.path.join(tempfile.gettempdir(), '_ncsg_test_output_.nc')
            res.write_netcdf(path, cra=cra)
            # self.ncdump(path, header=False)
            os.remove(path)

            # Test with multiple polygons.
            res = cf.from_shapely('polygon', [mp, wkt.loads(p1), wkt.loads(p2)])
            path = os.path.join(tempfile.gettempdir(), '_ncsg_test_output_.nc')
            res.write_netcdf(path, cra=cra)
            # self.ncdump(path, header=False)
            os.remove(path)

    def test_to_shapely_polygon_2d(self):
        cindex = [0, 1, 2, 3, 0]
        x = [30, 40, 20, 10]
        y = [10, 40, 40, 20]

        p = cf.to_shapely('polygon', cindex, x, y)
        desired = wkt.loads(self.fixture_wkt['2d']['polygon'])
        self.assertEqual(p, desired)

    def test_to_shapely_polygon_2d_hole(self):
        cindex = [0, 1, 2, 3, BreakValue.HOLE, 4, 5, 6, 4]
        x = [35, 45, 15, 10, 20, 35, 30]
        y = [10, 45, 40, 20, 30, 35, 20]

        p = cf.to_shapely('polygon', cindex, x, y)
        desired = wkt.loads(self.fixture_wkt['2d']['polygon_hole'])
        self.assertEqual(p, desired)

    def test_to_shapely_polygon_2d_multipart_hole(self):
        cindex = [0, 1, 2, 3, BreakValue.MULTIPART, 4, 5, 6, 7, 8, 9, BreakValue.HOLE, 10, 11, 12, 13]
        x = [40, 20, 45, 40, 20, 10, 10, 30, 45, 20, 30, 20, 20, 30]
        y = [40, 45, 30, 40, 35, 30, 10, 5, 20, 35, 20, 15, 25, 20]

        p = cf.to_shapely('multipolygon', cindex, x, y)
        desired = wkt.loads(self.fixture_wkt['2d']['multipolygon_hole'])
        self.assertEqual(p, desired)

    def test_to_shapely_polygon_2d_multipart_holes(self):
        cindex = [0, 1, 2, 3, 4, BreakValue.HOLE, 5, 6, 7, 8, BreakValue.HOLE, 9, 10, 11, 12, BreakValue.HOLE, 13, 14,
                  15, 16, BreakValue.MULTIPART, 17, 18, 19, 20, BreakValue.MULTIPART, 21, 22, 23, 24]
        x = [0, 20, 20, 0, 0, 1, 10, 19, 1, 5, 7, 9, 5, 11, 13, 15, 11, 5, 9, 7, 5, 11, 15, 13, 11]
        y = [0, 0, 20, 20, 0, 1, 5, 1, 1, 15, 19, 15, 15, 15, 19, 15, 15, 25, 25, 29, 25, 25, 25, 29, 25]

        p = cf.to_shapely('multipolygon', cindex, x, y)
        desired = wkt.loads(self.fixture_wkt['2d']['multipolygons_holes'])
        self.assertEqual(p, desired)
