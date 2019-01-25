from os.path import join

import pytest
from netCDF4 import Dataset
import numpy as np

from ..... import GeometryContainer, Geometry, Part
from ..... convert.netcdf.nc_writer import write_netcdf
from .... base import AbstractNcgeomTest
from ..... convert.json_io.json_reader import json_to_container


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


def _has_vltype(dataset, name, dtype=None):
    if name not in dataset.vltypes:
        return False
    if dtype is not None:
        vltype = dataset.vltypes[name]
        if vltype.dtype != dtype:
            return False
    return True


def _has_dim(dataset, name, length=None):
    if name not in dataset.dimensions:
        return False
    if length is not None:
        dim = dataset.dimensions[name]
        if len(dim) != length:
            return False
    return True


def _vals_equal(v1, v2):
    try:
        # Might be arrays
        if len(v1) != len(v2):
            return False
        for i, x1 in enumerate(v1):
            x2 = v2[i]
            if not _vals_equal(x1, x2):
                return False
    except Exception as ex:
        # Must be single values
        if ((np.isnan(v1) and not np.isnan(v2)) or
            (not np.isnan(v1) and np.isnan(v2))):
                return False
        if not np.isnan(v1) and v1 != v2:
            return False
    return True


def _has_var(dataset, name, dtype=None, vals=None):
    if name not in dataset.variables:
        return False
    var = dataset.variables[name]
    if dtype is not None:
         if var.dtype != dtype:
            return False
    if vals is not None:
        if not _vals_equal(var, vals):
            return False
    return True


def _has_attr(owner, name, val=None):
    if name not in owner.ncattrs():
        return False
    if val is not None:
        attr = getattr(owner, name)
        if attr != val:
            return False
    return True


