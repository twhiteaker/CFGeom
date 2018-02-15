"""Handles reading netCDF data into geometry containers."""

from netCDF4 import Dataset
import numpy as np

from ... container import GeometryContainer
from ... geometry import Geometry
from ... part import Part
from . nc_constants import (
    Attrs,
    RingType,
    )


def _find_geometry_container_variables(variables):
    """Finds geometry container variables amongst a set of netCDF variables.

    Note:
        A netCDF file may have more than one geometry container variable.

    Args:
        variables (dict(Variable)): The netCDF variables, as in
            nc_dataset.variables.

    Returns:
        list(str): Names of geometry container variables.

    """
    container_names = []
    geom_types = ['point', 'line', 'polygon']
    for var in variables:
        if (Attrs.GEOM_TYPE in var.ncattrs() and
            getattr(var, Attrs.GEOM_TYPE).lower() in geom_types and
            Attrs.NODE_COORDS in var.ncattrs()):
                try:
                    container_names.append(var.name)
                except AttributeError:
                    # Older library version may use _name instead
                    container_names.append(var._name)
    return container_names


def _get_coord_vals(nc_dataset, candidate_names, coord_type):
    """Extracts coordinate values for the given coordinate type.

    Given a coordinate type and a list of candidate variable names, identify
    the variable matching the coordinate type and extract its values.

    Args:
        nc_dataset (netCDF4.Dataset): The netCDF dataset.
        candidate_names (list(str)): Names of candidate variables, one of which
            should match the coordinate type.
        coord_type (str): The coordinate type, Valid values are X, Y, and Z.

    Returns:
        array-like: Coordinate values.

    """
    coord_type = coord_type.upper()
    for name in candidate_names:
        var = nc_dataset.variables[name]
        role = getattr(var, Attrs.AXIS).upper()
        if role == coord_type:
            return var[:]
    return None


def _get_geom_aux_variable(aux_attr, geom_var, nc_dataset):
    """Extracts values for the given variable related to geometry.

    A geometry container variable may have attributes providing names of
    related variables. Not all geometry types require all possible attributes.
    For example, only polygon types may require an interior_ring attribute. 

    Args:
        aux_attr (str): Attribute name to search for on the geometry container.
            should match the coordinate type.
        geom_var (Variable): The netCDF Variable object representing the
            geometry container.
        nc_dataset (netCDF4.Dataset): The netCDF dataset.

    Returns:
        If the geometer container includes the provided attribute, an
        array-like of the related variable's values is returned. Otherwise,
        None is returned.

    """
    var = None
    if aux_attr in geom_var.ncattrs():
        var_name = getattr(geom_var, aux_attr)
        if var_name:
            var = nc_dataset.variables[var_name][:]
    return var


def _is_vlen(geom_var, nc_dataset):
    """Determines if the geometry uses variable length arrays.

    Args:
        geom_var (Variable): The netCDF Variable object representing the
            geometry container.
        nc_dataset (netCDF4.Dataset): The netCDF dataset.

    Returns:
        bool: True if variable length arrays are used, False otherwise.

    """
    coord_var_name = getattr(geom_var, Attrs.NODE_COORDS).split(' ')[0]
    coord_var = nc_dataset.variables[coord_var_name]
    return isinstance(coord_var[0], np.ndarray)


def _geoms_from_cra(geom_type, x_vals, y_vals, z_vals, ring_types, node_counts,
                    part_node_counts):
    """Builds a GeometryContainer from contiguous ragged array netCDF.

    Args:
        geom_type (str): Geometry type. Must be point, line, or polygon.
        x_vals (array-like(float)): X node coordinate values.
        y_vals (array-like(float)): Y node coordinate values.
        z_vals (array-like(float) or None): Z node coordinate values.
        ring_types (array-like(int) or None): Polygon ring types.
        node_counts (array-like(int) or None): Node counts per geometry.
        part_node_counts (array-like(int) or None): Node counts per geometry
            part.

    Returns:
        GeometryContainer: Geometry container with geometries read from netCDF.

    """
    geoms = []
    has_z = z_vals is not None
    is_multipoint = (geom_type == 'point' and node_counts is not None)
    if node_counts is None:
        # Single node per geom. Make list to facilitate looping.
        node_counts = [1] * len(x_vals)
    if part_node_counts is None:
        if is_multipoint:
            # Each part is a single node.
            part_node_counts = [1] * np.sum(node_counts)
        else:
            # No parts. Use node count list to facilitate looping.
            part_node_counts = node_counts[:]
    if ring_types is None:
        # Use default value of outer ring to facilitate looping
        ring_types = [RingType.OUTER] * len(part_node_counts)

    start_node = 0
    part_idx = 0
    for node_count in node_counts:
        parts = []
        node_tally = 0
        while node_tally < node_count:
            part_node_count = part_node_counts[part_idx]
            end_node = start_node + part_node_count
            is_hole = bool(ring_types[part_idx] == RingType.INNER)
            x = x_vals[start_node:end_node]
            y = y_vals[start_node:end_node]
            if has_z:
                z = z_vals[start_node:end_node]
                non_null = z[~np.isnan(z)]
                if len(non_null) == 0:
                    z = None
            else:
                z = None
            parts.append(Part(x, y, z, is_hole))
            start_node = end_node
            node_tally += part_node_count
            part_idx += 1
        geoms.append(Geometry(geom_type, parts))
    return GeometryContainer(geoms)


