import numpy as np

from ncsg.base import AbstractNCSGObject


class ContiguousRaggedArray(AbstractNCSGObject):
    # TODO: Docstring and commenting

    def __init__(self, value, stops, start_index=0):
        self.stops = stops
        self.value = value
        self.start_index = start_index

    def as_vlen(self):
        stops = np.array(self.stops)
        stops -= self.start_index
        ret = []
        for ctr, stop in enumerate(stops):
            stop += 1
            if ctr == 0:
                start = 0
            else:
                start = stops[ctr - 1] + 1
            ret.append(self.value[start:stop])
        return ret

    @classmethod
    def from_vlen(cls, value, start_index=0):
        new_value = []
        current_stop = 0
        stops = []
        for element in value:
            len_element = len(element)
            try:
                to_extend = element.tolist()
            except AttributeError:
                to_extend = element
            new_value += to_extend
            current_stop += len_element
            stops.append(current_stop - 1)
        stops = np.array(stops)
        stops += start_index
        stops = stops.tolist()
        return ContiguousRaggedArray(new_value, stops, start_index=start_index)
