from ncsg.helpers import reindex
from ncsg.test.base import AbstractNCSGTest


class TestHelpers(AbstractNCSGTest):
    def test_reindex(self):
        cindices = [[0, 1, -1, 2], [0, 1, 2, 3], [0, 1, 2, -8, 3, 4]]

        cindex = reindex(cindices)

        desired_cindex = [[0, 1, -1, 2], [3, 4, 5, 6], [7, 8, 9, -8, 10, 11]]

        self.assertEqual([c.tolist() for c in cindex], desired_cindex)
