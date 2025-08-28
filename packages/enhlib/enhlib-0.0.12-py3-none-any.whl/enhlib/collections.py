from __future__ import division, print_function

from .stdlib.collections import OrderedDict
from .types import MISSING


class AttrDict(object):
    """
    allows dictionary lookup using . notation
    allows a default similar to defaultdict
    iterations always ordered by key
    """
    _internal = ['_illegal', '_keys', '_values', '_default', '_ordered']
    _default = None
    _ordered = True
    _illegal = ()
    _values = {}
    _keys = []

    def __init__(self, *args, **kwds):
        "kwds is evaluated last"
        if 'default' in kwds:
            self._default = kwds.pop('default')
        self._ordered = True
        self._keys = []
        self._values = _values = {}
        self._illegal = _illegal = tuple([attr for attr in dir(_values) if attr[0] != '_'])
        if self._default is None:
            default_factory = lambda : False
        else:
            default_factory = self._default
        for arg in args:
            # first, see if it's a lone string
            if isinstance(arg, basestring):
                arg = [(arg, default_factory())]
            elif isinstance(arg, tuple):
                # had better be (name, value)
                arg = [arg, ]
            # next, see if it's a mapping
            elif hasattr(arg, 'items'):
                new_arg = arg.items()
                if isinstance(arg, OrderedDict):
                    pass
                elif isinstance(arg, AttrDict) and arg._ordered:
                    pass
                else:
                    self._ordered = False
                arg = new_arg
            # now iterate over it
            for item in arg:
                if isinstance(item, basestring):
                    key, value = item, default_factory()
                else:
                    key, value = item
                if not isinstance(key, basestring):
                    raise ValueError('keys must be strings, but %r is %r' % (key, type(key)))
                if key in _illegal:
                    raise ValueError('%r is a reserved word' % key)
                _values[key] = value
                if key not in self._keys:
                    self._keys.append(key)
        if kwds:
            self._ordered = False
            _values.update(kwds)
            self._keys = list(set(self._keys + list(kwds.keys())))
        assert set(self._keys) == set(self._values.keys()), "%r is not equal to %r" % (self._keys, self._values.keys())

    def __contains__(self, key):
        return key in self._values

    def __delitem__(self, name):
        if name[0] == '_':
            raise KeyError("illegal key name: %r" % name)
        if name not in self._values:
            raise KeyError("%s: no such key" % name)
        self._values.pop(name)
        self._keys.remove(name)
        assert set(self._keys) == set(self._values.keys())

    def __delattr__(self, name):
        if name[0] == '_':
            raise AttributeError("illegal key name: %r" % name)
        if name not in self._values:
            raise AttributeError("%s: no such key" % name)
        self._values.pop(name)
        self._keys.remove(name)
        assert set(self._keys) == set(self._values.keys())

    def __hash__(self):
        return hash(tuple(sorted(self._keys)))

    def __eq__(self, other):
        try:
            if isinstance(other, AttrDict):
                other = other._values
            elif not isinstance(other, dict):
                return NotImplemented
            return other == self._values
        except UnicodeWarning:
            return False

    def __ne__(self, other):
        result = self == other
        if result is NotImplemented:
            return result
        else:
            return not result

    def __getitem__(self, name):
        if name in self._values:
            return self._values[name]
        elif self._default:
            result = self._values[name] = self._default()
            self._keys.append(name)
            assert set(self._keys) == set(self._values.keys())
            return result
        else:
            raise KeyError(name)

    def __getattr__(self, name):
        if name in self._values:
            return self._values[name]
        attr = getattr(self._values, name, None)
        if attr is not None:
            return attr
        elif self._default:
            result = self._values[name] = self._default()
            self._keys.append(name)
            assert set(self._keys) == set(self._values.keys())
            return result
        else:
            raise AttributeError(name)

    def __iter__(self):
        if self._ordered:
            return iter(self._keys)
        else:
            return iter(sorted(self._keys))

    def __len__(self):
        return len(self._values)

    def __setitem__(self, name, value):
        if name in self._internal:
            object.__setattr__(self, name, value)
        elif isinstance(name, basestring) and name[0:1] == name[-1:] == '_' and name not in ('__module__','__doc__'):
            raise KeyError("illegal attribute name: %r" % name)
        elif not isinstance(name, basestring):
            raise ValueError('attribute names must be str, not %r' % type(name))
        else:
            if name not in self._keys:
                self._keys.append(name)
            self._values[name] = value
        assert set(self._keys) == set(self._values.keys())

    def __setattr__(self, name, value):
        if name in self._internal:
            object.__setattr__(self, name, value)
        elif name in self._illegal or name[0:1] == name[-1:] == '_' and name not in ('__module__','__doc__'):
            raise AttributeError("illegal attribute name: %r" % name)
        elif not isinstance(name, basestring):
            raise ValueError('attribute names must be str, not %r' % type(name))
        else:
            if name not in self._keys:
                self._keys.append(name)
            self._values[name] = value
        assert set(self._keys) == set(self._values.keys()), "%r is not equal to %r" % (self._keys, self._values.keys())

    def __repr__(self):
        cls_name = self.__class__.__name__
        if not self:
            return "%s()" % cls_name
        return "%s(%s)" % (cls_name, ', '.join(["%s=%r" % (k, self._values[k]) for k in self.keys()]))

    def clear(self):
        self._values.clear()
        self._keys[:] = []
        self._ordered = True
        assert set(self._keys) == set(self._values.keys())

    def copy(self):
        result = self.__class__()
        result._illegal = self._illegal
        result._default = self._default
        result._ordered = self._ordered
        result._values.update(self._values.copy())
        result._keys = self._keys[:]
        return result

    @classmethod
    def fromkeys(cls, keys, value):
        return cls([(k, value) for k in keys])

    def items(self):
        return [(k, self._values[k]) for k in self.keys()]

    def keys(self):
        if self._ordered:
            return list(self._keys)
        else:
            return sorted(self._keys)

    def pop(self, key, default=MISSING):
        if default is MISSING:
            value = self._values.pop(key)
        else:
            value = self._values.pop(key, default)
        if key in self._keys:
            self._keys.remove(key)
        assert set(self._keys) == set(self._values.keys())
        return value

    def popitem(self):
        k, v = self._values.popitem()
        self._keys.remove(k)
        assert set(self._keys) == set(self._values.keys())
        return k, v

    def setdefault(self, key, value=MISSING):
        if key not in self._values:
            self._keys.append(key)
        if value is MISSING:
            result = self._values.setdefault(key)
        else:
            result = self._values.setdefault(key, value)
        assert set(self._keys) == set(self._values.keys())
        return result

    def update(self, items=(), **more_items):
        before = len(self._values)
        self._values.update(items, **more_items)
        after = len(self._values)
        if before != after:
            self._keys = self._values.keys()
            self._ordered = False
        assert set(self._keys) == set(self._values.keys())

    def updated(self, items=(), **more_items):
        self.update(items, **more_items)
        return self

    def values(self):
        return [self._values[k] for k in self.keys()]


