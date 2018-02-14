from shapely.geometry import (
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
)
from shapely.geometry.base import BaseGeometry


_geom_map = {'Point': Point,
             'MultiPoint': MultiPoint,
             'LineString': LineString,
             'MultiLineString': MultiLineString,
             'Polygon': Polygon,
             'MultiPolygon': MultiPolygon}


def _resolve_target_geom_type(geom, shapely_type):
    try:
        if isinstance(shapely_type, BaseGeometry):
            shapely_type = shapely_type.__name__
    except:
        pass    

    wkt_type = geom.wkt_type()
    if shapely_type and shapely_type != wkt_type:
        if shapely_type.replace('Multi', '') != wkt_type.replace('Multi', ''):
            m = ('Target shapely type of {0} does not match input geometry '
                 'type of {1}'.format(shapely_type, wkt_type))
            raise ValueError(m)
        if 'Multi' in shapely_type and 'Multi' not in wkt_type:
            wkt_type = shapely_type
    return _geom_map[wkt_type]


def _extract_geom_part_coordinates(part):
    coords = []
    x_vals = part.x
    y_vals = part.y
    if part.z:
        z_vals = part.z
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


def geom_to_shapely(geom, shapely_geom_type=None):
    shapely_type = _resolve_target_geom_type(geom, shapely_geom_type)
    shapely_type_str = shapely_type.__name__

    if 'Polygon' in shapely_type_str:
        single_type = _geom_map['Polygon']
        holes = []
        polygons = []
        exterior = None
        for part in geom.parts:
            part_coords = _extract_geom_part_coordinates(part)
            if part.is_hole:
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
        if shapely_type_str.startswith('Multi'):
            ret = shapely_type(polygons)
        else:
            ret = polygons[0]
    else:
        coords = [_extract_geom_part_coordinates(part) for part in geom.parts]
        if len(coords) == 1 and not shapely_type_str.startswith('Multi'):
            coords = coords[0]
        ret = shapely_type(coords)
        
    return ret
