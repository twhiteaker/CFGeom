from abc import ABCMeta

from ncsg.constants import GeneralAttributes


class AbstractNCSGException(Exception):
    __metaclass__ = ABCMeta

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class NoCoordinateIndexVariablesFoundError(AbstractNCSGException):
    def __init__(self):
        message = 'No coordinate index variables found. Provide a "target" or set the "{}" attribute on the ' \
                  'coordinate index variable to "{}".'.format(GeneralAttributes.CF_ROLE_NAME,
                                                              GeneralAttributes.CF_ROLE_VALUE)
        super().__init__(message)
