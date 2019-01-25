"""Handles writing data to netCDF format."""

from netCDF4 import Dataset
import numpy as np

from . nc_names import NcNames
from . nc_constants import (
    Attrs,
    RingType,
    )


def _to_cra_arrays(geom_container):
    """Exports contiguous ragged arrays from a geometry container.

    Args:
        geom_container (GeometryContainer): The geometry container.

    Returns:
        Tuple of one-dimensional arrays representing:
            x coordinates
            y coordinates
            z coordinates
            node counts per geometry
            node counts per geometry part
            ring type for each geometry part

    """
    x = []
    y = []
    ring_type = []
    node_count = []
    part_node_count = []
    has_z = geom_container.has_z()
    z = [] if has_z else None

    for geom in geom_container.geoms:
        node_counter = 0
        for part in geom.parts:
            x.extend(part.x)
            y.extend(part.y)
            if has_z:
                if not len(part.z):
                    z.extend(len(part.x) * [None])
                else:
                    z.extend(part.z)
            ring = RingType.INNER if part.is_hole else RingType.OUTER
            ring_type.append(ring)
            count_of_nodes_in_part = len(part.x)
            part_node_count.append(count_of_nodes_in_part)
            node_counter += count_of_nodes_in_part
        node_count.append(node_counter)

    x = np.array(x, dtype=np.float64)  # Converts None to nan
    y = np.array(y, dtype=np.float64)
    if has_z:
        z = np.array(z, dtype=np.float64)
    return (x, y, z, node_count, part_node_count, ring_type)


def _to_vlen_arrays(geom_container):
    """Exports variable length arrays from a geometry container.

    Args:
        geom_container (GeometryContainer): The geometry container.

    Returns:
        Tuple of arrays representing:
            x coordinates
            y coordinates
            z coordinates
            node counts per geometry part
            ring type for each geometry part

        The elements of each array may have variable length. For example,
        for a multiline geometry with two parts, x values could be::
        
            x = [[1, 2, 3, 4],
                 [9, 8, 7, 6]]

        If no z values are found, None is returned for the z array.

    """
    geom_cnt = len(geom_container.geoms)
    x = np.zeros(geom_cnt, dtype=object)
    y = np.zeros(geom_cnt, dtype=object)
    ring_type = np.zeros(geom_cnt, dtype=object)
    part_node_count = np.zeros(geom_cnt, dtype=object)
    has_z = geom_container.has_z()
    z = np.zeros(geom_cnt, dtype=object) if has_z else None

    for idx, geom in enumerate(geom_container.geoms):
        x_geom = []
        y_geom = []
        ring_type_geom = []
        part_node_count_geom = []
        z_geom = [] if has_z else None
        
        for part in geom.parts:
            x_geom.extend(part.x)
            y_geom.extend(part.y)
            if has_z:
                if not len(part.z):
                    z_geom.extend(len(part.x) * [None])
                else:
                    z_geom.extend(part.z)
            ring = RingType.INNER if part.is_hole else RingType.OUTER
            ring_type_geom.append(ring)
            count_of_nodes_in_part = len(part.x)
            part_node_count_geom.append(count_of_nodes_in_part)

        x[idx] = np.array(x_geom, dtype=np.float64)
        y[idx] = np.array(y_geom, dtype=np.float64)
        if has_z:
            z[idx] = np.array(z_geom, dtype=np.float64)
        ring_type[idx] = np.array(ring_type_geom, dtype=np.int_)
        part_node_count[idx] = np.array(part_node_count_geom, dtype=np.int_)

    return (x, y, z, part_node_count, ring_type)


