from ncgeom.util import is_iterable, as_iterable
from ncgeom.part import Part
from ncgeom.io.shapely_io.shapely_writer import geom_to_shapely as to_shp


class Geometry(object):
    _wkt_types = {'point': 'Point', 'line': 'LineString', 'polygon': 'Polygon'}


    def __init__(self, geom_type, parts):
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


    def has_hole(self):
        if self._has_hole is None:
            self._has_hole = False
            for part in self.parts:
                if part.is_hole:
                    self._has_hole = True
                    break
        return self._has_hole


    def is_multipart(self):
        if self._is_multipart is None:
            not_holes = [p for p in self.parts if not p.is_hole]
            self._is_multipart = len(not_holes) > 1
        return self._is_multipart


    def has_z(self):
        if self._has_z is None:
            self._has_z = False
            for part in self.parts:
                # Test len to avoid ambiguous truth value of array error
                if len(part.z):
                    self._has_z = True
                    break
        return self._has_z


    def orient(self, holes_clockwise=True):
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
        if self.is_multipart():
            return 'Multi' + self._wkt_types[self.geom_type]
        else:
            return self._wkt_types[self.geom_type]


    def to_shapely(self, shapely_geom_type=None):
        return to_shp(self, shapely_geom_type)
