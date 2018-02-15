"""Constants for reading and writing netCDF files."""

class Attrs(object):
    """NetCDF attribute names and values, taken largely from CF conventions."""

    AXIS = 'axis'
    GEOM_TYPE = 'geometry_type'
    NODE_COUNT = 'node_count'
    PART_NODE_COUNT = 'part_node_count'
    RING_TYPE = 'interior_ring'
    NODE_COORDS = 'node_coordinates'
    STANDARD_NAME = 'standard_name'
    GEOM_X_NODE = 'X'
    GEOM_Y_NODE = 'Y'
    GEOM_Z_NODE = 'Z'
    CONVENTIONS = 'Conventions'
    LONG_NAME = 'long_name'
    NODE_COUNT_LONG_NAME = 'count of coordinates in each instance geometry'
    PART_NODE_COUNT_LONG_NAME = 'count of nodes in each geometry part'
    RING_TYPE_LONG_NAME = 'type of each polygon geometry part'


class RingType(object):
    """Indicates polygon ring type. Inner rings are polygon holes."""

    OUTER = 0
    INNER = 1
