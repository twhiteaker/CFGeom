import numpy as np
import pytest

from ... part import Part, _compute_area, _is_clockwise
from .. base import AbstractNcgeomTest


class TestInit(AbstractNcgeomTest):
    def test_init_errors(self):
        with pytest.raises(ValueError):
            part = Part([], [1])
        with pytest.raises(ValueError):
            part = Part([1], None)
        with pytest.raises(ValueError):
            part = Part([1], [1, 1])
        with pytest.raises(ValueError):
            part = Part([1], [1], [1, 1])
        with pytest.raises(ValueError):
            part = Part([1], [1], is_hole='not a boolean')


    def test_init_ok_arrays(self):
        x = [1, 2, 3]
        y = np.array([4, 5, 6])
        z = [7, 8, 9]
        is_hole = True
        part = Part(x, y, z, is_hole=is_hole)
        self.assertEqual(part.x, x)
        self.assertEqual(part.y, list(y))
        self.assertEqual(part.z, z)
        self.assertEqual(part.is_hole, is_hole)
        

    def test_init_ok_scalars(self):
        x = [1]
        y = 2
        part = Part(x, y)
        self.assertEqual(part.x, x)
        self.assertEqual(part.y, [y])
        

class TestEq(AbstractNcgeomTest):
    def test_eq_arrays(self):
        a = np.array([1.0, 2.0])
        b = np.array([1, 2])
        c = [1,2]
        d = [1.0, 2.0]
        y = [1, 1]
        pa = Part(a, y)
        pb = Part(b, y)
        pc = Part(c, y)
        pd = Part(d, y)
        self.assertEqual(pa, pb)
        self.assertEqual(pa, pc)
        self.assertEqual(pc, pb)
        self.assertEqual(pc, pd)


    def test_eq_arrays(self):
        a = np.array([1.0, 2.0])
        b = np.array([3, 2])
        c = [2, 2]
        d = [2, 2, 2]
        y = [1, 1]
        pa = Part(a, y)
        pb = Part(b, y)
        pc = Part(c, y)
        pd = Part(d, [1, 1, 1])
        self.assertNotEqual(pa, pb)
        self.assertNotEqual(pa, pc)
        self.assertNotEqual(pc, pb)
        self.assertNotEqual(pc, pd)


    def test_eq_hole(self):
        a = Part(1, 2, True)
        b = Part(1, 2, True)
        c = Part(1, 2, False)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


class TestArea(AbstractNcgeomTest):
    def test_area_clockwise_convex(self):
        x = [0, 5, 10]
        y = [0, 5, 0]
        self.assertEqual(_compute_area(x, y), 25)


    def test_area_anticlockwise_convex(self):
        x = [10, 5, 0]
        y = [0, 5, 0]
        self.assertEqual(_compute_area(x, y), 25)


    def test_area_clockwise_concave(self):
        x = [1, 1, 4, 3, 4, 1]
        y = [1, 9, 9, 4, 1, 1]
        self.assertEqual(_compute_area(x, y), 20)


    def test_area_anticlockwise_concave(self):
        x = [1, 4, 3, 4, 1, 1]
        y = [1, 1, 4, 9, 9, 1]
        self.assertEqual(_compute_area(x, y), 20)


    def test_area_noabs_clockwise_convex(self):
        x = [0, 5, 10]
        y = [0, 5, 0]
        self.assertEqual(_compute_area(x, y, False), 25)


    def test_area_noabs_anticlockwise_convex(self):
        x = [10, 5, 0]
        y = [0, 5, 0]
        self.assertEqual(_compute_area(x, y, False), -25)


class TestIsClockwise(AbstractNcgeomTest):
    def test_isclockwise_clockwise_convex(self):
        x = [0, 5, 10]
        y = [0, 5, 0]
        self.assertEqual(_is_clockwise(x, y), True)
        part = Part(x, y)
        self.assertEqual(part.is_clockwise(), True)


    def test_isclockwise_anticlockwise_convex(self):
        x = [10, 5, 0]
        y = [0, 5, 0]
        self.assertEqual(_is_clockwise(x, y), False)
        part = Part(x, y)
        self.assertEqual(part.is_clockwise(), False)


    def test_isclockwise_clockwise_concave(self):
        x = [1, 1, 4, 3, 4, 1]
        y = [1, 9, 9, 4, 1, 1]
        self.assertEqual(_is_clockwise(x, y), True)
        part = Part(x, y)
        self.assertEqual(part.is_clockwise(), True)


    def test_isclockwise_anticlockwise_concave(self):
        x = [1, 4, 3, 4, 1, 1]
        y = [1, 1, 4, 9, 9, 1]
        self.assertEqual(_is_clockwise(x, y), False)
        part = Part(x, y)
        self.assertEqual(part.is_clockwise(), False)


class TestReverse(AbstractNcgeomTest):
    def test_reverse(self):
        x = [0, 5, 10]
        y = [0, 5, 0]
        part = Part(x, y)
        part.reverse()
        self.assertEqual(part.x, list(reversed(x)))
