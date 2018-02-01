from copy import deepcopy

import netCDF4 as nc
import numpy as np
from _pytest.assertion.util import basestring
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry
from shapely.geometry.polygon import orient

from ncsg.constants import (
    NCSG_GEOM_OBJECT_MAP,
    RingType,
    GeneralAttributes,
    )
from ncsg.exc import NoGeometryContainerVariablesFoundError
from ncsg.geometry.base import CFGeometryCollection


def from_shapely(geom_type, geoms, string_id=None):
    """
    Create a CF geometry collection from a sequence of geometries.

    :param str geom_type: The destination geometry type. Valid values are
    ``"point"``, ``"line"``, ``"polygon"``.
    :param sequence geoms: A sequence of geometry objects to convert.
    :return: :class:`~ncsg.CFGeometryCollection`
    """

    geom_type = geom_type.lower()
    geom_type = geom_type.replace('string', '')  # We use line instead of linestring

    # Allow a singleton geometry object to be passed.
    if isinstance(geoms, BaseGeometry):
        geoms = [geoms]

    # Holds each CF geometry.
    cf_geoms = []
    # May hold z coordinate values.
    has_z = False

    # Convert each geometry to its coordinate representation.
    for ctr_geom, geom in enumerate(geoms):
        # Holds geometry parts
        cf_parts = []
        # Allows us to iterate over single-part and multi-part geometries.
        for ctr_part, part in enumerate(_get_geometry_iter_(geom)):
            cf_part = {'ring_type': RingType.OUTER}
            if ctr_part == 0 and ctr_geom == 0 and part.has_z:
                has_z = True

            # Get the geometry nodes' coordinates.
            if 'polygon' in geom_type:
                exterior = part.exterior
                # Always orient the polygon CCW.
                if not exterior.is_ccw:
                    exterior = orient(part).exterior
                coords = np.array(exterior.coords)
            else:
                coords = np.array(part)

            # Add this geometry's coordinates to coordinate containers.
            cf_part['x'] = _get_coordinates_as_list_(coords, 0)
            cf_part['y'] = _get_coordinates_as_list_(coords, 1)
            if has_z:
                cf_part['z'] = _get_coordinates_as_list_(coords, 2)
            else:
                cf_part['z'] = None
            cf_parts.append(cf_part)
            
            # Check for polygon interiors.
            try:
                # Add interiors/holes if the polygon objects contains them.
                if len(part.interiors) > 0:
                    for ii in part.interiors:
                        cf_part = {'ring_type': RingType.INNER}
                        # Always orient holes CW.
                        if ii.is_ccw:
                            ii = orient(Polygon(ii), sign=-1.0).exterior
                        # Add interior's coordinates to coordinate containers.
                        coords = np.array(ii)
                        cf_part['x'] = coords[:, 0].tolist()
                        cf_part['y'] = coords[:, 1].tolist()
                        if has_z:
                            cf_part['z'] = coords[:, 2].tolist()
                        else:
                            cf_part['z'] = None
                        cf_parts.append(cf_part)
            except AttributeError:
                # If this is not a polygon, we are not worried about interiors.
                if 'polygon' in geom_type:
                    raise
        cf_geoms.append(cf_parts)

    return CFGeometryCollection(geom_type, cf_geoms, string_id)


