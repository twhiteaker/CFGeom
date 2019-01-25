import json
import os
import shutil
import subprocess
import tempfile
from abc import ABCMeta
from unittest.case import TestCase


class AbstractNcgeomTest(TestCase):
    __metaclass__ = ABCMeta
    _prefix_path_test = 'cfgeom_test_'

    def setUp(self):
        self.test_temp_dir = self.get_temporary_output_directory()

    def tearDown(self):
        shutil.rmtree(self.test_temp_dir)

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
        ret = os.path.join(os.path.realpath('../..'), 'data')
        os.chdir(cwd)
        return ret

    @property
    def path_fixture_wkt(self):
        return os.path.join(self.path_data, 'fixture_wkt.json')

    def get_temporary_file_path(self, name):
        """
        :param str name: The name to append to the current temporary output directory.
        :returns: Temporary path in the current output directory.
        :rtype: str
        """

        return os.path.join(self.test_temp_dir, name)

    def get_temporary_output_directory(self):
        """
        :returns: A path to a temporary directory with an appropriate prefix.
        :rtype: str
        """

        return tempfile.mkdtemp(prefix=self._prefix_path_test)

    def ncdump(self, path, header=True):
        cmd = ['ncdump']
        if header:
            cmd.append('-h')
        cmd.append(path)
        subprocess.check_call(cmd)
