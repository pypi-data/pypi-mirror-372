from __future__ import print_function

from ..contextlib import suppress
from ..csv import CSV
from ..itertools import all_equal, xrange
from ..misc import zip
from ..text import translator
import datetime
import re
import unittest

try:
    from string import letters, digits, lowercase, uppercase
except ImportError:
    from string import ascii_letters as letters, digits, ascii_lowercase as lowercase, ascii_uppercase as uppercase

try:
    from enum import Enum
except ImportError:
    try:
        from aenum import Enum
    except ImportError:
        Enum = None

## globals

class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwds):
        regex = getattr(self, 'assertRaisesRegex', None)
        if regex is None:
            self.assertRaisesRegex = getattr(self, 'assertRaisesRegexp')
        super(TestCase, self).__init__(*args, **kwds)



## tests

class Test_all_equal(TestCase):
    #
    def test_simple_equal(self):
        for items in (
                (1, 1, 1, 1, 1),
                (21, 21, 21),
                [827, 827, 827, 827, 827],
                [None, None],
                [],
                ):
            self.assertTrue(all_equal(items), '%r not all equal?' % (items, ))

    def test_simple_not_equal(self):
        for items in (
                (1, 1, 1, 1, 11),
                (21, 2, 21),
                [3, 827, 827, 827, 827],
                [None, None, False],
                ):
            self.assertFalse(all_equal(items), '%r all equal?' % (items, ))

    def test_function_equal(self):
        for items, func in (
                ((10, 12, 26, 4, 100), lambda x: x % 2 == 0),
                (('abc', 'def', 'ghi'), lambda x: len(x) == 3),
                ([827, 27, 87, 71, 99], lambda x: x % 2 == 1),
                ([None, None], lambda x: x is None),
                ([], lambda x: x is True),
                ):
            self.assertTrue(all_equal(items, func), '%r not all equal?' % (items, ))

    def test_function_not_equal(self):
        for items, func in (
                ((10, 12, 26, 4, 101), lambda x: x % 2 == 0),
                (('abc', 'defg', 'hij'), lambda x: len(x) == 3),
                ([82, 27, 87, 71, 99], lambda x: x % 2 == 1),
                ([None, None, True], lambda x: x is None),
                ):
            self.assertFalse(all_equal(items, func), '%r all equal?' % (items, ))

class Test_suppress(TestCase):
    #
    def test_no_exception(self):
        with suppress(ValueError):
            self.assertEqual(pow(2, 5), 32)

    def test_exact_exception(self):
        with suppress(TypeError):
            len(5)
        with self.assertRaises(AttributeError):
            with suppress(TypeError):
                None.not_here

    def test_multiple_exception_args(self):
        with suppress(ZeroDivisionError, TypeError):
            len(5)
        with suppress(ZeroDivisionError, TypeError):
            5 / 0
        with self.assertRaises(AttributeError):
            with suppress(ZeroDivisionError, TypeError):
                None.not_here

    def test_exception_hierarchy(self):
        with suppress(LookupError):
            'Hello'[50]

class Test_translator(TestCase):
    #
    def test_keep(self):
        alpha = translator(keep=letters)
        self.assertEqual(alpha('ethan7'), 'ethan')
        self.assertEqual(alpha('1234z'), 'z')
        self.assertEqual(alpha('ABCdef'), 'ABCdef')
        self.assertEqual(alpha('1234'), '')

    def test_delete(self):
        no_alpha = translator(delete=letters)
        self.assertEqual(no_alpha('ethan7'), '7')
        self.assertEqual(no_alpha('1234z'), '1234')
        self.assertEqual(no_alpha('ABCdef'), '')
        self.assertEqual(no_alpha('1234'), '1234')
        self.assertEqual(no_alpha('+|%.'), '+|%.')

    def test_to_keep(self):
        replace = translator(to=' ', keep=letters)
        self.assertEqual(replace('ethan7'), 'ethan ')
        self.assertEqual(replace('1234z'), '    z')
        self.assertEqual(replace('ABCdef'), 'ABCdef')
        self.assertEqual(replace('1234'), '    ')
        self.assertEqual(replace('ABC-def'), 'ABC def')

    def test_to_keep_compress(self):
        replace = translator(to=' ', keep=letters, compress=True)
        self.assertEqual(replace('ethan7'), 'ethan')
        self.assertEqual(replace('1234z'), 'z')
        self.assertEqual(replace('ABCdef'), 'ABCdef')
        self.assertEqual(replace('1234'), '')
        self.assertEqual(replace('ABC-def'), 'ABC def')
        self.assertEqual(replace('ABC-def//GhI'), 'ABC def GhI')

    def test_frm_to(self):
        upper = translator(frm=lowercase, to=uppercase)
        self.assertEqual(upper('ethan7'), 'ETHAN7')
        self.assertEqual(upper('1234z'), '1234Z')
        self.assertEqual(upper('ABCdef'), 'ABCDEF')
        self.assertEqual(upper('1234'), '1234')
        self.assertEqual(upper('ABC-def'), 'ABC-DEF')
        self.assertEqual(upper('ABC-def//GhI'), 'ABC-DEF//GHI')

    def test_frm_to_delete(self):
        upper = translator(frm=lowercase, to=uppercase, delete=digits)
        self.assertEqual(upper('ethan7'), 'ETHAN')
        self.assertEqual(upper('1234z'), 'Z')
        self.assertEqual(upper('ABCdef'), 'ABCDEF')
        self.assertEqual(upper('1234'), '')
        self.assertEqual(upper('ABC-def'), 'ABC-DEF')
        self.assertEqual(upper('ABC-def//789...GhI'), 'ABC-DEF//...GHI')


