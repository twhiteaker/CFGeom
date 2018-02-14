from . util import is_iterable, as_iterable
from . geometry import Geometry
from . convert.json_io.json_writer import container_to_json
from . convert.netcdf.nc_writer import write_netcdf
from . convert.shapely_io.shapely_writer import geom_to_shapely as to_shp


class GeometryContainer(object):
    def __init__(self, geometries):
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


    def has_hole(self):
        if self._has_hole is None:
            self._has_hole = False
            for geom in self.geoms:
                if geom.has_hole():
                    self._has_hole = True
                    break
        return self._has_hole


    def is_multipart(self):
        if self._is_multipart is None:
            self._is_multipart = False
            for geom in self.geoms:
                if geom.is_multipart():
                    self._is_multipart = True
                    break
        return self._is_multipart


    def has_z(self):
        if self._has_z is None:
            self._has_z = False
            for geom in self.geoms:
                if geom.has_z():
                    self._has_z = True
                    break
        return self._has_z


    def orient(self, holes_clockwise=True):
        for geom in self.geoms:
            geom.orient(holes_clockwise)


    def wkt_type(self):
        if self._wkt_type is None:
            types = list(set([g.wkt_type() for g in self.geoms]))
            self._wkt_type = types[0]
            for t in types:
                if 'Multi' in t:
                    self._wkt_type = t
                    break
        return self._wkt_type


    def to_json(self):
        return container_to_json(self)


    def to_netcdf(self, netcdf_path_or_object, nc_names=None, use_vlen=False):
        return write_netcdf(self, netcdf_path_or_object, nc_names=nc_names,
                            use_vlen=use_vlen)


    def to_shapely(self, shapely_geom_type=None):
        return [to_shp(g, shapely_geom_type) for g in self.geoms]
