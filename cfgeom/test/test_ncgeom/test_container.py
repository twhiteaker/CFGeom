import pytest

from ... import GeometryContainer, Geometry, Part
from .. base import AbstractNcgeomTest


point = Geometry('point', Part([10], [0]))

x = [10, 5, 0]
y = [0, 5, 0]
poly = Geometry('polygon', Part(x, y))
line = Geometry('line', Part(x, y))

x1 = [9, 5, 1]
y1 = [1, 4, 1]
z1 = [1, 1, 1]
poly2 = Geometry('polygon', Part(x1, y1, z1))

parts = [Part(x, y), Part(x1, y1, z1, is_hole=True)]
poly_hole = Geometry('polygon', parts)


class TestInit(AbstractNcgeomTest):
    def test_init_errors(self):
        with pytest.raises(ValueError):
            container = GeometryContainer([])
        with pytest.raises(ValueError):
            container = GeometryContainer([point, poly])
            

    def test_init_ok(self):
        geoms = [poly, poly2, poly_hole]
        container = GeometryContainer(geoms)
        self.assertEqual(len(container.geoms), 3)


class TestEq(AbstractNcgeomTest):
    def test_eq(self):
        a = Geometry('point', Part(1, 1))
        b = Geometry('point', Part(1, 1))
        c = Geometry('point', Part(2, 1))
        ca = GeometryContainer(a)
        cb = GeometryContainer(b)
        cc = GeometryContainer(c)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


class TestHasHole(AbstractNcgeomTest):
    def test_has_hole(self):
        container = GeometryContainer([poly, poly])
        self.assertEqual(container.has_hole(), False)
        container = GeometryContainer([poly, poly_hole])
        self.assertEqual(container.has_hole(), True)


class TestIsMultipart(AbstractNcgeomTest):
    def test_is_multipart(self):
        container = GeometryContainer([poly, poly2])
        self.assertEqual(container.is_multipart(), False)
        geom = Geometry('point', Part([10], [0]))
        container = GeometryContainer(geom)
        self.assertEqual(container.is_multipart(), False)
        container = GeometryContainer([geom, geom])
        self.assertEqual(container.is_multipart(), False)
        multi = Geometry('point', [Part([10], [0]), Part([1], [2])])
        container = GeometryContainer([geom, multi])
        self.assertEqual(container.is_multipart(), True)


class TestHasZ(AbstractNcgeomTest):
    def test_has_z(self):
        container = GeometryContainer([poly])
        self.assertEqual(container.has_hole(), False)
        container = GeometryContainer([poly, poly_hole])
        self.assertEqual(container.has_hole(), True)
        

class TestWktType(AbstractNcgeomTest):
    def test_wkt_type(self):
        container = GeometryContainer([poly, poly2])
        self.assertEqual(container.wkt_type(), 'Polygon')

        container = GeometryContainer(line)
        self.assertEqual(container.wkt_type(), 'LineString')

        geom = Geometry('point', Part([10], [0]))
        multi = Geometry('point', [Part([10], [0]), Part([1], [2])])
        container = GeometryContainer([geom, multi])
        self.assertEqual(container.wkt_type(), 'MultiPoint')

