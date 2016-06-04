from abc import ABCMeta

from ncsg.base import AbstractNCSGObject


class AbstractCFGeometry(AbstractNCSGObject):
    __metaclass__ = ABCMeta


class AbstractCFMultipartGeometry(AbstractCFGeometry):
    __metaclass__ = ABCMeta
