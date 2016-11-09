import numpy as np


def reindex(cindices):
    """
    :param cindices: Sequence of vector coordinate index arrays. A coordinate index array is a vector integer array.
    :type cindices: sequence
    :return: Tuple of coordinate index arrays with integer indices updated to match their new index location in a
     stacked context.
    :rtype: tuple
    """

    cindices_lengths = [sum(np.array(c) >= 0) for c in cindices]
    adjust = [None] * len(cindices_lengths)
    for idx in range(len(adjust)):
        if idx == 0:
            a = 0
        else:
            a = cindices_lengths[idx - 1] + adjust[idx - 1]
        adjust[idx] = a

    cindices_adjusted = [None] * len(cindices_lengths)
    for idx in range(len(cindices_adjusted)):
        cindices_arr = np.array(cindices[idx])
        ca = cindices_arr.copy()
        breaks = ca < 0
        ca += adjust[idx]
        ca[breaks] = cindices_arr[breaks]
        cindices_adjusted[idx] = ca

    return tuple(cindices_adjusted)


def stack_vectors(carrays):
    dtype = np.array(carrays[0][0]).dtype
    size = sum([len(c) for c in carrays])
    ret = np.zeros(size, dtype=dtype)
    start = 0
    for c in carrays:
        c = np.array(c)
        assert c.ndim == 1
        ret[start: start + c.shape[0]] = c
        start += c.shape[0]
    return ret
