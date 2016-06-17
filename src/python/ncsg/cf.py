from copy import deepcopy

import numpy as np

from ncsg.constants import NCSG_MULTIPART_BREAK_VALUE, NCSG_HOLE_BREAK_VALUE, NCSG_GEOM_OBJECT_MAP


# TODO (bekozi): Add docstring example and way to run test.
# TODO (bekozi): Test a polygon with multiple interior rings.
def loads(cindex, x, y, z=None, geom_type='point', start_index=0, multipart_break=NCSG_MULTIPART_BREAK_VALUE,
          hole_break=NCSG_HOLE_BREAK_VALUE):
    """
    Load a Shapely geometry object from its CF representation.

    :param cindex: A one-dimensional integer array containing indices into the coordinate arrays ``x``, ``y``, and
        optionally ``z``. ``multipart_break`` and ``hole_break`` may be part of this coordinate sequence.
    :type cindex: :class:`numpy.ndarray`
    :param x: A one-dimensional array of x-coordinate values.
    :type x: :class:`numpy.ndarray`
    :param y: A one-dimensional array of y-coordinate values.
    :type y: :class:`numpy.ndarray`
    :param z: An optional one-dimensional array of z-coordinate values.
    :type z: ``None`` or :class:`numpy.ndarray`
    :param geom_type: The destination geometry type. Valid values are ``"point"``, ``"linestring"``, and ``"polygon"``.
    :type geom_type: str
    :param start_index: The starting index value. The default is Python zero-based indexing. Valid values are ``0`` or
        ``1``.
    :type start_index: int
    :param multipart_break: A break value indicating a multipart geometry split. Setting to ``None`` tells the function
        to not search for breaks. Must be a negative integer value.
    :param hole_break: A break value indicating a hole in the previous polygon. Setting to ``None`` tells the function
        to not search for breaks. Must be a negative integer value. This argument is valid only when decoding polygon
        geometry objects. All holes (interiors) must be placed after the coordinate index sequence defining the
        polygon's exterior.
    :return: The Shapely object representing the geometry.
    :rtype: :class:`shapely.geometry.base.BaseGeometry`
    :raises: ValueError
    """

    # Don't be concerned about case with the geometry type.
    geom_type = geom_type.lower()
    # Determine the shapely geometry type.
    shapely_type = NCSG_GEOM_OBJECT_MAP[geom_type]['single']
    # Convert the coordinate index array to a NumPy integer array. This is the only actual NumPy array that is
    # required.
    cindex = np.array(cindex, dtype=int)

    # Check the start index is reasonable (i.e. C v Fortran).
    if start_index < 0 or start_index > 1:
        raise ValueError('"start_index" must be zero or one.')

    # Adjust indices to zero-based.
    if start_index == 1:
        cindex = deepcopy(cindex)
        cindex[cindex>0] -= 1

    # Split geometries if a multipart break value is provided. Otherwise, we'll operate on the single split.
    if multipart_break is None:
        splits = [cindex]
    else:
        splits = _get_splits_(cindex, multipart_break)
    len_splits = len(splits)

    # Convert and extract hole coordinate indices.
    if geom_type == 'polygon':
        holes = _get_holes_(hole_break, splits, x, y, z=z)
    else:
        holes = None

    # Convert coordinate index sequences into coordinate sequences.
    coords = _extract_coordinates_(splits, x, y, z=z)

    # Convert the coordinate indices to the geometry object. There are separate paths for a single and multi-geometry.
    if len_splits == 1:
        if geom_type == 'point':
            # Point coordinate sequences are not nested.
            ret = shapely_type(*coords[0])
        elif geom_type == 'polygon':
            # Polygons optionally require information on holes/interiors. Passing an empty list is okay with Shapely.
            ret = shapely_type(coords[0], holes[0])
        else:
            # This is only for a line string.
            ret = shapely_type(coords[0])
    else:
        # With the exception of a polygon, multipart geometries are first converted to single part before being passed
        # to the multipart converter.
        multi = [None] * len_splits
        if geom_type == 'point':
            # Remove a list level for multipoints.
            coords = [c[0] for c in coords]
        # Convert to the single part geometries.
        for idx, c in enumerate(coords):
            if geom_type == 'polygon':
                multi[idx] = shapely_type(c, holes[idx])
            else:
                multi[idx] = shapely_type(c)
        # Collect the single part geometries into a multipart collection.
        ret = NCSG_GEOM_OBJECT_MAP[geom_type]['multi'](multi)

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
