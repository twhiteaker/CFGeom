"""General utilities.

This module includes functions that may be of general use to other modules.
"""

def is_iterable(obj):
    """Determines if input object is iterable.

    Args:
        obj: The object to check.

    Returns:
        bool: True if iterable, False otherwise.

    """
    try:
        iter(obj)
        return True
    except:
        return False


def as_iterable(obj):
    """Returns an iterable object from the input object.

    If the input object is iterable, it is returned as is.  Otherwise, it is
    placed inside a list, and the list is returned.

    Args:
        obj: The object to convert to an iterable object if needed.

    Returns:
        The input object, either as itself if it was already iterable, or as a
        member of a new list otherwise.

    """
    if is_iterable(obj):
        return obj
    else:
        return [obj]
