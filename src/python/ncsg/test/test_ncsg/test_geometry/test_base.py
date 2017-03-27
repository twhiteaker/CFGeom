import netCDF4 as nc
from shapely.geometry import Point

from ncsg import cf
from ncsg.geometry.base import CFGeometryCollection
from ncsg.test.base import AbstractNCSGTest


class TestCFGeometryCollection(AbstractNCSGTest):
    def test_write_netcdf(self):
        path = self.get_temporary_file_path('foo.nc')

        geoms = [Point(1, 2, 10), Point(3, 4, 11), Point(5, 6, 12)]
        coll = cf.from_shapely('Point', geoms, string_id='tester_')
        coll.write_netcdf(path)

        with nc.Dataset(path) as source:
            self.assertIn('tester_geometry_container', source.variables)

    def test_polygon_orientation(self):
        # Pass clockwise exterior and anticlockwise interior
        x = [0.0, 10.0, 10.0, 0.0, 1.0, 9.0, 9.0, 1.0]
        y = [0.0, 10.0, 0.0, 0.0, 1.0, 1.0, 9.0, 1.0]
        geom = [{'x': x[:4], 'y': y[:4], 'ring_type': 0},
                {'x': x[4:], 'y': y[4:], 'ring_type': 1}]
        cf_col = CFGeometryCollection('polygon', [geom])
        # Expect anticlockwise exterior and clockwise interior
        out_x, out_y, z, node_cnt, part_node_cnt, interior_ring = cf_col.export_cra_arrays()
        self.assertEqual(x[:4][::-1], out_x[:4])
        self.assertEqual(y[:4][::-1], out_y[:4])
        self.assertEqual(x[4:][::-1], out_x[4:])
        self.assertEqual(y[4:][::-1], out_y[4:])

    def test_polygon_last_node_equals_first(self):
        x = [0, 1, 1]
        y = [0, 1, 0.5]
        geom = [{'x': x, 'y': y, 'ring_type': 0}]
        cf_col = CFGeometryCollection('polygon', [geom])
        out_x, out_y, z, node_cnt, part_node_cnt, interior_ring = cf_col.export_cra_arrays()
        self.assertEqual(x[0], out_x[-1])
        self.assertEqual(y[0], out_y[-1])