def to_shapely(geom_type, cf_geom):
    """
    Load a Shapely geometry object from its CF representation.

    :param geom_type: The destination geometry type. Valid values are ``"point"``, ``"line"``, ``"polygon"``, and
     multipart types `"multipoint"``, ``"multiline"``, ``"multipolygon"``.
    :type geom_type: str
    :param cf_geom: A list of CF geometry parts for a single geometry. Each item in
     the list is a dictionary with one-dimensional coordinate arrays ``x``,
     ``y``, and optionally ``z``. and an integer ``ring_type``.
    :type cf_geom: List
    :return: The Shapely object representing the geometry.
    :rtype: :class:`shapely.geometry.base.BaseGeometry`
    :raises: ValueError
    """

    geom_type = geom_type.lower()
    shapely_type = NCSG_GEOM_OBJECT_MAP[geom_type]

    if 'polygon' in geom_type:
        single_type = NCSG_GEOM_OBJECT_MAP['polygon']
        holes = []
        polygons = []
        exterior = None
        for part in cf_geom:
            part_coords = _extract_geom_part_coordinates(part)
            if 'ring_type' in part and part['ring_type'] == RingType.INNER:
                holes.append(part_coords)
            elif exterior is not None:
                # New exterior. Finish previous polygon.
                polygon = single_type(exterior, holes)
                polygons.append(polygon)
                # Start new polygon
                holes = []
                exterior = part_coords
            else:
                exterior = part_coords
        # Finish last polygon
        polygon = single_type(exterior, holes)
        polygons.append(polygon)
        # Create final geometry
        if geom_type.startswith('multi'):
            ret = shapely_type(polygons)
        else:
            ret = polygons[0]
    else:
        coords = [_extract_geom_part_coordinates(part) for part in cf_geom]
        if len(coords) == 1 and not geom_type.startswith('multi'):
            coords = coords[0]
        ret = shapely_type(coords)
        
    return ret


def _extract_geom_part_coordinates(part):
    coords = []
    x_vals = part['x']
    y_vals = part['y']
    if 'z' in part:
        z_vals = part['z']
    else:
        z_vals = None
    for idx, x in enumerate(x_vals):
        if z_vals is not None and z_vals[idx] is not None:
            coord = (x, y_vals[idx], z_vals[idx])
        else:
            coord = (x, y_vals[idx])
        coords.append(coord)
    if len(coords) == 1:
        coords = coords[0]
    return coords

    
def _get_geometry_iter_(geom):
    if isinstance(geom, BaseMultipartGeometry):
        ret = geom
    else:
        ret = [geom]
    return ret


def _get_coordinates_as_list_(coords, column_index):
    try:
        ret = coords[:, column_index].tolist()
    except IndexError:
        if coords.ndim == 1:
            coords = coords.reshape(-1, coords.shape[0])
            ret = _get_coordinates_as_list_(coords, column_index)
        else:
            raise
    return ret


def loads_from_netcdf(path_or_object, target=None):
    should_close = False
    if isinstance(path_or_object, nc.Dataset):
        ds = path_or_object
    else:
        ds = nc.Dataset(path_or_object)
        should_close = True

    try:
        if target is None:
            target = _find_geometry_container_variables_(ds.variables.values())
            if len(target) == 0:
                raise NoGeometryContainerVariablesFoundError
        else:
            if isinstance(target, basestring):
                target = [target]

        ret = []
        for geom_var_name in target:
            geom_var = ds.variables[geom_var_name]
            geom_type = getattr(geom_var, GeneralAttributes.GEOM_TYPE_NAME)
            coordinates = getattr(geom_var, GeneralAttributes.COORDINATES).split(' ')
            x = _get_coord_vals_(ds, coordinates, GeneralAttributes.GEOM_X_NODE)
            y = _get_coord_vals_(ds, coordinates, GeneralAttributes.GEOM_Y_NODE)
            z = _get_coord_vals_(ds, coordinates, GeneralAttributes.GEOM_Z_NODE)
            ring_types = _get_geom_aux_variable_(GeneralAttributes.RING_TYPE, geom_var, ds)
            node_counts = _get_geom_aux_variable_(GeneralAttributes.NODE_COUNT, geom_var, ds)
            part_node_counts = _get_geom_aux_variable_(GeneralAttributes.PART_NODE_COUNT, geom_var, ds)

            if _is_vlen_(geom_var, ds):
                is_multipoint = geom_type == 'multipoint'
                geoms = _geoms_from_vlen_(x, y, z, ring_types, part_node_counts, is_multipoint)
            else:
                geoms = _geoms_from_cra_(x, y, z, ring_types, node_counts, part_node_counts)
            gc = CFGeometryCollection(geom_type, geoms)
            ret.append(gc)
        return tuple(ret)
    finally:
        if should_close:
            ds.close()


