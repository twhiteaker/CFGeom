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


def _get_geometry_iter(geom):
    if isinstance(geom, BaseMultipartGeometry):
        ret = geom
    else:
        ret = [geom]
    return ret


def _get_coordinates_as_list(coords, column_index):
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
    x = _get_coordinates_as_list(coords, 0)
    y = _get_coordinates_as_list(coords, 1)
    if has_z:
        z = _get_coordinates_as_list(coords, 2)
    else:
        z = None
    return Part(x, y, z=z, is_hole=is_hole)


def shapely_to_geom(shape):
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
    if not geoms:
        raise ValueError('No Shapely geometries provided')

    # Allow a singleton geometry object to be passed.
    if isinstance(geoms, BaseGeometry):
        geoms = [geoms]

    cf_geoms = [shapely_to_geom(g) for g in geoms]
    return GeometryContainer(cf_geoms)
