from __future__ import division, print_function



def nested_property(func):
    """
    make defining properties simpler (from Mike Muller) [fget, fset, fdel]

    @nested_property
    def value():
        "doc string here"
        def fget(self):
            pass
        def fset(self, value):
            pass
        return locals()
    """
    names = dict([(n, f) for n, f in func().items() if n in ('fset', 'fget', 'fdel')])
    names['doc'] = func.__doc__
    return property(**names)


try:
    from .stlib.functools import simplegeneric
except ImportError:

    def simplegeneric(func):
        """Make a trivial single-dispatch generic function (from Python3.4 functools)"""
        registry = {}
        def wrapper(*args, **kw):
            ob = args[0]
            try:
                cls = ob.__class__
            except AttributeError:
                cls = type(ob)
            try:
                mro = cls.__mro__
            except AttributeError:
                try:
                    class cls(cls, object):
                        pass
                    mro = cls.__mro__[1:]
                except TypeError:
                    mro = object,   # must be an ExtensionClass or some such  :(
            for t in mro:
                if t in registry:
                    return registry[t](*args, **kw)
            else:
                return func(*args, **kw)
        try:
            wrapper.__name__ = func.__name__
        except (TypeError, AttributeError):
            pass    # Python 2.3 doesn't allow functions to be renamed

        def register(typ, func=None):
            if func is None:
                return lambda f: register(typ, f)
            registry[typ] = func
            return func

        wrapper.__dict__ = func.__dict__
        wrapper.__doc__ = func.__doc__
        wrapper.register = register
        return wrapper


