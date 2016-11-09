import fiona
import netCDF4 as nc
from shapely.geometry import shape

from ncsg import cf


def get_cf_geometry_collection(path_src, cf_geom_type):
    geoms = []
    with fiona.open(path_src, driver='GeoJSON') as source:
        for record in source:
            geom = shape(record['geometry'])
            geoms.append(geom)
    cf_geom = cf.from_shapely(cf_geom_type, geoms)
    return cf_geom


def main():
    CATCHMENTS = '/home/benkoziol/l/project/netCDF-CF-simple-geometry/data/use_cases/Bull_Creek/nhd_catchment.json'
    FLOWLINES = '/home/benkoziol/l/project/netCDF-CF-simple-geometry/data/use_cases/Bull_Creek/nhd_flowline.json'
    UPSTREAM_POINTS = '/home/benkoziol/l/project/netCDF-CF-simple-geometry/data/use_cases/Bull_Creek/upstream_point.json'
    OUT = '/tmp/bull_creek_NCSG.nc'
    OUT_CRA = '/tmp/bull_creek_NCSG_CRA.nc'

    catchments_coll = get_cf_geometry_collection(CATCHMENTS, 'multipolygon')
    flowlines_coll = get_cf_geometry_collection(FLOWLINES, 'linestring')
    upstream_points_coll = get_cf_geometry_collection(UPSTREAM_POINTS, 'point')

    # catchments_coll.describe(cra=True)
    # flowlines_coll.describe(cra=True)
    # upstream_points_coll.describe(cra=True)

    for path, cra in zip([OUT, OUT_CRA], [False, True]):
        with nc.Dataset(path, 'w') as ds:
            catchments_coll.write_netcdf(ds, cra=cra, string_id='c_')
            flowlines_coll.write_netcdf(ds, cra=cra, string_id='f_')
            upstream_points_coll.write_netcdf(ds, cra=cra, string_id='u_')


if __name__ == '__main__':
    main()