class BiDict(object):
    """
    key <=> value (value must also be hashable)
    """

    def __init__(self, *args, **kwargs):
        _dict = self._dict = dict()
        original_keys = self._primary_keys = list()
        for k, v in args:
            if k not in original_keys:
                original_keys.append(k)
            _dict[k] = v
            if v != k and v in _dict:
                raise ValueError("%s:%s violates one-to-one mapping" % (k, v))
            _dict[v] = k
        for key, value in kwargs.items():
            if key not in original_keys:
                original_keys.append(key)
            _dict[key] = value
            if value != key and value in _dict:
                raise ValueError("%s:%s violates one-to-one mapping" % (key, value))
            _dict[value] = key

    def __contains__(self, key):
        return key in self._dict

    def __delitem__(self, key):
        _dict = self._dict
        value = _dict[key]
        del _dict[value]
        if key != value:
            del _dict[key]
        target = (key, value)[value in self._primary_keys]
        self._primary_keys.pop(self._primary_keys.index(target))

    def __getitem__(self, key):
        return self._dict.__getitem__(key)

    def __iter__(self):
        return iter(self._primary_keys)

    def __len__(self):
        return len(self._primary_keys)

    def __setitem__(self, key, value):
        _dict = self._dict
        original_keys = self._primary_keys
        if key in _dict:
            mapping = key, _dict[key]
        else:
            mapping = ()
        if value in _dict and value not in mapping:
            raise ValueError("%s:%s violates one-to-one mapping" % (key, value))
        if mapping:
            k, v = mapping
            del _dict[k]
            if k != v:
                del _dict[v]
            target = (k, v)[v in original_keys]
            original_keys.pop(original_keys.index(target))
        _dict[key] = value
        _dict[value] = key
        original_keys.append(key)

    def __repr__(self):
        result = []
        for key in self._primary_keys:
            result.append(repr((key, self._dict[key])))
        return "BiDict(%s)" % ', '.join(result)

    def keys(self):
        return self._primary_keys[:]

    def items(self):
        return [(k, self._dict[k]) for k in self._primary_keys]

    def values(self):
        return [self._dict[key] for key in self._primary_keys]


