import re as _re
import sys as _sys

PY_VER = _sys.version_info[:2]

if PY_VER < (3, 0):
    bytes = str
    str = unicode
    unicode = unicode
    basestring = bytes, unicode
    long = long
    baseinteger = int, long
    xrange = xrange
    import __builtin__ as builtins
else:
    bytes = bytes
    str = str
    unicode = str
    basestring = unicode,
    long = int
    baseinteger = int,
    xrange = range
    import builtins

_bi_ord = builtins.ord

def ord(int_or_char):
    if isinstance(int_or_char, baseinteger):
        return int_or_char
    else:
        return _bi_ord(int_or_char)

def dir(obj, pat=None):
    res = builtins.dir(obj)
    if pat is not None:
        res = [s for s in res if _re.search(pat, s)]
    return res

def zip(*iterables, **kwds):
    for parm in kwds:
        if parm not in ('strict', 'fill'):
            raise TypeError('zip: invalid argument %r' % parm)
    strict = kwds.get('strict', False)
    fill = False
    if 'fill' in kwds:
        if strict:
            raise ValueError('cannot have both strict and fill')
        fill = True
        fill_value = kwds['fill']
    iterables = [iter(it) for it in iterables]
    while "more values possible":
        res = []
        exhausted = []
        for i, it in enumerate(iterables):
            try:
                res.append(next(it))
            except StopIteration:
                if fill:
                    res.append(fill_value)
                exhausted.append(i)
        if exhausted and fill and len(exhausted) != len(iterables):
            yield tuple(res)
            exhausted = []
        elif not exhausted:
            yield tuple(res)
        elif strict and len(exhausted) != len(iterables):
            raise ValueError(
                    'zip argument%s %s %s too short'
                    % (
                        ('','s')[len(exhausted)>1],
                        ', '.join(str(i+1) for i in exhausted),
                        ('is','are')[len(exhausted)>1],
                        ))
        else:
            break
