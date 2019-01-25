"""Represents a geometry, such as a point, line, or polygon."""

from . util import is_iterable, as_iterable
from . part import Part
from . convert.shapely_io.shapely_writer import geom_to_shapely as to_shp


_wkt_types = {'point': 'Point', 'line': 'LineString', 'polygon': 'Polygon'}
"""dict: Maps from geometry types to Well-Known Text (WKT) types."""


class Geometry(object):
    """Contains vertices for a single geometry part.

    Attributes:
        geom_type (str): Geometry type, eithier point, line, or polygon.
        parts (array-like(Part)): List of geometry parts.

    """

    def __init__(self, geom_type, parts):
        """Inits Geometry with a geometry type and geometry parts.

        Args:
            geom_type (str): Geometry type, eithier point, line, or polygon.
            parts (array-like(Part)): List of geometry parts.

        Raises:
            ValueError: If geometry type is not point, line, or polygon; or if
                no Parts are provided, or if node count per part does not work
                with the provided geometry type, or if first polygon part is a
                hole.

        """
        geom_type = geom_type.lower()
        if geom_type not in ['point', 'line', 'polygon']:
            raise ValueError('geom_type must be point, line, or polygon')
        parts = as_iterable(parts)
        if not len(parts):
            raise ValueError('Geometry part(s) must be provided')
        for part in parts:
            if not isinstance(part, Part):
                raise ValueError('Geometry part must be instance of Part class')
            nodes = len(part.x)
            if geom_type == 'polygon' and nodes < 3:
                raise ValueError('Polygon parts require at least three nodes')
            elif geom_type == 'line' and nodes < 2:
                raise ValueError('Line parts require at least two nodes')
            elif geom_type == 'point' and nodes != 1:
                raise ValueError('Points must have one node per part')
        if geom_type == 'polygon' and parts[0].is_hole:
            raise ValueError('First polygon part cannot be a hole')
        self.geom_type = geom_type
        self.parts = parts
        self._has_hole = False if geom_type != 'polygon' else None
        self._is_multipart = None
        self._has_z = None


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
        """Determines if the geometry has any polygon holes, i.e., inner rings.

        Note:
            Only polygons can have holes.

        Returns:
            bool: True if holes are found, False otherwise.

        """
        if self._has_hole is None:
            self._has_hole = False
            for part in self.parts:
                if part.is_hole:
                    self._has_hole = True
                    break
        return self._has_hole


    def is_multipart(self):
        """Determines if the geometry has multiple parts.

        Returns:
            bool: True if the geometry is multipart, False if single-part.

        """
        if self._is_multipart is None:
            not_holes = [p for p in self.parts if not p.is_hole]
            self._is_multipart = len(not_holes) > 1
        return self._is_multipart


    def has_z(self):
        """Determines if the geometry has z values.

        Returns:
            bool: True if the geometry has z values, False otherwise.

        """
        if self._has_z is None:
            self._has_z = False
            for part in self.parts:
                # Test len to avoid ambiguous truth value of array error
                if len(part.z):
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
            NotImplementedError: If geometry is not a polygon.

        """
        if self.geom_type != 'polygon':
            raise NotImplementedError('Only polygons can be oriented')
        for part in self.parts:
            is_hole = part.is_hole
            is_cw = part.is_clockwise()
            if ((holes_clockwise and is_hole and not is_cw) or
                (holes_clockwise and not is_hole and is_cw) or
                (not holes_clockwise and is_hole and is_cw) or
                (not holes_clockwise and not is_hole and not is_cw)):
                    part.reverse()


    def wkt_type(self):
        """Determines the matching Well-Known Text (WKT) type for the geometry.

        Returns:
            str: The matching WKT type.

        """
        if self.is_multipart():
            return 'Multi' + _wkt_types[self.geom_type]
        else:
            return _wkt_types[self.geom_type]


    def to_shapely(self, shapely_geom_type=None):
        """Converts the geometry to a shapely object.

        Args:
            shapely_geom_type (str or shapely.geometry type, optional): The
                target shapely geometry type. Use this to force a multipart
                shapely type when the geometry is single-part.

        Returns:
            shapely.geometry.BaseGeometry: Shapely geometry.

        """
        return to_shp(self, shapely_geom_type)