class TransformDict(dict):
    '''Dictionary that calls a transformation function when looking
    up keys, but preserves the original keys.

    >>> d = TransformDict(str.lower)
    >>> d['Foo'] = 5
    >>> d['foo'] == d['FOO'] == d['Foo'] == 5
    True
    >>> set(d.keys())
    {'Foo'}
    '''

    __slots__ = ('_transform', '_original', '_data')

    def __init__(self, transform, init_dict=None, **kwargs):
        '''Create a new TransformDict with the given *transform* function.
        *init_dict* and *kwargs* are optional initializers, as in the
        dict constructor.
        '''
        if not callable(transform):
            raise TypeError("expected a callable, got %r" % transform.__class__)
        self._transform = transform
        # transformed => original
        self._original = {}
        self._data = {}
        if init_dict:
            self.update(init_dict)
        if kwargs:
            self.update(kwargs)

    def getitem(self, key):
        'D.getitem(key) -> (stored key, value)'
        transformed = self._transform(key)
        original = self._original[transformed]
        value = self._data[transformed]
        return original, value

    @property
    def transform_func(self):
        "This TransformDict's transformation function"
        return self._transform

    # Minimum set of methods required for MutableMapping

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._original.values())

    def __getitem__(self, key):
        return self._data[self._transform(key)]

    def __setitem__(self, key, value):
        transformed = self._transform(key)
        self._data[transformed] = value
        self._original.setdefault(transformed, key)

    def __delitem__(self, key):
        transformed = self._transform(key)
        del self._data[transformed]
        del self._original[transformed]

    # Methods overriden to mitigate the performance overhead.

    def clear(self):
        'D.clear() -> None.  Remove all items from D.'
        self._data.clear()
        self._original.clear()

    def __contains__(self, key):
        return self._transform(key) in self._data

    def get(self, key, default=None):
        'D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.'
        return self._data.get(self._transform(key), default)

    def pop(self, key, default=MISSING):
        '''D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
          If key is not found, d is returned if given, otherwise KeyError is raised.
        '''
        transformed = self._transform(key)
        if default is MISSING:
            del self._original[transformed]
            return self._data.pop(transformed)
        else:
            self._original.pop(transformed, None)
            return self._data.pop(transformed, default)

    def popitem(self):
        '''D.popitem() -> (k, v), remove and return some (key, value) pair
           as a 2-tuple; but raise KeyError if D is empty.
        '''
        transformed, value = self._data.popitem()
        return self._original.pop(transformed), value

    # Other methods

    def copy(self):
        'D.copy() -> a shallow copy of D'
        other = self.__class__(self._transform)
        other._original = self._original.copy()
        other._data = self._data.copy()
        return other

    __copy__ = copy

    def __getstate__(self):
        return (self._transform, self._data, self._original)

    def __setstate__(self, state):
        self._transform, self._data, self._original = state

    def __repr__(self):
        try:
            equiv = dict(self)
        except TypeError:
            # Some keys are unhashable, fall back on .items()
            equiv = list(self.items())
        return '%s(%r, %s)' % (self.__class__.__name__,
                               self._transform, repr(equiv))


