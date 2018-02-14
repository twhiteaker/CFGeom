from decimal import Decimal
import numbers

from ncgeom.util import is_iterable


def _as_number(obj):
    if isinstance(obj, numbers.Number):
        return obj
    else:
        return Decimal(obj)


def _as_numeric_iterable(obj):
    if obj is None:
        return []
    elif isinstance(obj, str):
        return [Decimal(obj)]
    elif is_iterable(obj):
        return [_as_number(x) for x in obj]
    else:
        return [_as_number(obj)]
        

def _compute_area(x, y, absoluteValue=True):
    # Uses the shoelace method
    n = len(x)
    if n < 3:
        raise ValueError('At least three points are required to compute area')
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area -= x[i] * y[j]
        area += x[j] * y[i]
    if absoluteValue:
        return abs(area) / 2.0
    else:
        return area / 2.0


def _is_clockwise(x, y):
    try:
        area = _compute_area(x, y, False)
    except:
        # Can't compute area if less than three nodes
        area = 0
    return bool(area > 0)  # Avoid numpy.bool_


class Part(object):
    def __init__(self, x, y, z=None, is_hole=False):
        x = _as_numeric_iterable(x)
        y = _as_numeric_iterable(y)
        z = _as_numeric_iterable(z)
        if not len(x):
            raise ValueError('X value(s) must be provided')
        if not len(y):
            raise ValueError('Y value(s) must be provided')
        if len(x) != len(y):
            raise ValueError('x and y must contain the same number of items')
        if len(z) and len(x) != len(z):
            raise ValueError('x, y, and z must contain the same number of items')
        if not isinstance(is_hole, bool):
            m = 'is_hole must be boolean. Type provided: {0}'.format(
                type(is_hole))
            raise ValueError(m)
        self.x = x
        self.y = y
        self.z = z
        self.is_hole = is_hole
        self._is_clockwise = None


    def is_clockwise(self):
        if self._is_clockwise is None:
            self._is_clockwise = _is_clockwise(self.x, self.y)
        return self._is_clockwise


    def reverse(self):
        self.x = list(reversed(self.x))
        self.y = list(reversed(self.y))
        self.z = list(reversed(self.z))