class Test_xrange(TestCase):
    #
    def test_int_iter_forwards(self):
        self.assertEqual(
                list(range(10)),
                list(xrange(10)))
        self.assertEqual(
                list(range(0, 10)),
                list(xrange(0, 10)))
        self.assertEqual(
                list(range(0, 10, 1)),
                list(xrange(0, 10, 1)))
        self.assertEqual(
                list(range(0, 10, 1)),
                list(xrange(0, count=10)))
        self.assertEqual(
                list(range(0, 10, 1)),
                list(xrange(10, step=lambda s, i, v: v+1)))
        self.assertEqual(
                list(range(0, 10, 1)),
                list(xrange(10, step=lambda s, i, v: v+1)))
        self.assertEqual(
                list(range(5, 15)),
                list(xrange(5, count=10)))
        self.assertEqual(
                list(range(-10, 0)),
                list(xrange(-10, 0)))
        self.assertEqual(
                list(range(-9, 1)),
                list(xrange(-9, 1)))
        self.assertEqual(
                list(range(-20, 20, 1)),
                list(xrange(-20, 20, 1)))
        self.assertEqual(
                list(range(-20, 20, 2)),
                list(xrange(-20, 20, 2)))
        self.assertEqual(
                list(range(-20, 20, 3)),
                list(xrange(-20, 20, 3)))
        self.assertEqual(
                list(range(-20, 20, 4)),
                list(xrange(-20, 20, 4)))
        self.assertEqual(
                list(range(-20, 20, 5)),
                list(xrange(-20, 20, 5)))

    def test_int_iter_backwards(self):
        self.assertEqual(
                list(range(9, -1, -1)),
                list(xrange(9, -1, -1)))
        self.assertEqual(
                list(range(9, -9, -1)),
                list(xrange(9, -9, -1)))
        self.assertEqual(
                list(range(9, -9, -2)),
                list(xrange(9, -9, -2)))
        self.assertEqual(
                list(range(9, -9, -3)),
                list(xrange(9, -9, -3)))
        self.assertEqual(
                list(range(9, 0, -1)),
                list(xrange(9, 0, -1)))
        self.assertEqual(
                list(range(9, -1, -1)),
                list(xrange(9, -1, step=-1, count=10)))

    def test_int_containment(self):
        robj = xrange(10)
        for i in range(10):
            self.assertTrue(i in robj, '%d not in %r' % (i, robj))
        self.assertFalse(-1 in robj)
        self.assertFalse(10 in robj)
        self.assertFalse(5.23 in robj)

    def test_float_iter(self):
        floats = [float(i) for i in range(100)]
        self.assertEqual(
                floats,
                list(xrange(100.0, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(0, 100.0, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(0, 100.0, 1.0, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(100.0, step=lambda s, i, v: v + 1.0, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(100.0, step=lambda s, i, v: s + i * 1.0, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(0.0, count=100, epsilon=0.5)),
                repr(xrange(0.0, count=100, epsilon=0.5)))
        self.assertEqual(
                [0.3, 0.6],
                list(xrange(0.3, 0.9, 0.3, epsilon=0.15)))
        self.assertEqual(
                [0.4, 0.8],
                list(xrange(0.4, 1.2, 0.4, epsilon=0.2)))

    def test_float_iter_backwards(self):
        floats = [float(i) for i in range(99, -1, -1)]
        self.assertEqual(
                floats,
                list(xrange(99.0, -1, -1, epsilon=0.5)))
        self.assertEqual(
                floats,
                list(xrange(99.0, step=lambda s, i, v: v - 1.0, count=100, epsilon=0.5)))
        self.assertEqual(
                [0.6, 0.3],
                list(xrange(0.6, 0.0, -0.3, epsilon=0.15)))
        self.assertEqual(
                [0.8, 0.4]
                , list(xrange(0.8, 0.0, -0.4, epsilon=0.2)))

    def test_float_containment(self):
        robj = xrange(10000.0, epsilon=0.5)
        for i in range(0, 10000, 100):
            i = float(i)
            self.assertTrue(i in robj, '%s not in %r' % (i, robj))
        self.assertFalse(0.000001 in robj)
        self.assertFalse(1000000000.0 in robj)
        self.assertFalse(50.23 in robj)

    def test_date_iter(self):
        ONE_DAY = datetime.timedelta(1)
        robj = xrange(datetime.date(2014, 1, 1), step=ONE_DAY, count=31)
        day1 = datetime.date(2014, 1, 1)
        riter = iter(robj)
        for i in range(31):
            day = day1 + i * ONE_DAY
            rday = next(riter)
            self.assertEqual(day, rday)
            self.assertTrue(day in robj)
        self.assertRaises(StopIteration, next, riter)
        self.assertFalse(day + ONE_DAY in robj)

    def test_fraction_iter(self):
        from fractions import Fraction as F
        f = xrange(F(5, 10), count=3)
        self.assertEqual([F(5, 10), F(15, 10), F(25, 10)], list(f))





class Test_datetime(TestCase):
    #
    def test_basics(self):
        from .. import datetime
        datetime.moments


class Test_collections(TestCase):
    #
    def test_basics(self):
        from .. import collections
        collections.OrderedDict

class Test_contextlib(TestCase):
    #
    def test_basics(self):
        from .. import contextlib
        contextlib.suppress


class Test_csv(TestCase):
    #
    def test_plain_data_types(self):
        csv = CSV('test.csv', mode='w')
        data_line = True, False, 7.9, 'hello!', datetime.date(2025, 5, 20)
        csv_line = csv.to_csv(*data_line)
        self.assertEqual(csv_line, """t,f,7.9,"hello!",2025-05-20""")
        self.assertEqual(csv.from_csv(csv_line), data_line)

    def test_custom_data_types(self):
        class Custom(object):
            def __init__(self, value):
                self.value = value
            def __repr__(self):
                return ('Custom(%r)' % self.value)
            def __eq__(self, other):
                if isinstance(other, self.__class__):
                    return self.value == other.value
                return NotImplemented
        #
        def test_custom(text):
            return bool(re.match(r'^Custom[(][^)]*[)]$', text))
        def convert_custom(row, text):
            value ,= re.match(r'^Custom[(]([^)]*)[)]$', text).groups()
            return Custom(eval(value))
        #
        csv = CSV('test.csv', mode='w', custom_types=((test_custom, convert_custom), ))
        data_line = True, False, Custom(7.9), 'hello!', datetime.date(2025, 5, 20)
        csv_line = csv.to_csv(*data_line)
        self.assertEqual(csv_line, """t,f,Custom(7.9),"hello!",2025-05-20""")
        self.assertEqual(csv.from_csv(csv_line), data_line)


class Test_functools(TestCase):
    #
    def test_basics(self):
        from .. import functools
        functools.simplegeneric


class Test_itertools(TestCase):
    #
    def test_basics(self):
        from .. import itertools
        itertools.all_equal
        itertools.grouped
        itertools.grouped_by_column


class Test_random(TestCase):
    #
    def test_basics(self):
        from .. import random
        random.TinyRand


class Test_text(TestCase):
     #
     def test_basics(self):
         from .. import text
         text.translator


class Test_types(TestCase):
    #
    def test_basics(self):
        from .. import types
        types.MISSING


class TestZip(TestCase):
    #
    def test_equal_2(self):
        self.assertEqual(
                list(zip(range(5), range(5, 10))),
                [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)],
                )
    #
    def test_equal_3(self):
        self.assertEqual(
                list(zip(range(5), range(5, 10), range(10, 15))),
                [(0, 5, 10), (1, 6, 11), (2, 7, 12), (3, 8, 13), (4, 9, 14)],
                )
    #
    def test_no_valueerror(self):
        self.assertEqual(
                list(zip(range(4), range(5, 10))),
                [(0, 5), (1, 6), (2, 7), (3, 8)],
                )
    #
    def test_valueerror(self):
        with self.assertRaisesRegex(ValueError, 'zip argument 1 is too short'):
            list(zip(range(4), range(5, 10), strict=True))
    #
    def test_fill(self):
        self.assertEqual(
                list(zip(range(5), range(5, 10), fillvalue=0)),
                [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)],
                )
        self.assertEqual(
                list(zip(range(5), range(5, 10), range(10, 15), fillvalue=0)),
                [(0, 5, 10), (1, 6, 11), (2, 7, 12), (3, 8, 13), (4, 9, 14)],
                )
        self.assertEqual(
                list(zip(range(5), range(5, 8), fillvalue=0)),
                [(0, 5), (1, 6), (2, 7), (3, 0), (4, 0)],
                )
        self.assertEqual(
                list(zip(range(5), range(5, 8), range(10, 11), fillvalue=0)),
                [(0, 5, 10), (1, 6, 0), (2, 7, 0), (3, 0, 0), (4, 0, 0)],
                )



if __name__ == '__main__':
    unittest.main()

