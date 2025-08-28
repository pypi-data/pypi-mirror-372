from __future__ import division, print_function


class suppress(object):
    "suppresses first execption and exits the with block"
    def __init__(self, *exceptions):
        self.exceptions = exceptions
    def __enter__(self):
        pass
    def __exit__(self, etype, val, tb):
        return etype is None or issubclass(etype, self.exceptions)


