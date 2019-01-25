import json
import os
from os.path import join

import pytest

from .... base import AbstractNcgeomTest
from ..... convert.netcdf.nc_reader import read_netcdf


class TestReadNetcdf(AbstractNcgeomTest):
    def test_read_netcdf(self):
        root = join(self.path_data, 'simplified_examples')
        files = [join(root, f) for f in os.listdir(root)
                 if f.endswith('.json')]
        for json_file in files:
            with open(json_file) as f:
                data = json.load(f)
            nc_files = [json_file.replace('.json', '_cra.nc'),
                        json_file.replace('.json', '_vlen.nc')]
            for nc_file in nc_files:
                containers = read_netcdf(nc_file)
                container = containers['geometry_container']['container']
                self.assertEqual(json.loads(container.to_json()), data)

