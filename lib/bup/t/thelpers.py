import math
import os
import bup._helpers as _helpers
from bup.helpers import *
from wvtest import *

@wvtest
def test_parse_num():
    pn = parse_num
    WVPASSEQ(pn('1'), 1)
    WVPASSEQ(pn('0'), 0)
    WVPASSEQ(pn('1.5k'), 1536)
    WVPASSEQ(pn('2 gb'), 2*1024*1024*1024)
    WVPASSEQ(pn('1e+9 k'), 1000000000 * 1024)
    WVPASSEQ(pn('-3e-3mb'), int(-0.003 * 1024 * 1024))


@wvtest
def test_find_sparse_region():
    find_sparse_region = _helpers.find_sparse_region
    WVPASSEQ(find_sparse_region('', 0, 1), (0, 0))
    WVEXCEPT(OverflowError, find_sparse_region, '', 1, 1)
    WVEXCEPT(OverflowError, find_sparse_region, '', -1, 1)
    WVPASSEQ(find_sparse_region('xyz', 0, 0), (3, 0))
    WVPASSEQ(find_sparse_region('xyz', 1, 0), (2, 0))
    WVPASSEQ(find_sparse_region('xyz', 3, 0), (0, 0))
    WVPASSEQ(find_sparse_region('\x00\x00\x00', 0, 0), (0, 3))
    WVPASSEQ(find_sparse_region('\x00\x00\x00', 0, 4), (0, 3))
    WVPASSEQ(find_sparse_region('x\x00\x00\x00', 0, 4), (1, 3))
    WVPASSEQ(find_sparse_region('\x00\x00\x00xyz', 0, 0), (0, 3))
    WVPASSEQ(find_sparse_region('xyz\x00\x00\x00', 0, 0), (3, 3))
    WVPASSEQ(find_sparse_region('xyz\x00\x00\x00', 4, 0), (0, 2))
    WVPASSEQ(find_sparse_region('xyz\x00\x00\x00', 4, 4), (0, 2))
    WVPASSEQ(find_sparse_region('xyz\x00\x00\x00xyz', 0, 4), (9, 0))

@wvtest
def test_detect_fakeroot():
    if os.getenv('FAKEROOTKEY'):
        WVPASS(detect_fakeroot())
    else:
        WVPASS(not detect_fakeroot())

@wvtest
def test_path_components():
    WVPASSEQ(path_components('/'), [('', '/')])
    WVPASSEQ(path_components('/foo'), [('', '/'), ('foo', '/foo')])
    WVPASSEQ(path_components('/foo/'), [('', '/'), ('foo', '/foo')])
    WVPASSEQ(path_components('/foo/bar'),
             [('', '/'), ('foo', '/foo'), ('bar', '/foo/bar')])
    WVEXCEPT(Exception, path_components, 'foo')


@wvtest
def test_stripped_path_components():
    WVPASSEQ(stripped_path_components('/', []), [('', '/')])
    WVPASSEQ(stripped_path_components('/', ['']), [('', '/')])
    WVPASSEQ(stripped_path_components('/', ['/']), [('', '/')])
    WVPASSEQ(stripped_path_components('/', ['/foo']), [('', '/')])
    WVPASSEQ(stripped_path_components('/foo', ['/bar']),
             [('', '/'), ('foo', '/foo')])
    WVPASSEQ(stripped_path_components('/foo', ['/foo']), [('', '/foo')])
    WVPASSEQ(stripped_path_components('/foo/bar', ['/foo']),
             [('', '/foo'), ('bar', '/foo/bar')])
    WVPASSEQ(stripped_path_components('/foo/bar', ['/bar', '/foo', '/baz']),
             [('', '/foo'), ('bar', '/foo/bar')])
    WVPASSEQ(stripped_path_components('/foo/bar/baz', ['/foo/bar/baz']),
             [('', '/foo/bar/baz')])
    WVEXCEPT(Exception, stripped_path_components, 'foo', [])


@wvtest
def test_grafted_path_components():
    WVPASSEQ(grafted_path_components([('/chroot', '/')], '/foo'),
             [('', '/'), ('foo', '/foo')])
    WVPASSEQ(grafted_path_components([('/foo/bar', '/')], '/foo/bar/baz/bax'),
             [('', '/foo/bar'),
              ('baz', '/foo/bar/baz'),
              ('bax', '/foo/bar/baz/bax')])
    WVPASSEQ(grafted_path_components([('/foo/bar/baz', '/bax')],
                                     '/foo/bar/baz/1/2'),
             [('', None),
              ('bax', '/foo/bar/baz'),
              ('1', '/foo/bar/baz/1'),
              ('2', '/foo/bar/baz/1/2')])
    WVPASSEQ(grafted_path_components([('/foo', '/bar/baz/bax')],
                                     '/foo/bar'),
             [('', None),
              ('bar', None),
              ('baz', None),
              ('bax', '/foo'),
              ('bar', '/foo/bar')])
    WVPASSEQ(grafted_path_components([('/foo/bar/baz', '/a/b/c')],
                                     '/foo/bar/baz'),
             [('', None), ('a', None), ('b', None), ('c', '/foo/bar/baz')])
    WVPASSEQ(grafted_path_components([('/', '/a/b/c/')], '/foo/bar'),
             [('', None), ('a', None), ('b', None), ('c', '/'),
              ('foo', '/foo'), ('bar', '/foo/bar')])
    WVEXCEPT(Exception, grafted_path_components, 'foo', [])
