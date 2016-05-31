from shapely import wkt
from shapely.geometry.base import BaseGeometry

from ncsg.test.base import AbstractNCSGTest


class TestFixtures(AbstractNCSGTest):
    def test_fixture_wkt(self):
        """Test WKT fixture may be loaded into Shapely geometries."""

        for d in self.fixture_wkt.values():
            for v in d.values():
                s = wkt.loads(v)
                self.assertIsInstance(s, BaseGeometry)
