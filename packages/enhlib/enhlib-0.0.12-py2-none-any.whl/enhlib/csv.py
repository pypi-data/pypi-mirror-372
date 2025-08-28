from __future__ import division, print_function

from .collections import AttrDict
import codecs
import datetime
from .misc import basestring, unicode
import re


enums = ()
try:
    import aenum as _aenum
    enums += _aenum.Enum,
except ImportError:
    pass
try:
    import enum as _enum
    enums += _enum.Enum,
except ImportError:
    pass


class CSVError(Exception):
    """
    generic csv error
    """

class CSV(object):
    """
    represents a .csv file
    """
    _str = unicode
    _date = datetime.date
    _time = datetime.time
    _datetime = datetime.datetime
    _bool = bool
    _float = float
    _int = int
    _none = lambda s: None

    def __init__(self, filename, mode='r', header=True, types={}, default_type=None, custom_types=None):
        """
        filename: name of csv file to either read or write
        mode: open mode to use with file; defaults to `'r'`
        header: first line of read file is header?  default is `True`
        types: types to use for std data types
        default_type: type to use if known types fail; default is raise an exception
        custom_types: tuple of `(test(text), convert(col#, text))` functions
        """
        if mode not in ('r','w'):
            raise ValueError("mode must be 'r' or 'w', not %r" % (mode, ))
        for n, t in types.items():
            if n not in (
                    'bool', 'float', 'int', 'str',
                    'date', 'time', 'datetime',
                    ):
                raise TypeError('CSV: data type invalid-> %r' % (n, ))
            setattr(self, '_'+n, t)
        self.filename = filename
        self.mode = mode
        self.default_type = default_type
        self.custom_types = custom_types or ()
        if mode == 'r':
            with codecs.open(filename, mode='r', encoding='utf-8') as csv:
                raw_data = csv.read().split('\n')
            if header:
                self.header = raw_data.pop(0).strip().split(',')
            else:
                self.header = []
            self.data = [l.strip() for l in raw_data if l.strip()]
        else:
            self.header = []
            self.data = []
        if not header:
            self.header = []


    def __enter__(self):
        return self

    def __exit__(self, *args):
        if args == (None, None, None) and self.mode == 'w':
            self.save()

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.from_csv(self.data[index])
        # better be a slice
        lines = []
        for line in self.data[index]:
            lines.append(self.from_csv(line))
        return lines

    def __iter__(self):
        """
        returns data rows (not header)
        """
        for line in self.data:
            yield self.from_csv(line)

    def __len__(self):
        return len(self.data)

    def append(self, *values):
        if isinstance(values[0], (list, tuple)):
            values = tuple(values[0])
        if self.header and len(values) != len(self.header):
            raise ValueError('%d fields required, %d value(s) given' % (len(self.header), len(values)))
        line = self.to_csv(*values)
        new_values = self.from_csv(line)
        if values != new_values:
            print(len(values), len(new_values))
            print(line)
            print(values)
            print(new_values)
            raise ValueError("%r != %r" % (values, new_values))
        self.data.append(line)

    def from_csv(self, line):
        """
        returns a tuple of converted data from `line`

        supported types:

        date        : nnnn-nn-nn
        datetime    : nnnn-nn-nn nn:nn:nn
        time        : nn:nn:nn
        int         : non-quoted number with no fractions
        float       : non-quoted number with fraction
        bool        : true, yes, on, t / false, no, off, f
        unicode     : "anything else"
        """
        # break line into fields
        fields = []
        word = []
        encap = False
        parens = 0
        skip_next = False
        keep_next = False
        for i, ch in enumerate(line):
            if skip_next:
                skip_next = False
                continue
            elif keep_next:
                keep_next = False
                word.append(ch)
                continue
            elif encap:
                if ch == '"' and line[i+1:i+2] == '"':
                    word.append(ch)
                    skip_next = True
                elif ch =='"' and line[i+1:i+2] in ('', ','):
                    word.append(ch)
                    encap = False
                elif ch == '\\':
                    if line[i+1:i+2] == 'n':
                        word.append('\n')
                        skip_next = True
                    else:
                        keep_next = True
                elif ch == '"':
                    raise ValueError(
                            'invalid char following ": <%s> (should be comma or double-quote)\n%r\n%s^'
                            % (ch, line, ' ' * i)
                            )
                else:
                    word.append(ch)
            elif ch == '(':
                word.append(ch)
                parens += 1
            elif ch == ')':
                word.append(ch)
                parens -= 1
                if parens < 0:
                    raise ValueError('unbalanced parentheses in:\n%r' % line)
            else:
                if ch == ',' and not parens:
                    fields.append(''.join(word))
                    word = []
                elif ch == '"':
                    if word: # embedded " are not allowed
                        raise ValueError('embedded quotes not allowed:\n%s\n%s' % (line[:i], line))
                    encap = True
                    word.append(ch)
                else:
                    word.append(ch)
        if parens:
            raise ValueError('unbalanced parentheses in:\n%r' % line)
        # don't lose last field!
        fields.append(''.join(word))
        #
        # convert fields to their data types
        final = []
        for i, field in enumerate(fields):
            try:
                if not field:
                    final.append(self._none)
                    continue
                for test, convert in self.custom_types:
                    if test(field):
                        final.append(convert(i, field))
                        break
                else:
                    if field[0] == field[-1] and field[0] in ('"',"'"):
                        # simple string
                        final.append(self._str(field[1:-1]))
                    elif field.lower() in ('true','yes','on','t'):
                        final.append(self._bool(True))
                    elif field.lower() in ('false','no','off','f'):
                        final.append(self._bool(False))
                    elif '-' in field and ':' in field:
                        # TODO: use a re instead and support time zones
                        try:
                            year, month, day, hour, minute, second = map(
                                    int,
                                    re.match(r'^(\d+)-(\d+)-(\d+).(\d+):(\d+):(\d+)$', field).groups()
                                    )
                            final.append(self._datetime(year, month, day, hour, minute, second))
                        except Exception:
                            raise CSVError('invalid datetime value: %r' % (field, ))
                    elif '-' in field:
                        # final.append(self._date.strptime(field, '%Y-%m-%d'))
                        try:
                            year, month, day, = map(
                                    int,
                                    re.match(r'^(\d+)-(\d+)-(\d+)$', field).groups()
                                    )
                            final.append(self._date(year, month, day))
                        except Exception:
                            raise CSVError('invalid date value: %r' % (field, ))
                    elif ':' in field:
                        # final.append(self._time.strptime(field, '%H:%M:%S'))
                        try:
                            year, month, day, = map(
                                    int,
                                    re.match(r'^(\d+):(\d+):(\d+)$', field).groups()
                                    )
                            final.append(self._date(year, month, day))
                        except Exception:
                            raise CSVError('invalid time value: %r' % (field, ))
                    else:
                        try:
                            final.append(self._int(field))
                        except ValueError:
                            final.append(self._float(field))
            except ValueError:
                if self.default_type is not None:
                    final.append(self.default_type(field))
                else:
                    ve = ValueError('unable to determine datatype of <%r>' % (field, ))
                    ve.__cause__ = None
                    raise ve
        return tuple(final)

    def iter_map(self, header=None):
        header = self.header or header
        if not header:
            raise ValueError('header needed for iter_map()')
        for record in self:
            yield AttrDict(zip(self.header, record))

    def save(self, filename=None):
        if filename is None:
            filename = self.filename
        with codecs.open(filename, mode='w', encoding='utf-8') as csv:
            if self.header:
                # write the header
                csv.write(','.join(self.header) + '\n')
            # write the data
            for line in self.data:
                csv.write(line + '\n')

    def to_csv(self, *data):
        """
        convert data to text and add to CSV

        supported types:

        unicode       : "str and unicode"
        date          : nnnn-nn-nn
        datetime      : nnnn-nn-nn nn:nn:nn
        time          : nn:nn:nn
        bool          : true, yes, on, t / false, no, off, f
        anything else : repr()
        """
        line = []
        for datum in data:
            if datum is None or datum == '':
                line.append('')
            elif isinstance(datum, basestring):
                datum = datum.replace('"','""').replace('\\','\\\\').replace('\n',r'\n')
                line.append('"%s"' % datum)
            elif isinstance(datum, (datetime.datetime, self._datetime)):
                line.append(datum.strftime('%Y-%m-%d %H:%M:%S'))
            elif isinstance(datum, (datetime.date, self._date)):
                line.append(datum.strftime('%Y-%m-%d'))
            elif isinstance(datum, (datetime.time, self._time)):
                line.append(datum.strftime('%H:%M:%S'))
            elif isinstance(datum, (bool, self._bool)):
                line.append('ft'[datum])
            elif isinstance(datum, enums):
                line.append(repr(datum.value))
            else:
                line.append(repr(datum))
        return ','.join(line)

    def to_stream(self):
        utf8 = codecs.getencoder('utf-8')
        yield utf8(','.join(self.header) + '\n')
        for line in self.data:
            yield utf8(line + '\n')

