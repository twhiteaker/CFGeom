import os
from os.path import join

import pytest

from .... base import AbstractNcgeomTest
from ..... convert.json_io.json_reader import json_to_container
from ..... convert.json_io.json_writer import container_to_json



class TestJson(AbstractNcgeomTest):
    def compare_from_file(self, json_file):
        root = join(self.path_data, 'simplified_examples')
        filename = join(root, json_file)
        with open(filename) as f:
            data = f.read()
        container = json_to_container(data)
        self.assertEqual(container.to_json(), data)


    def test_point_z(self):
        self.compare_from_file('point_z.json')

    def test_multipoint(self):
        self.compare_from_file('multipoint.json')

    def test_line(self):
        self.compare_from_file('line.json')

    def test_line_z(self):
        self.compare_from_file('line_z.json')

    def test_multiline(self):
        self.compare_from_file('multiline.json')

    def test_polygon(self):
        self.compare_from_file('polygon.json')

    def test_polygon_hole(self):
        self.compare_from_file('polygon_hole.json')

    def test_multipolygon(self):
        self.compare_from_file('multipolygon.json')