class TestNcWriter(AbstractNcgeomTest):
    def test_write_point_z(self):
        root = join(self.path_data, 'simplified_examples')
        json_file = join(root, 'point_z.json')
        with open(json_file) as f:
            data = f.read()
        container = json_to_container(data)
        for vlen in [False, True]:
            tmp_file = self.get_temporary_file_path('foo.nc')
            container.to_netcdf(tmp_file, use_vlen=vlen)
            with Dataset(tmp_file) as nc:
                assert _has_dim(nc, 'instance', 2)
                assert not _has_dim(nc, 'node')
                assert not _has_dim(nc, 'part')
                assert _has_var(nc, 'geometry_container')
                var = nc.variables['geometry_container']
                assert _has_attr(var, 'geometry_type', 'point')
                assert _has_attr(var, 'node_coordinates', 'x y z')
                assert not _has_attr(var, 'node_count')
                assert not _has_attr(var, 'part_node_count')
                assert not _has_attr(var, 'interior_ring')
                assert not _has_var(nc, 'node_count')
                assert not _has_var(nc, 'part_node_count')
                assert not _has_var(nc, 'interior_ring')
                assert _has_var(nc, 'x', float, [1, 2])
                assert _has_var(nc, 'y', float, [1, 3])
                assert _has_var(nc, 'z', float, [np.nan, 50])


    def test_write_multipoint(self):
        root = join(self.path_data, 'simplified_examples')
        json_file = join(root, 'multipoint.json')
        with open(json_file) as f:
            data = f.read()
        container = json_to_container(data)
        for vlen in [False, True]:
            tmp_file = self.get_temporary_file_path('foo.nc')
            container.to_netcdf(tmp_file, use_vlen=vlen)
            with Dataset(tmp_file) as nc:
                assert _has_dim(nc, 'instance', 2)
                assert _has_var(nc, 'geometry_container')
                var = nc.variables['geometry_container']
                assert _has_attr(var, 'geometry_type', 'point')
                assert not _has_attr(var, 'part_node_count')
                assert not _has_attr(var, 'interior_ring')
                assert not _has_var(nc, 'part_node_count')
                assert not _has_var(nc, 'interior_ring')
                assert not _has_dim(nc, 'part')
                if vlen:
                    assert _has_vltype(nc, 'node_VLType', float)
                    assert not _has_vltype(nc, 'part_node_VLType')
                    assert not _has_var(nc, 'node_count')
                    assert _has_var(nc, 'x', float, [[1], [1, 4]])
                    assert _has_var(nc, 'y', float, [[1], [4, 3]])
                else:
                    assert _has_dim(nc, 'node', 3)
                    assert _has_attr(var, 'node_count', 'node_count')
                    assert _has_var(nc, 'node_count', int, [1, 2])
                    assert _has_var(nc, 'x', float, [1, 1, 4])
                    assert _has_var(nc, 'y', float, [1, 4, 3])


    def test_write_line(self):
        root = join(self.path_data, 'simplified_examples')
        json_file = join(root, 'line.json')
        with open(json_file) as f:
            data = f.read()
        container = json_to_container(data)
        for vlen in [False, True]:
            tmp_file = self.get_temporary_file_path('foo.nc')
            container.to_netcdf(tmp_file, use_vlen=vlen)
            with Dataset(tmp_file) as nc:
                assert not _has_dim(nc, 'part')
                var = nc.variables['geometry_container']
                assert _has_attr(var, 'geometry_type', 'line')
                assert not _has_attr(var, 'part_node_count')
                assert not _has_attr(var, 'interior_ring')
                assert not _has_var(nc, 'part_node_count')
                assert not _has_var(nc, 'interior_ring')
                if vlen:
                    assert _has_vltype(nc, 'node_VLType', float)
                    assert not _has_vltype(nc, 'part_node_VLType')
                else:
                    assert _has_dim(nc, 'node', 5)
                    assert _has_attr(var, 'node_count', 'node_count')
                    assert _has_attr(var, 'node_coordinates', 'x y')
                    assert _has_var(nc, 'node_count', int, [3, 2])


    def test_write_multiline(self):
        root = join(self.path_data, 'simplified_examples')
        json_file = join(root, 'multiline.json')
        with open(json_file) as f:
            data = f.read()
        container = json_to_container(data)
        for vlen in [False, True]:
            tmp_file = self.get_temporary_file_path('foo.nc')
            container.to_netcdf(tmp_file, use_vlen=vlen)
            with Dataset(tmp_file) as nc:
                var = nc.variables['geometry_container']
                assert _has_attr(var, 'geometry_type', 'line')
                assert _has_attr(var, 'part_node_count', 'part_node_count')
                assert not _has_attr(var, 'interior_ring')
                assert not _has_var(nc, 'interior_ring')
                if vlen:
                    assert _has_vltype(nc, 'node_VLType', float)
                    assert _has_vltype(nc, 'part_node_VLType', int)
                    assert _has_var(nc, 'part_node_count', int, [[3], [2, 2]])
                else:
                    assert _has_dim(nc, 'node', 7)
                    assert _has_dim(nc, 'part', 3)
                    assert _has_attr(var, 'node_count', 'node_count')
                    assert _has_var(nc, 'node_count', int, [3, 4])
                    assert _has_var(nc, 'part_node_count', int, [3, 2, 2])


    def test_write_polygon(self):
        root = join(self.path_data, 'simplified_examples')
        json_file = join(root, 'polygon.json')
        with open(json_file) as f:
            data = f.read()
        container = json_to_container(data)
        for vlen in [False, True]:
            tmp_file = self.get_temporary_file_path('foo.nc')
            container.to_netcdf(tmp_file, use_vlen=vlen)
            with Dataset(tmp_file) as nc:
                assert not _has_dim(nc, 'part')
                var = nc.variables['geometry_container']
                assert _has_attr(var, 'geometry_type', 'polygon')
                assert not _has_attr(var, 'part_node_count')
                assert not _has_attr(var, 'interior_ring')
                assert not _has_var(nc, 'part_node_count')
                assert not _has_var(nc, 'interior_ring')
                if vlen:
                    assert _has_vltype(nc, 'node_VLType', float)
                    assert not _has_vltype(nc, 'part_node_VLType')
                else:
                    assert _has_dim(nc, 'node', 7)
                    assert _has_attr(var, 'node_count', 'node_count')
                    assert _has_var(nc, 'node_count', int, [3, 4])


    def test_write_multipolygon(self):
        root = join(self.path_data, 'simplified_examples')
        json_file = join(root, 'multipolygon.json')
        with open(json_file) as f:
            data = f.read()
        container = json_to_container(data)
        for vlen in [False, True]:
            tmp_file = self.get_temporary_file_path('foo.nc')
            container.to_netcdf(tmp_file, use_vlen=vlen)
            with Dataset(tmp_file) as nc:
                assert _has_dim(nc, 'instance', 2)
                assert _has_var(nc, 'geometry_container')
                var = nc.variables['geometry_container']
                assert _has_attr(var, 'geometry_type', 'polygon')
                assert _has_attr(var, 'node_coordinates', 'x y')
                assert _has_attr(var, 'part_node_count', 'part_node_count')
                assert _has_attr(var, 'interior_ring', 'interior_ring')
                if vlen:
                    assert _has_vltype(nc, 'node_VLType', float)
                    assert _has_vltype(nc, 'part_node_VLType', int)
                    assert not _has_var(nc, 'node_count')
                    assert _has_var(nc, 'part_node_count', int, [[3], [3, 3, 4]])
                    assert _has_var(nc, 'interior_ring', int, [[0], [0, 1, 0]])
                    assert _has_var(nc, 'x', float, [[100, 75, 50], [10, 5, 0, 1, 5, 9, 20, 15, 11, 15]])
                    assert _has_var(nc, 'y', float, [[100, 500, 100], [0, 5, 0, 1, 4, 1, 20, 25, 20, 15]])
                else:
                    assert _has_dim(nc, 'node', 13)
                    assert _has_dim(nc, 'part', 4)
                    assert _has_attr(var, 'node_count', 'node_count')
                    assert _has_var(nc, 'node_count', int, [3, 10])
                    assert _has_var(nc, 'part_node_count', int, [3, 3, 3, 4])
                    assert _has_var(nc, 'interior_ring', int, [0, 0, 1, 0])
                    assert _has_var(nc, 'x', float, [100, 75, 50, 10, 5, 0, 1, 5, 9, 20, 15, 11, 15])
                    assert _has_var(nc, 'y', float, [100, 500, 100, 0, 5, 0, 1, 4, 1, 20, 25, 20, 15])
                assert not _has_var(nc, 'z')


    def test_polygon_orientation(self):
            path = self.get_temporary_file_path('foo.nc')
            container = GeometryContainer(poly_hole)
            write_netcdf(container, path)
            with Dataset(path) as nc:
                x = nc.variables['x']
                self.assertEqual(list(x), [10, 5, 0, 1, 5, 9])