def _make_vltype(dataset, base_type, type_name):
    """Creates a variable length data type in the netCDF file.

    Creates a variable length data type in the netCDF file. If a compatible
    data type of the same name already exists, it is returned.

    Args:
        dataset (netCDF4.Dataset): The netCDF file object.
        base_type (numpy.dtype): The base data type for the VLType.
        type_name (str): The name for the VLType.

    Returns:
        VLType: The VLType class instance describing the datatype.

    Raises:
        ValueError: If input netCDF file doesn't use a data model supporting
            VLTypes, or if the VLType already exists but is of a different
            base type than what was provided.

    """
    if dataset.data_model != 'NETCDF4':
        raise ValueError('Input netCDF dataset must use NETCDF4 data model to '
                         'support VLEN types. Current data model: {}'.format(
                             dataset.data_model))
    if type_name not in dataset.vltypes:
        vltype = dataset.createVLType(base_type, type_name)
    else:
        vltype = dataset.vltypes[type_name]
        if vltype.dtype != base_type:
            m = ('{0} VLType exists in netCDF file but is not of '
                 'the correct data type. Existing data type: {1}. '
                 'Expected data type: {2}.')
            m = m.format(str(vltype.dtype), str(base_type))
            raise ValueError(m)
    return vltype


def _make_dim(dataset, name, length):
    """Creates a dimension in the netCDF file.

    Creates a dimension in the netCDF file. If a dimension of the same name
    with the same length already exists, it is returned.

    Args:
        dataset (netCDF4.Dataset): The netCDF file object.
        name (str): The name for the dimension.
        length (int): The length for the dimension.

    Returns:
        Dimension: Dimension class instance describing the dimension.

    Raises:
        ValueError: If the dimension already exists but is of a different
            length than what was provided.

    """
    if name not in dataset.dimensions:
        dim = dataset.createDimension(name, length)
    else:
        dim = dataset.dimensions[name]
        if len(dim) != length:
            m = ('{0} dimension exists in netCDF file but is not of '
                 'the correct length.  Dimension length: {1}. Expected '
                 'length: {2}.').format(name, len(dim), length)
            raise ValueError(m)
    return dim


def _make_var(dataset, name, dtype, dim_tuple=None):
    """Creates a variable in the netCDF file.

    Args:
        dataset (netCDF4.Dataset): The netCDF file object.
        name (str): The name for the variable.
        dtype (numpy.dtype): The data type for the variable.
        dim_tuple (tuple(str), optional): Tuple of dimension names to use for
            the variable. Leave as None for scalar variables.

    Returns:
        Variable: Variable class instance describing the new variable.

    Raises:
        ValueError: If the variable already exists in the file.

    """
    if dim_tuple is None:
        dim_tuple = ()
    if name not in dataset.variables:
        var = dataset.createVariable(name, dtype, dim_tuple)
    else:
        m = '{0} variable already exists in netCDF file'.format(name)
        raise ValueError(m)
    return var


def _set_attr(owner, name, value):
    """Sets an attribute value for a netCDF file or variable.

    Args:
        owner (Dataset or Variable): The netCDF file or variable.
        name (str): The name for the attribute.
        value (object): The value for the attribute.

    Raises:
        ValueError: If the attribute already exists and has a value different
        than what was provided.

    """
    if name not in owner.ncattrs():
        setattr(owner, name, value)
    else:
        attr = getattr(owner, name)
        if attr != value:
            m = ('{0} attribute of {1} already exists and has a '
                 'different value than expected. Existing value: {2}. '
                 'Expected value: {3}.')
            m = m.format(name, owner.name, attr, value)
            raise ValueError(m)


