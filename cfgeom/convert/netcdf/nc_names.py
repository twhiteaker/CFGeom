"""Means of providing names and attribute values to use in a netCDF file."""

class NcNames(object):
    """Provides names and attribute values to use in a netCDF file."""

    def __init__(self):
        """Inits NcNames with default values."""

        self.node_vltype = 'node_VLType'
        self.part_node_vltype = 'part_node_VLType'
        self.instance_dim = 'instance'
        self.node_dim = 'node'
        self.part_dim = 'part'
        self.x_var = 'x'
        self.y_var = 'y'
        self.z_var = 'z'
        self.container_var = 'geometry_container'
        self.node_count_var = 'node_count'
        self.part_node_count_var = 'part_node_count'
        self.ring_var = 'interior_ring'
        self.conventions = 'CF-1.8'


    def set_prefix(self, prefix):
        """Prepends text to some names.

        Args:
            prefix (str): The prefix to append, e.g., mydata_. A resulting
                variable name might be mydata_x.

        """
        self.node_dim = prefix + self.node_dim
        self.part_dim = prefix + self.part_dim
        self.x_var = prefix + self.x_var
        self.y_var = prefix + self.y_var
        self.z_var = prefix + self.z_var
        self.container_var = prefix + self.container_var
        self.node_count_var = prefix + self.node_count_var
        self.part_node_count_var = prefix + self.part_node_count_var
        self.ring_var = prefix + self.ring_var
