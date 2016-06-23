from copy import deepcopy

import numpy as np
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry

from ncsg.constants import NCSG_GEOM_OBJECT_MAP, BreakValue
from ncsg.geometry.base import CFGeometryCollection


def dumps(geom_type, geoms, start_index=0, multipart_break=BreakValue.MULTIPART, hole_break=BreakValue.HOLE):
    """
    Create a CF geometry collection from a sequence of geometries.

    :param str geom_type: The destination geometry type. Valid values are ``"point"``,
     ``"linestring"``, ``"polygon"``, and multipart types `"multipoint"``, ``"multilinestring"``, ``"multipolygon"``.
    :param sequence geoms: A sequence of geometry objects to convert.
    :param int start_index: The starting index value. The default is Python zero-based indexing. Valid values are ``0``
     or ``1``.
    :param int multipart_break: A break value indicating a multipart geometry split. Must be a negative integer value.
     If ``None``, there will be no attempt to search for multipart splits.
    :param int hole_break: A break value indicating a hole in the previous polygon. Setting to ``None`` tells the
     function to not search for holes. Must be a negative integer value. This argument is valid only when decoding
     polygon geometry objects. All holes (interiors) must be placed after the coordinate index sequence defining the
     polygon's exterior.
    :return: :class:`~ncsg.CFGeometryCollection`
    """

    # Allow a singletone geometry object to be passed.
    if isinstance(geoms, BaseGeometry):
        itr = [geoms]
    else:
        itr = geoms

    # Holds coordinate index arrays for each geometry.
    cindex_all = []
    # Holds all the x coordinate values.
    x = []
    # Holds all the y coordinate values.
    y = []
    # May hold z coordinate values.
    z = None
    # Flag to indicate if there are z values in our geometries.
    has_z = False
    # Track the current node index value when creating coordinate index arrays.
    node_index = start_index

    # Convert each geometry to its coordinate index representation.
    for ctr_geom_element, geom_element in enumerate(itr):
        # Coordinate index for the current geometry.
        cindex = []
        # Allows us to iterate over single-part and multi-part geometries.
        for ctr_geom, geom in enumerate(_get_geometry_iter_(geom_element)):
            # Determine if we have z coordinates in our geometry.
            if ctr_geom == 0 and ctr_geom_element == 0 and geom.has_z:
                z = []
                has_z = True
            # Add a multi-part break value if we are on the second component of a geometry.
            if ctr_geom > 0:
                cindex += [multipart_break]
            # Get the geometry nodes' coordinates.
            if 'polygon' in geom_type:
                coords = np.array(geom.exterior.coords)
            else:
                coords = np.array(geom)
            # Make sure we have a two-dimensional point array.
            if 'point' in geom_type:
                coords = coords.reshape(1, -1)
            # Extent coordinate containers with additional coordinates for the geometry.
            x += coords[:, 0].tolist()
            y += coords[:, 1].tolist()
            if has_z:
                z += coords[:, 2].tolist()
            # Extend the coordinate index array.
            cindex += range(node_index, node_index + coords.shape[0])
            # Increment the node index accordingly.
            node_index += coords.shape[0]
            # Check for polygon interiors.
            try:
                # Add interiors/holes if the polygon objects contains them.
                if len(geom.interiors) > 0:
                    for ii in geom.interiors:
                        # Add a hole to the coordinate index.
                        cindex += [hole_break]
                        # Convert exterior to a coordinate series and add these values to the coordinate arrays.
                        coords = np.array(ii)
                        x += coords[:, 0].tolist()
                        y += coords[:, 1].tolist()
                        if has_z:
                            z += coords[:, 2].tolist()
                        # Add coordinate indices.
                        cindex += range(node_index, node_index + coords.shape[0])
                        # Increment the node index.
                        node_index += coords.shape[0]
            except AttributeError:
                # If this is not a polygon, we are not worried about interiors.
                if 'polygon' in geom_type:
                    raise
        # Add the geometries coordinate index array to the collection of index arrays.
        cindex_all.append(cindex)

    return CFGeometryCollection(geom_type, cindex_all, x, y, z=z, start_index=start_index,
                                multipart_break=multipart_break, hole_break=hole_break)


