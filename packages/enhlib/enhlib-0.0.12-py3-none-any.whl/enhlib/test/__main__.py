from __future__ import print_function

import shutil
import tempfile
import unittest

from . import test_enhlib

module = globals()
tempdir = tempfile.mkdtemp()

for m in (test_enhlib, ):
    setattr(m, 'tempdir', tempdir)
    for name in dir(m):
        if name != 'TestCase' and name.startswith('Test'):
            module[name] = getattr(m, name)

try:
    unittest.main()
finally:
    shutil.rmtree(tempdir, True)

