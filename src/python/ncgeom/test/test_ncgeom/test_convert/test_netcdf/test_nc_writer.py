import pytest
from netCDF4 import Dataset

from ..... import GeometryContainer, Geometry, Part
from ..... convert.netcdf.nc_writer import write_netcdf
from .... base import AbstractNcgeomTest


point = Geometry('point', Part([10], [0]))

x = [10, 5, 0]
y = [0, 5, 0]
poly = Geometry('polygon', Part(x, y))
line = Geometry('line', Part(x, y))

x1 = [9, 5, 1]
y1 = [1, 4, 1]
z1 = [1, 1, 1]
poly2 = Geometry('polygon', Part(x1, y1, z1))

parts = [Part(x, y), Part(x1, y1, z1, is_hole=True)]
poly_hole = Geometry('polygon', parts)



class TestNcWriter(AbstractNcgeomTest):
    def test_write_netcdf(self):
        path = self.get_temporary_file_path('foo.nc')
        container = GeometryContainer([poly, poly2])
        write_netcdf(container, path)
        with Dataset(path) as nc:
            self.assertIn('geometry_container', nc.variables)


    def test_polygon_orientation(self):
        path = self.get_temporary_file_path('foo.nc')
        container = GeometryContainer(poly_hole)
        write_netcdf(container, path)
        with Dataset(path) as nc:
            x = nc.variables['x']
            self.assertEqual(list(x), [10, 5, 0, 1, 5, 9])