# TODO (bekozi): Add docstring example and way to run test.
def loads(geom_type, cindex, x, y, z=None, start_index=0, multipart_break=BreakValue.MULTIPART,
          hole_break=BreakValue.HOLE):
    """
    Load a Shapely geometry object from its CF representation.

    :param geom_type: The destination geometry type. Valid values are ``"point"``, ``"linestring"``, ``"polygon"``, and
     multipart types `"multipoint"``, ``"multilinestring"``, ``"multipolygon"``.
    :type geom_type: str
    :param cindex: A one-dimensional integer array containing indices into the coordinate arrays ``x``, ``y``, and
     optionally ``z``. ``multipart_break`` and ``hole_break`` may be part of this coordinate sequence.
    :type cindex: :class:`numpy.ndarray`
    :param x: A one-dimensional array of x-coordinate values.
    :type x: :class:`numpy.ndarray`
    :param y: A one-dimensional array of y-coordinate values.
    :type y: :class:`numpy.ndarray`
    :param z: An optional one-dimensional array of z-coordinate values.
    :type z: ``None`` or :class:`numpy.ndarray`
    :param start_index: The starting index value. The default is Python zero-based indexing. Valid values are ``0`` or
        ``1``.
    :type start_index: int
    :param int multipart_break: A break value indicating a multipart geometry split. Must be a negative integer value.
     If ``None``, there will be no attempt to search for multipart splits.
    :param int hole_break: A break value indicating a hole in the previous polygon. Setting to ``None`` tells the
     function to not search for holes. Must be a negative integer value. This argument is valid only when decoding
     polygon geometry objects. All holes (interiors) must be placed after the coordinate index sequence defining the
     polygon's exterior.
    :return: The Shapely object representing the geometry.
    :rtype: :class:`shapely.geometry.base.BaseGeometry`
    :raises: ValueError
    """

    # Don't be concerned about case with the geometry type.
    geom_type = geom_type.lower()
    # Determine the shapely geometry type.
    shapely_type = _get_shapely_klass_(geom_type, single=True)
    # Convert the coordinate index array to a NumPy integer array. This is the only actual NumPy array that is
    # required.
    cindex = np.array(cindex, dtype=int)

    # Check the start index is reasonable (i.e. C v Fortran).
    if start_index < 0 or start_index > 1:
        raise ValueError('"start_index" must be zero or one.')

    # Adjust indices to zero-based.
    if start_index == 1:
        cindex = deepcopy(cindex)
        cindex[cindex > 0] -= 1  # Don't adjust the break values.

    # Split geometries if there is a break value to use. Otherwise, we'll operate on the single split.
    if multipart_break is None:
        splits = [cindex]
    else:
        splits = _get_splits_(cindex, multipart_break)
    len_splits = len(splits)

    # Convert and extract hole coordinate indices.
    if 'polygon' in geom_type:
        holes = _get_holes_(hole_break, splits, x, y, z=z)
    else:
        holes = None

    # Convert coordinate index sequences into coordinate sequences.
    coords = _extract_coordinates_(splits, x, y, z=z)

    # Convert the coordinate indices to the geometry object. There are separate paths for a single and multi-geometry.
    if len_splits == 1:
        if 'point' in geom_type:
            # Point coordinate sequences are not nested.
            ret = shapely_type(*coords[0])
        elif 'polygon' in geom_type:
            # Polygons optionally require information on holes/interiors. Passing an empty list is okay with Shapely.
            ret = shapely_type(coords[0], holes[0])
        else:
            # This is only for a line string.
            ret = shapely_type(coords[0])
    else:
        # With the exception of a polygon, multipart geometries are first converted to single part before being passed
        # to the multipart converter.
        ret = [None] * len_splits
        if 'point' in geom_type:
            # Remove a list level for multipoints.
            coords = [c[0] for c in coords]
        # Convert to the single part geometries.
        for idx, c in enumerate(coords):
            if 'polygon' in geom_type:
                ret[idx] = shapely_type(c, holes[idx])
            else:
                ret[idx] = shapely_type(c)
    if len_splits > 1 or geom_type.startswith('multi'):
        if len_splits == 1:
            # Only one split, but we want to convert to a multi-geometry.
            ret = [ret]
        # Collect the single part geometries into a multipart collection.
        ret = _get_shapely_klass_(geom_type, single=False)(ret)

    return ret


def _get_holes_(hole_break, multipart_splits, x, y, z=None):
    len_splits = len(multipart_splits)
    holes = [[]] * len_splits
    if hole_break is not None:
        # Check for holes in polygons.
        for idx, hidx in enumerate(multipart_splits):
            # Need to remove the hole indices from the exterior coordinates.
            hole_split_indices = np.where(hidx == hole_break)[0]
            if len(hole_split_indices) > 0:
                multipart_splits[idx] = multipart_splits[idx][0:hole_split_indices[0]]

            # Split holes into coordinate index sequences.
            hsplits = _get_splits_(hidx, hole_break)
            holes[idx] = hsplits[1:]

        # Convert coordinate index sequences for holes into actual coordinates.
        for hidx, h in enumerate(holes):
            holes[hidx] = _extract_coordinates_(h, x, y, z=z)
    return holes


def _get_splits_(to_split, break_value):
    # Locate the indices of the split values.
    widx = np.where(to_split == break_value)[0]
    # Only bother to break apart the array if the split value is found.
    if len(widx) == 0:
        splits = [to_split]
    else:
        splits = []
        start_of_split = 0
        for ctr, w in enumerate(widx):
            splits.append(to_split[start_of_split: w])
            start_of_split = w + 1
        # Do not forget the coordinates following the last split!
        splits.append(to_split[start_of_split:])
    return splits


def _extract_coordinates_(splits, x, y, z=None):
    coords = [None] * len(splits)

    # For each split, extract the coordinate indices from the coordinate arrays.
    for idx_split, split in enumerate(splits):
        sub_coords = [None] * len(split)
        for sub_split_idx, coordinate_idx in enumerate(split):
            sapp = [x[coordinate_idx], y[coordinate_idx]]
            if z is not None:
                sapp.append(z[coordinate_idx])
            sub_coords[sub_split_idx] = sapp
        coords[idx_split] = sub_coords
    return coords


def _get_geometry_iter_(geom):
    if isinstance(geom, BaseMultipartGeometry):
        ret = geom
    else:
        ret = [geom]
    return ret


def _get_shapely_klass_(geom_type, single=True):
    if geom_type.startswith('multi'):
        geom_type = geom_type[5:]
    ret = NCSG_GEOM_OBJECT_MAP[geom_type]
    if single:
        ret = ret['single']
    else:
        ret = ret['multi']
    return ret
