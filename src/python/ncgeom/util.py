def is_iterable(obj):
    try:
        iter(obj)
        return True
    except:
        return False


def as_iterable(obj):
    if is_iterable(obj):
        return obj
    else:
        return [obj]