def _find_geometry_container_variables_(variables):
    ret = []
    for var in variables:
        if (GeneralAttributes.GEOM_TYPE_NAME in var.ncattrs() and
            getattr(var, GeneralAttributes.GEOM_TYPE_NAME) in NCSG_GEOM_OBJECT_MAP and
            GeneralAttributes.COORDINATES in var.ncattrs()):
                try:
                    ret.append(var.name)
                except AttributeError:
                    ret.append(var._name)  # For older netCDF4 modules?
    return ret


def _is_vlen_(geom_var, nc_dataset):
    coord_var_name = getattr(geom_var, GeneralAttributes.COORDINATES).split(' ')[0]
    coord_var = nc_dataset.variables[coord_var_name]
    return isinstance(coord_var[0], np.ndarray)


def _get_coord_vals_(nc_dataset, candidate_names, coord_type):
    for name in candidate_names:
        var = nc_dataset.variables[name]
        role = getattr(var, GeneralAttributes.CF_ROLE_NAME)
        if role == coord_type:
            return var[:]
    return None


def _get_geom_aux_variable_(aux_attr, geom_var, nc_dataset):
    var = None
    if aux_attr in geom_var.ncattrs():
        var_name = getattr(geom_var, aux_attr)
        if var_name:
            var = nc_dataset.variables[var_name][:]
    return var


def _geoms_from_cra_(x_vals, y_vals, z_vals, ring_types, node_counts, part_node_counts):
    geoms = []
    has_z = z_vals is not None
    if node_counts is None:
        # Single node per geom. Make list to facilitate looping.
        node_counts = [1] * len(x_vals)
    if part_node_counts is None:
        # No parts. Use node count list to facilitate looping.
        part_node_counts = node_counts[:]
    if ring_types is None:
        # Use default value of outer ring to facilitate looping
        ring_types = [RingType.OUTER] * len(part_node_counts)

    start_node = 0
    part_idx = 0
    for node_count in node_counts:
        geom = []
        node_tally = 0
        while node_tally < node_count:
            part_node_count = part_node_counts[part_idx]
            end_node = start_node + part_node_count
            part = {'ring_type': ring_types[part_idx]}
            part['x'] = x_vals[start_node:end_node]
            part['y'] = y_vals[start_node:end_node]
            if has_z:
                part['z'] = z_vals[start_node:end_node]
            else:
                part['z'] = None
            geom.append(part)
            start_node = end_node
            node_tally += part_node_count
            part_idx += 1
        geoms.append(geom)
    return geoms


def _geoms_from_vlen_(x_vals, y_vals, z_vals, ring_types, part_node_counts, is_multipoint):
    geoms = []
    has_z = z_vals is not None
    if part_node_counts is None:
        # No parts. Make list to facilitate looping.
        if is_multipoint:
            part_node_counts = [[1] * len(x_per_geom) for x_per_geom in x_vals]
        else:
            part_node_counts = [[len(x_per_geom)] for x_per_geom in x_vals]
    if ring_types is None:
        # Use default value of outer ring to facilitate looping
        ring_types = [[RingType.OUTER] * len(c) for c in part_node_counts]
    
    for geom_idx, x_arr in enumerate(x_vals):
        geom = []
        start_idx = 0
        for part_idx, part_node_count in enumerate(part_node_counts[geom_idx]):
            part = {'ring_type': ring_types[geom_idx][part_idx]}
            end_idx = start_idx + part_node_count
            part['x'] = x_arr[start_idx:end_idx]
            part['y'] = y_vals[geom_idx][start_idx:end_idx]
            if has_z:
                part['z'] = z_vals[geom_idx][start_idx:end_idx]
            else:
                part['z'] = None
            start_idx = end_idx
            geom.append(part)
        geoms.append(geom)
    return geoms
