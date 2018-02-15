"""Represents a single geometry part."""

from decimal import Decimal
import numbers

from . util import is_iterable


def _as_number(obj):
    """Converts the input object to a number if it is not already a number.

    If the input object is a number, it is returned as is.  Otherwise, it is
    converted to a number and returned.

    Args:
        obj: The object to convert to a number if it is not already a number.

    Returns:
        The input object if it was already a number, or the object converted to
        a number otherwise.

    """
    if isinstance(obj, numbers.Number):
        return obj
    else:
        return Decimal(obj)


def _as_numeric_iterable(obj):
    """Returns an iterable object containing numbers from the input object.

    If the input object is None, an empty list is returned.
    If the input object is a string, it is converted to a number and returned
    in a list.
    If the input object is iterable, a new list is generated with each item in
    the object converted to a number.
    Otherwise, the object is converted to a number and returned in a new list.

    Args:
        obj: The object to convert to a numeric iterable object.

    Returns:
        list: A list containing the input object(s) converted to a number.

    """
    if obj is None:
        return []
    elif isinstance(obj, str):
        return [Decimal(obj)]
    elif is_iterable(obj):
        return [_as_number(x) for x in obj]
    else:
        return [_as_number(obj)]
        

def _compute_area(x, y, absoluteValue=True):
    """Computes area, presumably of a polygon.

    Computes area using the shoelace method.  If nodes are oriented in a
    clockwise fashion, the computed area is positive; otherwise, the area
    is negative.

    Args:
        x (array-like): X coordinates of the geometry part.
        y (array-like): Y coordinates of the geometry part.
        absoluteValue (bool): True if the absolute value of the area should be
            returned; False if negative values are allowed.  Use False to
            determine node orientation. Use True to compute area regardless of
            orientation.

    Returns:
        float: Area.

    Raises:
        ValueError: If less than three nodes are provided.

    """
    n = len(x)
    if n < 3:
        raise ValueError('At least three nodes are required to compute area')
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
    """Determines if node orientation is clockwise.

    Args:
        x (array-like): X coordinates of the geometry part.
        y (array-like): Y coordinates of the geometry part.

    Returns:
        bool: True if nodes are oriented clockwise, False otherwise. If there
        are less than three nodes, False is returned.

    """
    try:
        area = _compute_area(x, y, False)
    except:
        # Can't compute area if less than three nodes
        area = 0
    return bool(area > 0)  # Avoid numpy.bool_


class Part(object):
    """Contains vertices for a single geometry part.

    Attributes:
        x (array-like): X coordinates of the geometry part.
        y (array-like): Y coordinates of the geometry part.
        z (array-like): Z coordinates of the geometry part, if any.
        is_hole (bool): True if part is a polygon hole, False otherwise.

    """
    
    def __init__(self, x, y, z=None, is_hole=False):
        """Inits Part with coordinates.

        Args:
            x (array-like): X coordinates of the geometry part.
            y (array-like): Y coordinates of the geometry part.
            z (array-like, optional): Z coordinates of the geometry part.
            is_hole (bool, optional): True if part is a polygon hole, False
                otherwise.

        Raises:
            ValueError: If x or y values are not provided, or if x, y, and
                z (if provided) arrays are not of the same length, or if
                is_hole is not a boolean.

        """
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
        """Determines if nodes are oriented clockwise.

        Returns:
            bool: True if nodes are oriented clockwise, False otherwise.

        """
        if self._is_clockwise is None:
            self._is_clockwise = _is_clockwise(self.x, self.y)
        return self._is_clockwise


    def reverse(self):
        """Reverses node order in-place."""
        self.x = list(reversed(self.x))
        self.y = list(reversed(self.y))
        self.z = list(reversed(self.z))
