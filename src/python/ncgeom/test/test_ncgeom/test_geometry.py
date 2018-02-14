import pytest

from ncgeom import Geometry, Part
from ncgeom.test.base import AbstractNcgeomTest


point = Part([10], [0])

x = [10, 5, 0]
y = [0, 5, 0]
poly = Part(x, y)

x1 = [9, 5, 1]
y1 = [1, 4, 1]
z1 = [1, 1, 1]
hole = Part(x1, y1, z1, is_hole=True)


class TestInit(AbstractNcgeomTest):
    def test_init_errors(self):
        with pytest.raises(ValueError):
            geom = Geometry('not a geom type', poly)
        with pytest.raises(ValueError):
            geom = Geometry('polygon', [])
        with pytest.raises(ValueError):
            geom = Geometry('polygon', point)
        with pytest.raises(ValueError):
            geom = Geometry('point', poly)
            

    def test_init_hole_cannot_be_first(self):
        with pytest.raises(ValueError):
            geom = Geometry('polygon', hole)


    def test_init_single(self):
        geom = Geometry('line', poly)
        self.assertEqual(len(geom.parts), 1)


    def test_init_multi(self):
        geom = Geometry('line', [poly, poly])
        self.assertEqual(len(geom.parts), 2)


    def test_init_holes_invalid_types(self):
        geom = Geometry('point', point)
        self.assertEqual(geom.has_hole(), False)
        geom = Geometry('line', poly)
        self.assertEqual(geom.has_hole(), False)


class TestHasHole(AbstractNcgeomTest):
    def test_has_hole(self):
        geom = Geometry('polygon', [poly, poly])
        self.assertEqual(geom.has_hole(), False)
        geom = Geometry('polygon', [poly, hole])
        self.assertEqual(geom.has_hole(), True)


class TestIsMultipart(AbstractNcgeomTest):
    def test_is_multipart(self):
        geom = Geometry('polygon', [poly])
        self.assertEqual(geom.is_multipart(), False)
        geom = Geometry('polygon', [poly, poly])
        self.assertEqual(geom.is_multipart(), True)
        geom = Geometry('polygon', [poly, hole])
        self.assertEqual(geom.is_multipart(), False)


class TestHasZ(AbstractNcgeomTest):
    def test_has_z(self):
        geom = Geometry('polygon', poly)
        self.assertEqual(geom.has_hole(), False)
        geom = Geometry('polygon', [poly, hole])
        self.assertEqual(geom.has_hole(), True)
        

class TestOrient(AbstractNcgeomTest):
    def test_orient_point_line(self):
        geom = Geometry('line', poly)
        with pytest.raises(NotImplementedError):
            geom.orient()                
        geom = Geometry('point', point)
        with pytest.raises(NotImplementedError):
            geom.orient()                


    def test_orient_holes_clockwise(self):
        geom = Geometry('polygon', [poly, hole])
        geom.orient(holes_clockwise=True)
        self.assertEqual(geom.parts[0].x, x)
        self.assertEqual(geom.parts[1].x, list(reversed(x1)))
        geom.orient(holes_clockwise=True)
        self.assertEqual(geom.parts[0].y, y)
        self.assertEqual(geom.parts[1].y, list(reversed(y1)))
        geom.orient(holes_clockwise=False)
        self.assertEqual(geom.parts[0].x, list(reversed(x)))
        self.assertEqual(geom.parts[1].x, x1)



