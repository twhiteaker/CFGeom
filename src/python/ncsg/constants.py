from shapely.geometry import Point, MultiPoint, Polygon, MultiPolygon, LineString, MultiLineString


#: Maps single and multipart types.
NCSG_GEOM_OBJECT_MAP = {'point': {'single': Point, 'multi': MultiPoint},
                        'linestring': {'single': LineString, 'multi': MultiLineString},
                        'polygon': {'single': Polygon, 'multi': MultiPolygon}}


class BreakValue(object):
    MULTIPART = -1
    HOLE = -2


class DataType(object):
    INT = int
    GEOMETRY_VLTYPE = 'geom_VLType'
    FLOAT = float


class NetcdfDimension(object):
    GEOMETRY_COUNT = 'geom'
    NODE_COUNT = 'node'
    CRA_NODE_INDEX = 'node_index'


class NetcdfVariable(object):
    COORDINATE_INDEX = 'coordinate_index'
    X = 'x'
    Y = 'y'
    Z = 'z'
    CRA_STOP = 'geom_stop'


class OuterRingOrder(object):
    NAME = 'outer_ring_order'
    CCW = 'anticlockwise'
    CW = 'clockwise'


class ClosureConvention(object):
    NAME = 'closure_convention'
    INDEPENDENT = 'last_node_independent_of_first'
    CLOSED = 'last_node_equals_first'
