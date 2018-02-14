import os
from os.path import join

import pytest

from ncgeom.test.base import AbstractNcgeomTest
from ncgeom.io.json_io.json_reader import json_to_container
from ncgeom.io.json_io.json_writer import container_to_json



class TestJson(AbstractNcgeomTest):
    def test_round_trip(self):
        root = join(self.path_data, 'simplified_examples')
        files = [join(root, f) for f in os.listdir(root)
                 if f.endswith('.json')]
        for json_file in files:
            with open(json_file) as f:
                data = f.read()
            container = json_to_container(data)
            self.assertEqual(container.to_json(), data)

