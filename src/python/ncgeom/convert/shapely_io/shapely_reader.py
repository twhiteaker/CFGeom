"""Converts from shapely geometries to GeometryContainer objects."""

import numpy as np
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry

from ... container import GeometryContainer
from ... geometry import Geometry
from ... part import Part


_geom_map = {'Point': 'point',
             'MultiPoint': 'point',
             'LineString': 'line',
             'MultiLineString': 'line',
             'Polygon': 'polygon',
             'MultiPolygon': 'polygon'}
"""dict: Maps from shapely geometry types to CF types."""


def _get_geometry_iter(geom):
    """Gets an iterable of geometries from an input geometry.

    Multipart geometries in shapely are iterable, but single-part geometries
    are not. If a single-part geometry is provided, it is returned within a
    list to support iteration.

    Args:
        geom (shapely.geometry.BaseGeometry): Shapely geometry object.

    Returns:
        array-like(shapely.geometry.BaseGeometry): Iterable of geometries.

    """
    if isinstance(geom, BaseMultipartGeometry):
        ret = geom
    else:
        ret = [geom]
    return ret


def _get_coordinates_as_list(coords, column_index):
    """Returns a list of X, Y, or Z values from shapely geometry coordinates.

    Args:
        coords (array-like): Shapely geometry coordinates, where each
            coordinate is a tuple of x, y, and z values (if present).
        column_index (int): Column to extract from the coordinates. X, Y, and Z
            values are in columns 0, 1, and 2, respectively.

    Returns:
        array-like(float): List of geometry coordinate values.

    """
    try:
        ret = coords[:, column_index].tolist()
    except IndexError:
        if coords.ndim == 1:
            coords = coords.reshape(-1, coords.shape[0])
            ret = _get_coordinates_as_list(coords, column_index)
        else:
            raise
    return ret


def _shapely_coords_to_part(coords, has_z, is_hole=False):
    """Converts shapely coordinates to a geometry Part instance.

    Args:
        coords (array-like): Shapely geometry coordinates, where each
        coordinate is a tuple of x, y, and z values (if present).
        has_z (bool): True if coordinates include Z values, False otherwise.
        is_hole (bool): True if the geometry part is a polygon interior ring.

    Returns:
        Part: Part instance.

    """
    x = _get_coordinates_as_list(coords, 0)
    y = _get_coordinates_as_list(coords, 1)
    if has_z:
        z = _get_coordinates_as_list(coords, 2)
    else:
        z = None
    return Part(x, y, z=z, is_hole=is_hole)


def shapely_to_geom(shape):
    """Converts shapely geometry to a Geometry instance.

    Args:
        shape (shapely.geometry.BaseGeometry): Shapely geometry object.

    Returns:
        Geometry: Geometry instance.

    """
    cf_parts = []
    geom_type = _geom_map[shape.geom_type]
    for ctr_part, part in enumerate(_get_geometry_iter(shape)):
        if geom_type == 'polygon':
            coords = np.array(part.exterior.coords)
        else:
            coords = np.array(part)
        cf_parts.append(_shapely_coords_to_part(coords, part.has_z))
        
        # Check for polygon interiors
        try:
            if len(part.interiors) > 0:
                for ii in part.interiors:
                    coords = np.array(ii)
                    cf_parts.append(
                        _shapely_coords_to_part(coords, part.has_z, True))
        except AttributeError:
            # If this is not a polygon, we are not worried about interiors.
            if geom_type == 'polygon':
                raise    
    return Geometry(geom_type, cf_parts)


def shapely_to_container(geoms):
    """Converts list of shapely geometries to a GeometryContainer instance.

    Args:
        geoms (array-like(shapely.geometry.BaseGeometry)): Shapely geometry
            object or objects.

    Returns:
        GeometryContainer: GeometryContainer instance.

    """
    if not geoms:
        raise ValueError('No Shapely geometries provided')

    # Allow a singleton geometry object to be passed.
    if isinstance(geoms, BaseGeometry):
        geoms = [geoms]

    cf_geoms = [shapely_to_geom(g) for g in geoms]
    return GeometryContainer(cf_geoms)
