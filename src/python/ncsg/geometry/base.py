import os
import subprocess
import tempfile
from abc import ABCMeta

import netCDF4 as nc
import numpy as np

from ncsg import cf
from ncsg.base import AbstractNCSGObject
from ncsg.constants import NetcdfDimension, DataType, NetcdfVariable, OuterRingOrder, ClosureConvention, StopEncoding, \
    GeneralAttributes


class CFGeometryCollection(AbstractNCSGObject):
    """
    A collection of CF geometries.
    """
    # TODO: Docstring and commenting
    __metaclass__ = ABCMeta

    def __init__(self, geom_type, cindex, x, y, z=None, start_index=0, multipart_break=None, hole_break=None,
                 outer_ring_order=None, closure_convention=ClosureConvention.INDEPENDENT, string_id=None):
        geom_type = geom_type.lower()
        if geom_type.startswith('multi'):
            assert multipart_break is not None

        cindex_new = np.zeros(len(cindex), dtype=object)
        for idx, ii in enumerate(cindex):
            cindex_new[idx] = np.array(ii, dtype=DataType.INT)

        if string_id is None:
            string_id = ''
        self.string_id = string_id
        self.cindex = cindex_new
        self.x = x
        self.y = y
        self.z = z
        self.geom_type = geom_type

        self.start_index = start_index
        self.multipart_break = multipart_break
        self.hole_break = hole_break
        self.outer_ring_order = outer_ring_order
        self.closure_convention = closure_convention

        self.cf_names = {'variables': {'coordinate_index': '{}{}'.format(string_id,
                                                                         NetcdfVariable.COORDINATE_INDEX)},
                         'dimensions': {'geometry_count': '{}{}'.format(string_id, NetcdfDimension.GEOMETRY_COUNT)}}

        assert len(self.x) == len(self.y)
        if self.z is not None:
            assert len(self.z) == len(self.x)

    def __eq__(self, other):
        ret = True
        for k, v in self.__dict__.items():
            ov = other.__dict__[k]
            try:
                if k == GeneralAttributes.GEOM_TYPE_NAME:
                    if v.lower() != ov.lower():
                        raise AssertionError('Geometry types are not equal.')
                elif k == 'cindex':
                    for idx in range(len(v)):
                        _assert_array_equal_(v[idx], ov[idx])
                elif k in ['x', 'y', 'z']:
                    _assert_array_equal_(v, ov)
                else:
                    if v != ov:
                        raise AssertionError('"{}" are not equal.'.format(k))
            except AssertionError as _:
                ret = False
        return ret

    def as_shapely(self):
        ret = [None] * len(self.cindex)
        for idx in range(len(self.cindex)):
            geom = cf.to_shapely(self.geom_type, self.cindex[idx], self.x, self.y, z=self.z,
                                 start_index=self.start_index, multipart_break=self.multipart_break,
                                 hole_break=self.hole_break)
            ret[idx] = geom

        return tuple(ret)

    def describe(self, cra=False, header=True, capture=False):
        path = os.path.join(tempfile.gettempdir(), '_ncsg_describe_.nc')
        self.write_netcdf(path, cra=cra)
        ret = None
        try:
            cmd = ['ncdump']
            if header:
                cmd.append('-h')
            cmd.append(path)
            if capture:
                ret = str(subprocess.check_output(cmd))
            else:
                subprocess.check_call(cmd)
        finally:
            os.remove(path)
        return ret

    def write_netcdf(self, path_or_object, cra=False):
        string_id = self.string_id

        should_close = False
        if isinstance(path_or_object, nc.Dataset):
            ds = path_or_object
        else:
            ds = nc.Dataset(path_or_object, mode='w')
            should_close = True

        setattr(ds, GeneralAttributes.CONVENTIONS, GeneralAttributes.CONVENTIONS_VALUE)

        try:
            dname_node_count = '{}{}'.format(string_id, NetcdfDimension.NODE_COUNT)
            dname_geom_count = self.cf_names['dimensions']['geometry_count']
            vname_x = '{}{}'.format(string_id, NetcdfVariable.X)
            vname_y = '{}{}'.format(string_id, NetcdfVariable.Y)
            vname_z = '{}{}'.format(string_id, NetcdfVariable.Z)
            vname_cindex = self.cf_names['variables']['coordinate_index']

            ds.createDimension(dname_node_count, size=len(self.x))
            if cra:
                from ncsg.cra import ContiguousRaggedArray

                dname_cra_node_index = '{}{}'.format(string_id, NetcdfDimension.CRA_NODE_INDEX)
                vname_cra_stop = '{}{}'.format(string_id, NetcdfVariable.CRA_STOP)

                cra_obj = ContiguousRaggedArray.from_vlen(self.cindex, start_index=self.start_index)
                ds.createDimension(dname_geom_count, size=len(cra_obj.stops))
                ds.createDimension(dname_cra_node_index, size=len(cra_obj.value))
                cindex = ds.createVariable(vname_cindex, DataType.INT, dimensions=(dname_cra_node_index,))
                stops = ds.createVariable(vname_cra_stop, DataType.INT, dimensions=(dname_geom_count,))
            else:
                ds.createDimension(dname_geom_count, size=len(self.cindex))
                try:
                    vltype = ds.createVLType(DataType.INT, DataType.GEOMETRY_VLTYPE)
                except RuntimeError:
                    # Type is likely already created. Try to access it.
                    vltype = ds.vltypes[DataType.GEOMETRY_VLTYPE]
                cindex = ds.createVariable(vname_cindex, vltype, dimensions=(dname_geom_count,))

            if cra:
                stop_encoding = StopEncoding.CRA
                cindex_value = cra_obj.value
                stops[:] = cra_obj.stops
                setattr(stops, GeneralAttributes.RAGGED_DIMENSION, dname_cra_node_index)
            else:
                stop_encoding = StopEncoding.VLEN
                cindex_value = self.cindex
            cindex[:] = cindex_value

            cindex.cf_role = GeneralAttributes.CF_ROLE_VALUE
            cindex.geom_type = self.geom_type
            setattr(cindex, GeneralAttributes.GEOM_DIMENSION, dname_geom_count)

            coordinates = [vname_x, vname_y]
            if self.z is not None:
                coordinates.append(vname_z)
            setattr(cindex, GeneralAttributes.COORDINATES, ' '.join(coordinates))
            setattr(cindex, StopEncoding.NAME, stop_encoding)
            if self.multipart_break is not None:
                cindex.multipart_break_value = self.multipart_break
            if 'polygon' in self.geom_type:
                if self.hole_break is not None:
                    cindex.hole_break_value = self.hole_break
                if self.outer_ring_order is not None:
                    setattr(cindex, OuterRingOrder.NAME, self.outer_ring_order)
                setattr(cindex, ClosureConvention.NAME, self.closure_convention)

            x = ds.createVariable(vname_x, DataType.FLOAT, dimensions=(dname_node_count,))
            x[:] = self.x
            setattr(x, GeneralAttributes.STANDARD_NAME, GeneralAttributes.GEOM_X_NODE)

            y = ds.createVariable(vname_y, DataType.FLOAT, dimensions=(dname_node_count,))
            y[:] = self.y
            setattr(y, GeneralAttributes.STANDARD_NAME, GeneralAttributes.GEOM_Y_NODE)

            if self.z is not None:
                z = ds.createVariable(vname_z, DataType.FLOAT, dimensions=(dname_node_count,))
                z[:] = self.z
                setattr(z, GeneralAttributes.STANDARD_NAME, GeneralAttributes.GEOM_Z_NODE)

        finally:
            if should_close:
                ds.close()


def _assert_array_equal_(actual, desired):
    actual = np.array(actual)
    desired = np.array(desired)
    if actual.dtype != desired.dtype:
        raise AssertionError('Data types are not equal.')
    cmp = actual == desired
    if not cmp.all():
        raise AssertionError('Not all values are equal.')