def write_netcdf(geom_container, path_or_object, nc_names=None, use_vlen=False):
    """Exports a geometry container to a CF-compliant netCDF file.

    Args:
        geom_container (GeometryContainer): Geometry container object.
        path_or_object (str or netCDF4.Dataset): Target netCDF file
            or object.  If the file exists, it is overwritten. Pass a
            netCDF4.Dataset object to append to an existing file.
        nc_names (nc_names.NcNames, optional): Object specifying names for
            types, dimensions, and variables to use in the netCDF file.
        use_vlen (bool, optional): True if variable length (VLEN) arrays from
            the netCDF enhanced model should be used for variables such as node
            coordinate arrays, False otherwise.

    """
    if nc_names is None:
        nc_names = NcNames()
    if geom_container.geom_type == 'polygon':
        geom_container.orient()  # Set anticlockwise vs clockwise node order

    if use_vlen:
        x, y, z, part_node_count, ring_type = _to_vlen_arrays(geom_container)
    else:
        x, y, z, node_count, part_node_count, ring_type = _to_cra_arrays(geom_container)

    has_holes = geom_container.has_hole()
    geom_subtype = geom_container.wkt_type().lower()
    has_multinode_parts = (geom_subtype in ['multilinestring', 'multipolygon'] or
                           has_holes)

    should_close = False
    if isinstance(path_or_object, Dataset):
        ds = path_or_object
    else:
        ds = Dataset(path_or_object, mode='w')
        should_close = True

    try:
        _set_attr(ds, Attrs.CONVENTIONS, nc_names.conventions)

        # Dimensions and Types
        _make_dim(ds, nc_names.instance_dim, len(geom_container.geoms))

        if use_vlen:
            if geom_subtype != 'point':
                node_type = _make_vltype(ds, np.float64, nc_names.node_vltype)
            else:
                node_type = np.float64
            if has_multinode_parts:
                part_node_type = _make_vltype(ds, np.int_, nc_names.part_node_vltype)
            node_dim = nc_names.instance_dim
            part_node_count_dim = nc_names.instance_dim
        else:
            node_type = np.float64
            part_node_type = np.int_
            if geom_subtype != 'point':
                node_dim = nc_names.node_dim
                _make_dim(ds, node_dim, len(x))
            else:
                node_dim = nc_names.instance_dim
            if has_multinode_parts:
                part_node_count_dim = nc_names.part_dim
                _make_dim(ds, part_node_count_dim, len(part_node_count))

        # Variables
        v_container = _make_var(ds, nc_names.container_var, np.int_)
        _set_attr(v_container, Attrs.GEOM_TYPE, geom_container.geom_type)
        node_coords = nc_names.x_var + ' ' + nc_names.y_var
        if z is not None:
            node_coords += ' ' + nc_names.z_var
        _set_attr(v_container, Attrs.NODE_COORDS, node_coords)

        v_x = _make_var(ds, nc_names.x_var, node_type, (node_dim,))
        _set_attr(v_x, Attrs.AXIS, Attrs.GEOM_X_NODE)
        v_x[:] = x

        v_y = _make_var(ds, nc_names.y_var, node_type, (node_dim,))
        _set_attr(v_y, Attrs.AXIS, Attrs.GEOM_Y_NODE)
        v_y[:] = y

        if z is not None:
            v_z = _make_var(ds, nc_names.z_var, node_type, (node_dim,))
            _set_attr(v_z, Attrs.AXIS, Attrs.GEOM_Z_NODE)
            v_z[:] = z

        if (not use_vlen) and geom_subtype != 'point':
            v_node_count = _make_var(
                ds, nc_names.node_count_var, np.int_, (nc_names.instance_dim,))
            _set_attr(v_node_count, Attrs.LONG_NAME, Attrs.NODE_COUNT_LONG_NAME)
            v_node_count[:] = node_count
            _set_attr(v_container, Attrs.NODE_COUNT, nc_names.node_count_var)

        if has_multinode_parts:
            v_part_node_count = _make_var(
                ds, nc_names.part_node_count_var, part_node_type, (part_node_count_dim,))
            _set_attr(v_part_node_count, Attrs.LONG_NAME,
                      Attrs.PART_NODE_COUNT_LONG_NAME)
            v_part_node_count[:] = part_node_count
            _set_attr(v_container, Attrs.PART_NODE_COUNT, nc_names.part_node_count_var)

        if has_holes:
            v_ring_type = _make_var(
                ds, nc_names.ring_var, part_node_type, (part_node_count_dim,))
            _set_attr(v_ring_type, Attrs.LONG_NAME, Attrs.RING_TYPE_LONG_NAME)
            v_ring_type[:] = ring_type
            _set_attr(v_container, Attrs.RING_TYPE, nc_names.ring_var)
    finally:
        if should_close:
            ds.close()


