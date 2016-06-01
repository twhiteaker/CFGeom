from shapely.geometry import Point, MultiPoint, Polygon, MultiPolygon, LineString, MultiLineString

#: Break value for multipart geometries.
NCSG_MULTIPART_BREAK_VALUE = -1

#: Break value to indicate holes in polygons.
NCSG_HOLE_BREAK_VALUE = -2

#: Maps geometry types to their associate Shapely types.
NCSG_GEOM_OBJECT_MAP = {'point': {'single': Point, 'multi': MultiPoint},
                        'linestring': {'single': LineString, 'multi': MultiLineString},
                        'polygon': {'single': Polygon, 'multi': MultiPolygon}}
