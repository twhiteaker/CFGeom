"""Convert example geometries from JSON files to netCDF and CDL."""

import os
import subprocess
import sys


sys.path.append(os.path.abspath('../src/python'))
from ncgeom import read_json

FOLDER = '../data/simplified_examples'


def ncdump(src):
    dest = src[:-3] + '.cdl'
    shell = os.name == 'nt'  # Use shell=True for commands on Windows
    cmd = ['ncdump']
    cmd.append(os.path.abspath(src))
    cmd.append('>')
    cmd.append(os.path.abspath(dest))
    return str(subprocess.check_output(cmd, shell=shell))
    

def main():
    files = [os.path.join(FOLDER, f) for f in os.listdir(FOLDER)
             if f.endswith('.json')]
    for json_file in files:
        print json_file
        with open(json_file) as f:
            data = f.read().replace('\n', '')
        container = read_json(data)
        filename = json_file[:-5] + '_cra.nc'
        container.to_netcdf(filename, use_vlen=False)
        ncdump(filename)
        filename = json_file[:-5] + '_vlen.nc'
        container.to_netcdf(filename, use_vlen=True)
        ncdump(filename)


if __name__ == '__main__':
    main()