def _geoms_from_vlen(geom_type, x_vals, y_vals, z_vals, ring_types,
                     part_node_counts, is_multipoint):
    """Builds a GeometryContainer from variable length array netCDF.

    Args:
        geom_type (str): Geometry type. Must be point, line, or polygon.
        x_vals (array-like(float)): X node coordinate values.
        y_vals (array-like(float)): Y node coordinate values.
        z_vals (array-like(float) or None): Z node coordinate values.
        ring_types (array-like(int) or None): Polygon ring types.
        part_node_counts (array-like(int) or None): Node counts per geometry
            part.
        is_multipoint (bool): True if multipoint geometries are present, False
            otherwise.

    Returns:
        GeometryContainer: Geometry container with geometries read from netCDF.

    """
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
        parts = []
        start_idx = 0
        for part_idx, part_node_count in enumerate(part_node_counts[geom_idx]):
            is_hole = bool(ring_types[geom_idx][part_idx] == RingType.INNER)
            end_idx = start_idx + part_node_count
            x = x_arr[start_idx:end_idx]
            y = y_vals[geom_idx][start_idx:end_idx]
            if has_z:
                z = z_vals[geom_idx][start_idx:end_idx]
                non_null = z[~np.isnan(z)]
                if len(non_null) == 0:
                    z = None
            else:
                z = None
            start_idx = end_idx
            parts.append(Part(x, y, z, is_hole))
        geoms.append(Geometry(geom_type, parts))
    return GeometryContainer(geoms)


def read_netcdf(path_or_object, container_name=None):
    """Reads a netCDF file into geometry containers.

    Args:
        path_or_object (str or netCDF4.Dataset): Input netCDF file or object.
        container_name (str): Name of the geometry container variable to
            extract from the file.

    Returns:
        Dictionary with one item for each geometry container found within the
        file, or a single item if a container_name was provided. The dictionary
        is keyed by geometry container variable and has this structure::

            {
                'A_Geometry_Container_Variable_Name': {
                    'container': GeometryContainer instance},
                'Another_Geometry_Container_Variable_Name': {
                    'container': GeometryContainer instance}
            }

    Raises:
        ValueError: If geometry container with the provided name was not found.

    Todo:
        * Return NcNames in the dictionary for each container.
    """
    should_close = False
    if isinstance(path_or_object, Dataset):
        ds = path_or_object
    else:
        ds = Dataset(path_or_object)
        should_close = True

    try:
        pass
        if container_name is None:
            target = _find_geometry_container_variables(ds.variables.values())
            if len(target) == 0:
                raise ValueError('No geometry container variable found')
        else:
            if isinstance(container_name, str):
                target = [container_name]
            else:
                target = container_name

        containers = {}
        for geom_var_name in target:
            geom_var = ds.variables[geom_var_name]
            geom_type = getattr(geom_var, Attrs.GEOM_TYPE).lower()
            coordinates = getattr(geom_var, Attrs.NODE_COORDS).split(' ')
            x = _get_coord_vals(ds, coordinates, Attrs.GEOM_X_NODE)
            y = _get_coord_vals(ds, coordinates, Attrs.GEOM_Y_NODE)
            z = _get_coord_vals(ds, coordinates, Attrs.GEOM_Z_NODE)
            ring_types = _get_geom_aux_variable(Attrs.RING_TYPE, geom_var, ds)
            node_counts = _get_geom_aux_variable(Attrs.NODE_COUNT, geom_var, ds)
            part_node_counts = _get_geom_aux_variable(Attrs.PART_NODE_COUNT, geom_var, ds)

            if _is_vlen(geom_var, ds):
                is_multipoint = (geom_type == 'point')  # single point doesn't use vlen
                container = _geoms_from_vlen(
                    geom_type, x, y, z, ring_types, part_node_counts, is_multipoint)
            else:
                container = _geoms_from_cra(
                    geom_type, x, y, z, ring_types, node_counts, part_node_counts)
            containers[geom_var_name] = {'container': container}
        return containers
    finally:
        if should_close:
            ds.close()


