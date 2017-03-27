import os
import subprocess
import tempfile
from abc import ABCMeta

import netCDF4 as nc
import numpy as np

from ncsg.base import AbstractNCSGObject
from ncsg.constants import (
    DataType,
    GeneralAttributes,
    NetcdfDimension,
    NetcdfVariable,
    RingType,
    )


class CFGeometryCollection(AbstractNCSGObject):
    """
    A collection of CF geometries.
    """
    # TODO: Docstring and commenting
    __metaclass__ = ABCMeta


    def __init__(self, geom_type, geom_list, string_id=None):
        geom_type = geom_type.lower()

        if string_id is None:
            string_id = ''
        self.string_id = string_id
        self.geom_type = geom_type
        self.geoms = geom_list
        self.cf_names = {'variables': {'geometry_container': '{}{}'.format(string_id, NetcdfVariable.GEOMETRY_CONTAINER),
                                       'node_count': '{}{}'.format(string_id, NetcdfVariable.NODE_COUNT),
                                       'part_node_count': '{}{}'.format(string_id, NetcdfVariable.PART_NODE_COUNT),
                                       'x': '{}{}'.format(string_id, NetcdfVariable.X),
                                       'y': '{}{}'.format(string_id, NetcdfVariable.Y),
                                       'z': '{}{}'.format(string_id, NetcdfVariable.Z),
                                       'polygon_ring_type': '{}{}'.format(string_id, NetcdfVariable.RING_TYPE)},
                         'dimensions': {'geometry_count': '{}{}'.format(string_id, NetcdfDimension.GEOMETRY_COUNT),
                                        'node_count': '{}{}'.format(string_id, NetcdfDimension.NODE_COUNT),
                                        'part_count': '{}{}'.format(string_id, NetcdfDimension.PART_COUNT)}}
        for geom in self.geoms:
            for part in geom:                
                assert len(part['x']) == len(part['y'])
                if 'z' in part and part['z'] is not None:
                    assert len(part['z']) == len(part['x'])


    def __eq__(self, other):
        ret = True
        for k, v in self.__dict__.items():
            ov = other.__dict__[k]
            try:
                if k == GeneralAttributes.GEOM_TYPE_NAME:
                    if v.lower() != ov.lower():
                        raise AssertionError('Geometry types are not equal.')
                elif k == 'geoms':
                    for geom_idx, geom in enumerate(v):
                        o_geom = ov[geom_idx]
                        for part_idx, part in enumerate(geom):
                            o_part = o_geom[part_idx]
                            _assert_array_equal_(part['x'], o_part['x'])
                            _assert_array_equal_(part['y'], o_part['y'])
                            _assert_array_equal_(part['z'], o_part['z'])
                            if part['ring_type'] != o_part['ring_type']:
                                raise AssertionError('Ring types are not equal.')
                else:
                    if v != ov:
                        raise AssertionError('"{}" are not equal.'.format(k))
            except AssertionError as _:
                ret = False
        return ret


    def as_shapely(self):
        from ncsg import cf
        ret = [cf.to_shapely(self.geom_type, g) for g in self.geoms]
        return tuple(ret)


    def describe(self, cra=False, header=True, capture=False):
        path = os.path.join(tempfile.gettempdir(), '_ncsg_describe_.nc')
        self.write_netcdf(path, cra=cra)
        ret = None
        shell = os.name == 'nt'  # Use shell=True for commands on Windows
        try:
            cmd = ['ncdump']
            if header:
                cmd.append('-h')
            cmd.append(path)
            if capture:
                ret = str(subprocess.check_output(cmd, shell=shell))
            else:
                subprocess.check_call(cmd, shell=shell)
        finally:
            os.remove(path)
        return ret


    def write_netcdf(self, path_or_object, cra=False):
        dname_geom_count = self.cf_names['dimensions']['geometry_count']
        dname_node_count = self.cf_names['dimensions']['node_count']
        dname_part_count = self.cf_names['dimensions']['part_count']
        vname_x = self.cf_names['variables']['x']
        vname_y = self.cf_names['variables']['y']
        vname_z = self.cf_names['variables']['z']
        vname_container = self.cf_names['variables']['geometry_container']
        vname_node_count = self.cf_names['variables']['node_count']
        vname_part_node_count = self.cf_names['variables']['part_node_count']
        vname_ring_type = self.cf_names['variables']['polygon_ring_type']
        string_id = self.string_id

        if cra:
            x, y, z, node_count, part_node_count, ring_type = self.export_cra_arrays()
        else:
            x, y, z, part_node_count, ring_type = self.export_vlen_arrays()
        has_holes = self.has_holes()
        geom_type = self.geom_type
        has_multinode_parts = (geom_type in ['multiline', 'multipolygon'] or
                               has_holes)

        should_close = False
        if isinstance(path_or_object, nc.Dataset):
            ds = path_or_object
        else:
            ds = nc.Dataset(path_or_object, mode='w')
            should_close = True

        try:
            setattr(ds, GeneralAttributes.CONVENTIONS, GeneralAttributes.CONVENTIONS_VALUE)

            # Dimensions
            ds.createDimension(dname_geom_count, len(self.geoms))
            if cra:
                node_type = DataType.FLOAT
                part_node_count_dim = dname_part_count
                part_node_type = DataType.INT
                if geom_type != 'point':
                    ds.createDimension(dname_node_count, len(x))
                    node_dim = dname_node_count
                else:
                    node_dim = dname_geom_count
                if has_multinode_parts:
                    ds.createDimension(dname_part_count, len(part_node_count))
            else:
                node_dim = dname_geom_count
                part_node_count_dim = dname_geom_count
                if geom_type != 'point':
                    node_type = _make_vltype_(ds, DataType.FLOAT, DataType.NODE_VLTYPE)
                else:
                    node_type = DataType.FLOAT
                if has_multinode_parts:
                    part_node_type = _make_vltype_(ds, DataType.INT, DataType.PART_NODES_VLTYPE)

            # Variables
            v_container = ds.createVariable(vname_container, DataType.INT)
            setattr(v_container, GeneralAttributes.GEOM_TYPE_NAME, geom_type)
            if z is None:
                node_coords = vname_x + ' ' + vname_y
            else:
                node_coords = vname_x + ' ' + vname_y + ' ' + vname_z
            setattr(v_container, GeneralAttributes.COORDINATES, node_coords)

            v_x = ds.createVariable(vname_x, node_type, (node_dim,))
            setattr(v_x, GeneralAttributes.CF_ROLE_NAME, GeneralAttributes.GEOM_X_NODE)
            v_x[:] = x

            v_y = ds.createVariable(vname_y, node_type, (node_dim,))
            setattr(v_y, GeneralAttributes.CF_ROLE_NAME, GeneralAttributes.GEOM_Y_NODE)
            v_y[:] = y

            if z is not None:
                v_z = ds.createVariable(vname_z, node_type, (node_dim,))
                setattr(v_z, GeneralAttributes.CF_ROLE_NAME, GeneralAttributes.GEOM_Z_NODE)
                v_z[:] = z

            if cra and geom_type != 'point':
                v_node_count = ds.createVariable(vname_node_count, DataType.INT, (dname_geom_count,))
                setattr(v_node_count, GeneralAttributes.LONG_NAME, GeneralAttributes.NODE_COUNT_LONG_NAME)
                v_node_count[:] = node_count
                setattr(v_container, GeneralAttributes.NODE_COUNT, vname_node_count)

            if has_multinode_parts:
                v_part_node_count = ds.createVariable(vname_part_node_count, part_node_type, (part_node_count_dim,))
                setattr(v_part_node_count, GeneralAttributes.LONG_NAME, GeneralAttributes.PART_NODE_COUNT_LONG_NAME)
                v_part_node_count[:] = part_node_count
                setattr(v_container, GeneralAttributes.PART_NODE_COUNT, vname_part_node_count)

            if has_holes:
                v_ring_type = ds.createVariable(vname_ring_type, part_node_type, (part_node_count_dim,))
                setattr(v_ring_type, GeneralAttributes.LONG_NAME, GeneralAttributes.RING_TYPE_LONG_NAME)
                v_ring_type[:] = ring_type
                setattr(v_container, GeneralAttributes.RING_TYPE, vname_ring_type)
        finally:
            if should_close:
                ds.close()


    def export_cra_arrays(self):
        from ncsg.cf import from_shapely, to_shapely
        x = []
        y = []
        ring_type = []
        node_count = []
        part_node_count = []
        has_z = self.has_z()
        if has_z:
            z = []
        else:
            z = None

        for geom in self.geoms:
            # Use Shapely to enforce anticlockwise exterior rings and
            # first-last node equivalence.
            shapely_geom = to_shapely(self.geom_type, geom)
            geom = from_shapely(self.geom_type, shapely_geom).geoms[0]
            
            node_counter = 0
            for part in geom:
                x.extend(part['x'])
                y.extend(part['y'])
                if has_z:
                    z.extend(part['z'])
                ring_type.append(part['ring_type'])
                part_node_count.append(len(part['x']))
                node_counter += part_node_count[-1]
            node_count.append(node_counter)

        return (x, y, z, node_count, part_node_count, ring_type)


    def export_vlen_arrays(self):
        from ncsg.cf import from_shapely, to_shapely
        geom_cnt = len(self.geoms)
        x = np.zeros(geom_cnt, dtype=object)
        y = np.zeros(geom_cnt, dtype=object)
        ring_type = np.zeros(geom_cnt, dtype=object)
        part_node_count = np.zeros(geom_cnt, dtype=object)
        has_z = self.has_z()
        if has_z:
            z = np.zeros(geom_cnt, dtype=object)
        else:
            z = None

        for idx, geom in enumerate(self.geoms):
            # Use Shapely to enforce anticlockwise exterior rings and
            # first-last node equivalence.
            shapely_geom = to_shapely(self.geom_type, geom)
            geom = from_shapely(self.geom_type, shapely_geom).geoms[0]
            
            x_geom = []
            y_geom = []
            ring_type_geom = []
            part_node_count_geom = []
            if has_z:
                z_geom = []
            else:
                z_geom = None
            
            for part in geom:
                x_geom.extend(part['x'])
                y_geom.extend(part['y'])
                if has_z:
                    z_geom.extend(part['z'])
                ring_type_geom.append(part['ring_type'])
                part_node_count_geom.append(len(part['x']))

            x[idx] = np.array(x_geom, dtype=DataType.FLOAT)
            y[idx] = np.array(y_geom, dtype=DataType.FLOAT)
            if has_z:
                z[idx] = np.array(z_geom, dtype=DataType.FLOAT)
            ring_type[idx] = np.array(ring_type_geom, dtype=DataType.INT)
            part_node_count[idx] = np.array(part_node_count_geom, dtype=DataType.INT)

        return (x, y, z, part_node_count, ring_type)


    def has_holes(self):
        ret = False
        if 'polygon' in self.geom_type:
            for geom in self.geoms:
                for part in geom:
                    if part['ring_type'] == RingType.INNER:
                        ret = True
                        break
        return ret


    def has_z(self):
        # TODO: possible that only some z values are NULL?
        try:
            return self.geoms[0][0]['z'] is not None
        except:
            return False


def _make_vltype_(nc_dataset, base_type, type_name):
    try:
        vltype = nc_dataset.createVLType(base_type, type_name)
    except RuntimeError:
        # Type is likely already created. Try to access it.
        vltype = nc_dataset.vltypes[type_name]
    return vltype


def _assert_array_equal_(actual, desired):
    actual = np.array(actual)
    desired = np.array(desired)
    if actual.dtype != desired.dtype:
        raise AssertionError('Data types are not equal.')
    cmp = actual == desired
    if not cmp.all():
        raise AssertionError('Not all values are equal.')
