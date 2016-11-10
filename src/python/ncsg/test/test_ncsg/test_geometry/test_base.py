import netCDF4 as nc
from shapely.geometry import Point

from ncsg import cf
from ncsg.test.base import AbstractNCSGTest


class TestCFGeometryCollection(AbstractNCSGTest):
    def test_write_netcdf(self):
        path = self.get_temporary_file_path('foo.nc')

        geoms = [Point(1, 2, 10), Point(3, 4, 11), Point(5, 6, 12)]
        coll = cf.from_shapely('Point', geoms, string_id='tester_')
        coll.write_netcdf(path)

        with nc.Dataset(path) as source:
            self.assertIn('tester_coordinate_index', source.variables)
