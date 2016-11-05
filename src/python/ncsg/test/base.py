import json
import os
import subprocess
from abc import ABCMeta
from unittest.case import TestCase


class AbstractNCSGTest(TestCase):
    __metaclass__ = ABCMeta

    @property
    def fixture_wkt(self):
        with open(self.path_fixture_wkt) as f:
            fw = json.load(f)
        return fw

    @property
    def path_data(self):
        # Change working directories to help test runners like py.test.
        cwd = os.getcwd()
        os.chdir(os.path.split(__file__)[0])
        ret = os.path.join(os.path.realpath('../../../..'), 'data')
        os.chdir(cwd)
        return ret

    @property
    def path_fixture_wkt(self):
        return os.path.join(self.path_data, 'fixture_wkt.json')

    def ncdump(self, path, header=True):
        cmd = ['ncdump']
        if header:
            cmd.append('-h')
        cmd.append(path)
        subprocess.check_call(cmd)
