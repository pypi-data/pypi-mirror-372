from __future__ import division, print_function

from .types import MISSING

def translator(frm=u'', to=u'', delete=u'', keep=u'', strip=MISSING, compress=False):
    # delete and keep are mutually exclusive
    if delete and keep:
        raise ValueError('cannot specify both keep and delete')
    replacement = replacement_ord = None
    if len(to) == 1:
        if frm == u'':
            replacement = to
            replacement_ord = ord(to)
            to = u''
        else:
            to = to * len(frm)
    if len(to) != len(frm):
        raise ValueError('frm and to should be equal lengths (or to should be a single character)')
    uni_table = dict(
            (ord(f), ord(t))
            for f, t in zip(frm, to)
            )
    for ch in delete:
        uni_table[ord(ch)] = None
    def translate(s):
        if isinstance(s, bytes):
            s = s.decode('latin1')
        s = s.translate(uni_table)
        if keep:
            remove_table = {}
            for chr in set(s) - set(keep):
                remove_table[ord(chr)] = replacement_ord
            s = s.translate(remove_table)
        if strip is not MISSING:
            s = s.strip(strip)
        if replacement and compress:
            s = replacement.join([p for p in s.split(replacement) if p])
        return s
    return translate



