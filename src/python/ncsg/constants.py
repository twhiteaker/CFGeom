from shapely.geometry import (
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
)

#: Maps single and multipart types.
NCSG_GEOM_OBJECT_MAP = {'point': Point,
                        'multipoint': MultiPoint,
                        'line': LineString,
                        'multiline': MultiLineString,
                        'polygon': Polygon,
                        'multipolygon': MultiPolygon}


class GeneralAttributes(object):
    CF_ROLE_NAME = 'cf_role'
    GEOM_TYPE_NAME = 'geometry_type'
    NODE_COUNT = 'node_count'
    PART_NODE_COUNT = 'part_node_count'
    RING_TYPE = 'interior_ring'
    COORDINATES = 'node_coordinates'
    STANDARD_NAME = 'standard_name'
    GEOM_X_NODE = 'geometry_x_node'
    GEOM_Y_NODE = 'geometry_y_node'
    GEOM_Z_NODE = 'geometry_z_node'
    CONVENTIONS = 'Conventions'
    CONVENTIONS_VALUE = 'CF-1.8'
    LONG_NAME = 'long_name'
    NODE_COUNT_LONG_NAME = 'count of coordinates in each instance geometry'
    PART_NODE_COUNT_LONG_NAME = 'count of nodes in each geometry part'
    RING_TYPE_LONG_NAME = 'type of each geometry part'


class RingType(object):
    OUTER = 0
    INNER = 1


class DataType(object):
    INT = int
    NODE_VLTYPE = 'node_VLType'
    PART_NODES_VLTYPE = 'part_nodes_VLType'
    FLOAT = float


class NetcdfDimension(object):
    GEOMETRY_COUNT = 'instance'
    NODE_COUNT = 'node'
    PART_COUNT = 'part'


class NetcdfVariable(object):
    GEOMETRY_CONTAINER = 'geometry_container'
    X = 'x'
    Y = 'y'
    Z = 'z'
    NODE_COUNT = 'node_count'
    PART_NODE_COUNT = 'part_node_count'
    RING_TYPE = 'interior_ring'
