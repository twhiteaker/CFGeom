import os
import subprocess
import tempfile
from abc import ABCMeta

import netCDF4 as nc
import numpy as np

from ncsg.base import AbstractNCSGObject
from ncsg.constants import NetcdfDimension, DataType, NetcdfVariable, OuterRingOrder, ClosureConvention


class CFGeometryCollection(AbstractNCSGObject):
    """
    A collection of CF geometries.
    """
    # TODO: Docstring and commenting
    __metaclass__ = ABCMeta

    def __init__(self, geom_type, cindex, x, y, z=None, start_index=0, multipart_break=None, hole_break=None,
                 outer_ring_order=None, closure_convention=ClosureConvention.INDEPENDENT):
        if geom_type.startswith('multi'):
            assert multipart_break is not None

        cindex_new = np.zeros(len(cindex), dtype=object)
        for idx, ii in enumerate(cindex):
            cindex_new[idx] = np.array(ii, dtype=DataType.INT)

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

        assert len(self.x) == len(self.y)
        if self.z is not None:
            assert len(self.z) == len(self.x)

    def describe(self, cra=False, header=True):
        path = os.path.join(tempfile.gettempdir(), '_ncsg_describe_.nc')
        self.write_netcdf(path, cra=cra)
        try:
            cmd = ['ncdump']
            if header:
                cmd.append('-h')
            cmd.append(path)
            subprocess.check_call(cmd)
        finally:
            os.remove(path)

    def write_netcdf(self, path_or_object, cra=False):
        should_close = False
        if isinstance(path_or_object, nc.Dataset):
            ds = path_or_object
        else:
            ds = nc.Dataset(path_or_object, mode='w')
            should_close = True

        try:
            ds.createDimension(NetcdfDimension.NODE_COUNT, size=len(self.x))

            if cra:
                from ncsg.cf import ContinuousRaggedArray

                cra_obj = ContinuousRaggedArray.from_vlen(self.cindex, start_index=self.start_index)
                ds.createDimension(NetcdfDimension.GEOMETRY_COUNT, size=len(cra_obj.stops))
                ds.createDimension(NetcdfDimension.CRA_NODE_INDEX, size=len(cra_obj.value))
                cindex = ds.createVariable(NetcdfVariable.COORDINATE_INDEX, DataType.INT,
                                           dimensions=(NetcdfDimension.CRA_NODE_INDEX,))
                stops = ds.createVariable(NetcdfVariable.CRA_STOP, DataType.INT,
                                          dimensions=(NetcdfDimension.GEOMETRY_COUNT,))
            else:
                ds.createDimension(NetcdfDimension.GEOMETRY_COUNT, size=len(self.cindex))
                vltype = ds.createVLType(DataType.INT, DataType.GEOMETRY_VLTYPE)
                cindex = ds.createVariable(NetcdfVariable.COORDINATE_INDEX, vltype,
                                           dimensions=(NetcdfDimension.GEOMETRY_COUNT,))

            if cra:
                cindex_value = cra_obj.value
                stops[:] = cra_obj.stops
                stops.continuous_ragged_dimension = NetcdfDimension.CRA_NODE_INDEX
            else:
                cindex_value = self.cindex
            cindex[:] = cindex_value

            cindex.geom_type = self.geom_type
            coordinates = [NetcdfVariable.X, NetcdfVariable.Y]
            if self.z is not None:
                coordinates.append(NetcdfVariable.Z)
            cindex.coordinates = ' '.join(coordinates)
            if self.multipart_break is not None:
                cindex.multipart_break_value = self.multipart_break
            if 'polygon' in self.geom_type:
                if self.hole_break is not None:
                    cindex.hole_break_value = self.hole_break
                if self.outer_ring_order is not None:
                    setattr(cindex, OuterRingOrder.NAME, self.outer_ring_order)
                setattr(cindex, ClosureConvention.NAME, self.closure_convention)

            x = ds.createVariable(NetcdfVariable.X, DataType.FLOAT, dimensions=(NetcdfDimension.NODE_COUNT,))
            x[:] = self.x

            y = ds.createVariable(NetcdfVariable.Y, DataType.FLOAT, dimensions=(NetcdfDimension.NODE_COUNT,))
            y[:] = self.y

            if self.z is not None:
                z = ds.createVariable(NetcdfVariable.Z, DataType.FLOAT, dimensions=(NetcdfDimension.NODE_COUNT,))
                z[:] = self.z

        finally:
            if should_close:
                ds.close()
