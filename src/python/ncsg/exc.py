from abc import ABCMeta

from ncsg.constants import GeneralAttributes


class AbstractNCSGException(Exception):
    __metaclass__ = ABCMeta

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class NoGeometryContainerVariablesFoundError(AbstractNCSGException):
    def __init__(self):
        message = ('No geometry variables found. Provide a "target" or assign '
                   '"{}" and "{}" attributes on the geometry variable.').format(
                       GeneralAttributes.GEOM_TYPE_NAME,
                       GeneralAttributes.COORDINATES)
        super(NoGeometryContainerVariablesFoundError, self).__init__(message)
