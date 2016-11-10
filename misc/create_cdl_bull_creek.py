from collections import OrderedDict

import fiona
import netCDF4 as nc
from shapely.geometry import shape

from ncsg import cf


def get_cf_geometry_collection(path_src, cf_geom_type, string_id):
    geoms = []
    with fiona.open(path_src, driver='GeoJSON') as source:
        properties = OrderedDict()
        for p in source.schema['properties'].keys():
            properties[p] = []
        for record in source:
            geom = shape(record['geometry'])
            for pk, pv in record['properties'].items():
                properties[pk].append(pv)
            geoms.append(geom)
    cf_geom = cf.from_shapely(cf_geom_type, geoms, string_id=string_id)
    return cf_geom, properties


def write_collection(coll, coll_properties, cra, ds):
    coll.write_netcdf(ds, cra=cra)
    name_cindex = coll.cf_names['variables']['coordinate_index']
    string_id = coll.string_id
    for pk, pv in coll_properties.items():
        vname = '{}{}'.format(string_id, pk)
        dtype = type(pv[0])
        if dtype == str:
            dtype = 'S1'
        var = ds.createVariable(vname, dtype, dimensions=[coll.cf_names['dimensions']['geometry_count']])
        var[:] = pv
        var.cf_simple_geom = name_cindex


def main():
    CATCHMENTS = '/home/benkoziol/l/project/netCDF-CF-simple-geometry/data/use_cases/Bull_Creek/nhd_catchment.json'
    FLOWLINES = '/home/benkoziol/l/project/netCDF-CF-simple-geometry/data/use_cases/Bull_Creek/nhd_flowline.json'
    UPSTREAM_POINTS = '/home/benkoziol/l/project/netCDF-CF-simple-geometry/data/use_cases/Bull_Creek/upstream_point.json'
    OUT = '/tmp/bull_creek_NCSG.nc'
    OUT_CRA = '/tmp/bull_creek_NCSG_CRA.nc'

    catchments_coll, catchments_properties = get_cf_geometry_collection(CATCHMENTS, 'multipolygon', 'catchments_')
    flowlines_coll, flowlines_properties = get_cf_geometry_collection(FLOWLINES, 'linestring', 'flowlines_')
    upstream_points_coll, upstream_properties = get_cf_geometry_collection(UPSTREAM_POINTS, 'point', 'upstream_')

    # catchments_coll.describe(cra=True)
    # flowlines_coll.describe(cra=True)
    # upstream_points_coll.describe(cra=True)

    for path, cra in zip([OUT, OUT_CRA], [False, True]):
        with nc.Dataset(path, 'w') as ds:
            write_collection(catchments_coll, catchments_properties, cra, ds)
            write_collection(flowlines_coll, flowlines_properties, cra, ds)
            write_collection(upstream_points_coll, upstream_properties, cra, ds)


if __name__ == '__main__':
    main()
