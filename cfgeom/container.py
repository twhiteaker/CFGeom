"""Represents a geometry container, a collection of like geometries."""

from . util import is_iterable, as_iterable
from . geometry import Geometry
from . convert.json_io.json_writer import container_to_json
from . convert.netcdf.nc_writer import write_netcdf
from . convert.shapely_io.shapely_writer import geom_to_shapely as to_shp


class GeometryContainer(object):
    """Contains a set of geometries of the same type.

    Attributes:
        geom_type (str): Geometry type, eithier point, line, or polygon.
        geoms (array-like(Geometry)): List of geometry objects.

    """

    def __init__(self, geometries):
        """Inits GeometryContainer with geometries.

        Args:
            geometries (array-like(Geometry)): List of geometry objects.

        Raises:
            ValueError: If no Geometries are provided, or if geometries are of
                different types.

        """
        geometries = as_iterable(geometries)
        if not len(geometries):
            raise ValueError('Geometry must be provided')
        types = []
        for geom in geometries:
            if not isinstance(geom, Geometry):
                raise ValueError('Geometry must be instance of Geometry class')
            types.append(geom.geom_type)
        types = set(types)
        if len(types) > 1:
            m = ('Geometry container can only store one type.  Types provided:'
                 ' {0}').format(','.join(types))
            raise ValueError(m)
        self.geom_type = geometries[0].geom_type
        self.geoms = geometries
        self._has_hole = False if self.geom_type != 'polygon' else None
        self._is_multipart = None
        self._has_z = None
        self._wkt_type = None


    def __eq__(self, other):
        if type(other) is type(self):
            try:
                attributes_to_check = [k for k in self.__dict__ if k[0] != '_']
                for k in attributes_to_check:
                    if self.__dict__[k] != other.__dict__[k]:
                        return False
                return True
            except:
                return False
        return False        


    def __ne__(self, other):
        return not self.__eq__(other)


    def has_hole(self):
        """Determines if any geometries in the container have polygon holes.

        Note:
            Only polygons can have holes.

        Returns:
            bool: True if holes are found, False otherwise.

        """
        if self._has_hole is None:
            self._has_hole = False
            for geom in self.geoms:
                if geom.has_hole():
                    self._has_hole = True
                    break
        return self._has_hole


    def is_multipart(self):
        """Determines if any geometries in the container have multiple parts.

        Returns:
            bool: True if multipart geometries were found, False otherwise.

        """
        if self._is_multipart is None:
            self._is_multipart = False
            for geom in self.geoms:
                if geom.is_multipart():
                    self._is_multipart = True
                    break
        return self._is_multipart


    def has_z(self):
        """Determines if any geometries in the container have z values.

        Returns:
            bool: True if z values were found, False otherwise.

        """
        if self._has_z is None:
            self._has_z = False
            for geom in self.geoms:
                if geom.has_z():
                    self._has_z = True
                    break
        return self._has_z


    def orient(self, holes_clockwise=True):
        """Orients polygon exterior and interior rings consistently, in-place.

        Args:
            holes_clockwise (bool, optional): True if nodes comprising holes
                should be oriented clockwise while exterior rings are oriented
                anticlockwise, False if holes should be oriented anticlockwise
                while exterior rings are oriented clockwise.

        Raises:
            NotImplementedError: If geometry type is not polygon.

        """
        for geom in self.geoms:
            geom.orient(holes_clockwise)


    def wkt_type(self):
        """Determines the matching WKT type for the container.

        Determines the Well-Known Text (WKT) type which can represent all
        geometries within the container. If any multipart geometries are
        present, then a multipart WKT type is required.

        Returns:
            str: The matching WKT type.

        """
        if self._wkt_type is None:
            types = list(set([g.wkt_type() for g in self.geoms]))
            self._wkt_type = types[0]
            for t in types:
                if 'Multi' in t:
                    self._wkt_type = t
                    break
        return self._wkt_type


    def to_json(self):
        """Serializes the geometry container to JSON.

        Returns:
            str: JSON serialization of the geometry container.

        """
        return container_to_json(self)


    def to_netcdf(self, netcdf_path_or_object, nc_names=None, use_vlen=False):
        """Exports the geometry container to a CF-compliant netCDF file.

        Args:
            netcdf_path_or_object (str or netCDF4.Dataset): Target netCDF file
                or object.  If the file exists, it is overwritten. Pass a
                netCDF4.Dataset object to append to an existing file.
            nc_names (cfgeom.convert.netcdf.nc_names.NcNames, optional): Object
                specifying names for types, dimensions, and variables to use in
                the netCDF file.
            use_vlen (bool, optional): True if variable length (VLEN) arrays
                from the netCDF enhanced model should be used for variables
                such as node coordinate arrays, False otherwise.

        """
        write_netcdf(self, netcdf_path_or_object, nc_names=nc_names,
                     use_vlen=use_vlen)


    def to_shapely(self, shapely_geom_type=None):
        """Converts geometries in the container to shapely objects.

        Args:
            shapely_geom_type (str or shapely.geometry type, optional): The
                target shapely geometry type. Use this to force a multipart
                shapely type when the geometry is single-part.

        Returns:
            list(shapely.geometry.BaseGeometry): List of shapely geometries.

        """
        return [to_shp(g, shapely_geom_type) for g in self.geoms]
