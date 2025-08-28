import collections
import contextlib
import datetime
import functools
import itertools
import random
import sys
import types

for m in (collections, contextlib, datetime, functools, itertools, random, sys, types):
    sys.modules['enhlib.stdlib.%s' % m.__name__] = m

if sys.version_info < (3, ):
    import __builtin__ as builtins
    import ConfigParser as configparser
    import copy_reg as copyreg
    import cPickle as pickle
    import Queue as queue
    import repr as reprlib
    import SocketServer as socketserver
    import thread as _thread
    import Tkinter as tkinter
    import cStringIO as io
else:
    import builtins
    import configparser
    import copyreg
    import pickle
    import queue
    import reprlib
    import socketserver
    import _thread
    import tkinter
    import io

sys.modules['enhlib.stdlib.configparser'] = configparser
sys.modules['enhlib.stdlib.copyreg'] = copyreg
sys.modules['enhlib.stdlib.pickle'] = pickle
sys.modules['enhlib.stdlib.queue'] = queue
sys.modules['enhlib.stdlib.reprlib'] = reprlib
sys.modules['enhlib.stdlib.socketserver'] = socketserver
sys.modules['enhlib.stdlib._thread'] = _thread
sys.modules['enhlib.stdlib.tkinter'] = tkinter
sys.modules['enhlib.stdlib.io'] = io

if sys.version_info < (3, ):
    class abc(object):
        from collections import Callable
        from collections import Container
        from collections import Counter
        from collections import Hashable
        from collections import ItemsView
        from collections import Iterable
        from collections import Iterator
        from collections import KeysView
        from collections import Mapping
        from collections import MappingView
        from collections import MutableMapping
        from collections import MutableSequence
        from collections import MutableSet
        from collections import OrderedDict
        from collections import Sequence
        from collections import Set
        from collections import Sized
        from collections import ValuesView
    collections.abc = abc()
    sys.modules['enhlib.stdlib.collections.abc'] = collections.abc
else:
    from collections import abc
    sys.modules['enhlib.stdlib.collections.abc'] = abc

if sys.version_info < (3, ):
    range = xrange
    zip = itertools.izip
    input = raw_input
    map = itertools.imap
    sys.intern = intern


# dbm_gnu gdbm dbm.gnu
# dbm_ndbm dbm dbm.ndbm
# _dummy_thread dummy_thread _dummy_thread (< 3.9) _thread (3.9+)
# email_mime_base email.MIMEBase email.mime.base
# email_mime_image email.MIMEImage email.mime.image
# email_mime_multipart email.MIMEMultipart email.mime.multipart
# email_mime_nonmultipart email.MIMENonMultipart email.mime.nonmultipart
# email_mime_text email.MIMEText email.mime.text
# filter itertools.ifilter() filter()
# filterfalse itertools.ifilterfalse() itertools.filterfalse()
# getcwd os.getcwdu() os.getcwd()
# getcwdb os.getcwd() os.getcwdb()
# getoutput commands.getoutput() subprocess.getoutput()
# http_cookiejar cookielib http.cookiejar
# http_cookies Cookie http.cookies
# html_entities htmlentitydefs html.entities
# html_parser HTMLParser html.parser
# http_client httplib http.client
# BaseHTTPServer BaseHTTPServer http.server
# CGIHTTPServer CGIHTTPServer http.server
# SimpleHTTPServer SimpleHTTPServer http.server
# reload_module reload() imp.reload(), importlib.reload() on Python 3.4+
# shlex_quote pipes.quote shlex.quote
# tkinter_dialog Dialog tkinter.dialog
# tkinter_filedialog FileDialog tkinter.FileDialog
# tkinter_scrolledtext ScrolledText tkinter.scrolledtext
# tkinter_simpledialog SimpleDialog tkinter.simpledialog
# tkinter_ttk ttk tkinter.ttk
# tkinter_tix Tix tkinter.tix
# tkinter_constants Tkconstants tkinter.constants
# tkinter_dnd Tkdnd tkinter.dnd
# tkinter_colorchooser tkColorChooser tkinter.colorchooser
# tkinter_commondialog tkCommonDialog tkinter.commondialog
# tkinter_tkfiledialog tkFileDialog tkinter.filedialog
# tkinter_font tkFont tkinter.font
# tkinter_messagebox tkMessageBox tkinter.messagebox
# tkinter_tksimpledialog tkSimpleDialog tkinter.simpledialog
# urllib.parse See six.moves.urllib.parse urllib.parse
# urllib.error See six.moves.urllib.error urllib.error
# urllib.request See six.moves.urllib.request urllib.request
# urllib.response See six.moves.urllib.response urllib.response
# urllib.robotparser robotparser urllib.robotparser
# urllib_robotparser robotparser urllib.robotparser
# UserDict UserDict.UserDict collections.UserDict
# UserList UserList.UserList collections.UserList
# UserString UserString.UserString collections.UserString
# xmlrpc_client xmlrpclib xmlrpc.client
# xmlrpc_server SimpleXMLRPCServer xmlrpc.server
# zip_longest itertools.izip_longest() itertools.zip_longest()
# import _winreg as winreg
# range xrange() range

