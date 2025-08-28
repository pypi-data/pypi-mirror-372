from __future__ import division, print_function


class Sentinel(object):
    """
    When you have to be absolutely sure your object is unique.
    """
    def __init__(self, name, bool=None, doc=''):
        self.name = name
        self.__doc__ = doc
        self.__bool = bool

    def __repr__(self):
        return "<%r>" % self.name

    def __bool__(self):
        if self.__bool is None:
            raise NotImplementedError('Sentinel %r has no boolean value' % self.name)
        return self.__bool
    __nonzero__ = __bool__


MISSING = Sentinel('MISSING', doc="argument not provided by caller")
