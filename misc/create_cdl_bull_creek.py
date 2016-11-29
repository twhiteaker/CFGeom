from collections import OrderedDict
from datetime import datetime, timedelta

import fiona
import netCDF4 as nc
import numpy as np
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
    string_id = coll.string_id
    for pk, pv in coll_properties.items():
        vname = '{}{}'.format(string_id, pk)
        try:
            dtype = pv.dtype
        except AttributeError:
            dtype = type(pv[0])
        if dtype == str:
            dtype = 'S1'
        try:
            if pv.ndim > 1:
                dimensions = ['time', coll.cf_names['dimensions']['geometry_count']]
            else:
                raise AttributeError
        except AttributeError:
            dimensions = [coll.cf_names['dimensions']['geometry_count']]
        var = ds.createVariable(vname, dtype, dimensions=dimensions)
        var[:] = pv


def main():
    CATCHMENTS = '/home/benkoziol/l/project/netCDF-CF-simple-geometry/data/use_cases/Bull_Creek/nhd_catchment.json'
    FLOWLINES = '/home/benkoziol/l/project/netCDF-CF-simple-geometry/data/use_cases/Bull_Creek/nhd_flowline.json'
    UPSTREAM_POINTS = '/home/benkoziol/l/project/netCDF-CF-simple-geometry/data/use_cases/Bull_Creek/upstream_point.json'
    OUT = '/tmp/bull_creek_NCSG.nc'
    OUT_CRA = '/tmp/bull_creek_NCSG_CRA.nc'
    CATCHMENTS_SID = 'catchments_'
    FLOWLINES_SID = 'flowlines_'
    UPSTREAM_SID = 'upstream_'
    START_TIME = datetime(2016, 8, 14, 0)
    STOP_TIME = datetime(2016, 8, 17, 0)
    TIME_DELTA = timedelta(hours=1)

    times = [START_TIME]
    curr_time = START_TIME
    while curr_time != STOP_TIME:
        curr_time += TIME_DELTA
        times.append(curr_time)

    catchments_coll, catchments_properties = get_cf_geometry_collection(CATCHMENTS, 'multipolygon', CATCHMENTS_SID)
    catchments_properties['evapotranspiration'] = np.zeros((len(times), catchments_coll.cindex.shape[0]))
    catchments_properties['soil_moisture'] = np.zeros((len(times), catchments_coll.cindex.shape[0]))

    flowlines_coll, flowlines_properties = get_cf_geometry_collection(FLOWLINES, 'linestring', FLOWLINES_SID)
    flowlines_properties['streamflow'] = np.zeros((len(times), flowlines_coll.cindex.shape[0]))

    upstream_points_coll, upstream_properties = get_cf_geometry_collection(UPSTREAM_POINTS, 'point', UPSTREAM_SID)

    # catchments_coll.describe(cra=True)
    # flowlines_coll.describe(cra=True)
    # upstream_points_coll.describe(cra=True)

    for path, cra in zip([OUT, OUT_CRA], [False, True]):
        with nc.Dataset(path, 'w') as ds:
            ds.createDimension('time')
            wtimes = nc.date2num(times, 'hours since 2000-1-1-00:00')
            tvar = ds.createVariable('time', wtimes.dtype, dimensions=['time'])
            tvar[:] = wtimes
            tvar.axis = 'T'
            tvar.calendar = 'standard'
            tvar.units = 'hours since 2000-1-1-00:00'

            write_collection(catchments_coll, catchments_properties, cra, ds)
            write_collection(flowlines_coll, flowlines_properties, cra, ds)
            write_collection(upstream_points_coll, upstream_properties, cra, ds)


if __name__ == '__main__':
    main()
