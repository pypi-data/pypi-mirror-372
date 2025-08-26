import sys

IS_PY3 = sys.version_info[0] == 3

if IS_PY3:
    unicode = str
    bytes = bytes
    basestring = str
    xrange = range
