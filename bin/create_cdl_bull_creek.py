"""Add geometry to Bull Creek streamflow data and export CDL."""

from collections import OrderedDict
from datetime import datetime, timedelta
import os
import subprocess
import sys

import fiona
from netCDF4 import Dataset, stringtochar
import numpy as np
from shapely.geometry import shape

sys.path.append(os.path.abspath('../src/python'))
from cfgeom import read_shapely
from cfgeom.convert.netcdf.nc_names import NcNames

CATCHMENTS = '../data/use_cases/Bull_Creek/nhd_catchment.json'
FLOWLINES = '../data/use_cases/Bull_Creek/nhd_flowline.json'
UPSTREAM_POINTS = '../data/use_cases/Bull_Creek/upstream_point.json'
IN = '../data/use_cases/Bull_Creek/bull_creek_streamflow.cdl'
OUT_VLEN = '../misc/tmp/bull_creek_with_geom_VLEN.nc'
OUT_CRA = '../misc/tmp/bull_creek_with_geom_CRA.nc'
CATCHMENTS_SID = 'catchments_'
FLOWLINES_SID = 'flowlines_'
UPSTREAM_SID = 'upstream_'
INSTANCE_DIM = 'comid'


def ncgen(src, dest):
    shell = os.name == 'nt'  # Use shell=True for commands on Windows
    cmd = ['ncgen']
    cmd.append('-o')
    cmd.append(os.path.abspath(dest))
    cmd.append(os.path.abspath(src))
    return str(subprocess.check_output(cmd, shell=shell))
    

def ncdump(src):
    dest = src[:-3] + '.cdl'
    shell = os.name == 'nt'  # Use shell=True for commands on Windows
    cmd = ['ncdump']
    cmd.append(os.path.abspath(src))
    cmd.append('>')
    cmd.append(os.path.abspath(dest))
    return str(subprocess.check_output(cmd, shell=shell))
    

def get_cf_geometry_collection(path_src, string_id, comids):
    """Returns geometries and properties from GeoJSON sorted by COMID."""
    properties = OrderedDict()
    features = {}  # indexes features by COMID
    with fiona.open(path_src, driver='GeoJSON') as source:
        for p in source.schema['properties'].keys():
            if p != 'COMID':
                properties[p] = []
        for record in source:
            comid = None
            geom = shape(record['geometry'])
            props = {}
            for pk, pv in record['properties'].items():
                if pk == 'COMID':
                    comid = pv
                else:
                    props[pk] = pv
            if comid is None:
                raise KeyError('COMID not found in feature attributes')
            elif comid in features:
                raise ValueError('Duplicate COMID found: {}'.format(comid))
            features[comid] = (geom, props)
    geoms = []
    for comid in comids:
        geom, props = features[comid]
        geoms.append(geom)
        for pk, pv in props.items():
            properties[pk].append(pv)
    print string_id
    cf_geom = read_shapely(geoms)
    return cf_geom, properties


def write_collection(coll, nc_names, coll_properties, cra, nc):
    nc_names.instance_dim = INSTANCE_DIM
    coll.to_netcdf(nc, nc_names=nc_names, use_vlen=(not cra))
    string_id = nc_names.x_var[:(nc_names.x_var.find('_') + 1)]
    for pk, pv in coll_properties.items():
        vname = '{}{}'.format(string_id, pk)
        try:
            dtype = pv.dtype
        except AttributeError:
            dtype = type(pv[0])
        if dtype in (str, unicode):
            dtype = 'S1'
        if dtype == 'S1':
            pv = ['' if v is None else v for v in pv]
            max_char = len(max(pv, key=len))
            dim_name = vname + '_strlen'
            nc.createDimension(dim_name, max_char)
            var = nc.createVariable(
                vname, dtype, dimensions=(INSTANCE_DIM, dim_name))
            for i in range(len(var)):
                var[i] = stringtochar(np.array(pv[i], 'S' + str(max_char)))
        else:
            var = nc.createVariable(vname, dtype, dimensions=(INSTANCE_DIM,))
            var[:] = pv


def copy_nc(src_file, dest_file):
    with Dataset(src_file, 'r') as src, Dataset(dest_file, 'w') as dst:
        for name, dimension in src.dimensions.iteritems():
            dst.createDimension(
                name, len(dimension) if not dimension.isunlimited() else None)

        for name, var in src.variables.items():
            x = dst.createVariable(name, var.datatype, var.dimensions)
            x.setncatts({k: var.getncattr(k) for k in var.ncattrs()})
            x[:] = var[:]

        global_attrs = {k: src.getncattr(k) for k in src.ncattrs()}
        dst.setncatts(global_attrs)


def main():
    # Start with geometry-less example data
    ncgen(IN, OUT_CRA)

    # Read geometries in the same order as instances in the netCDF file
    with Dataset(OUT_CRA, 'r') as nc:
        comids = nc.variables[INSTANCE_DIM][:]
    cf_lines, line_props = get_cf_geometry_collection(
        FLOWLINES, FLOWLINES_SID, comids)
    cf_polys, poly_props = get_cf_geometry_collection(
        CATCHMENTS, CATCHMENTS_SID, comids)

    # Copy data into a file which uses the enhanced data model (for VLEN)
    copy_nc(OUT_CRA, OUT_VLEN)

    # Set netCDF dim and variable names for lines and polygons
    line_names = NcNames()
    line_names.set_prefix('flowlines_')
    poly_names = NcNames()
    poly_names.set_prefix('catchments_')

    # Process both VLEN and CRA
    for out_path, is_cra in zip([OUT_VLEN, OUT_CRA], [False, True]):    
        with Dataset(out_path, 'a') as nc:
            geom_var_name = line_names.container_var
            write_collection(cf_lines, line_names, line_props, is_cra, nc)
            nc.variables['streamflow'].geometry = geom_var_name
            nc.variables['lat'].nodes = line_names.y_var
            nc.variables['lon'].nodes = line_names.x_var
            write_collection(cf_polys, poly_names, poly_props, is_cra, nc)
        ncdump(out_path)


if __name__ == '__main__':
    main()
