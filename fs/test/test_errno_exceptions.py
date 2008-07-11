from nose.tools import (
    eq_ as eq,
    )

from fs.test.util import (
    assert_raises,
    )

import errno
import os

from fs import errno_exceptions

def test_adapt_simple():
    old = OSError(
        errno.ENOENT,
        os.strerror(errno.ENOENT),
        'fake-filename',
        )
    new = errno_exceptions.adapt(old)
    assert type(new) is errno_exceptions.NoSuchFileOrDirectoryError, \
        'New has wrong type: %r' % type(new)
    assert type(new) is errno_exceptions.ENOENT_Error, \
        'New has wrong type: %r' % type(new)
    eq(new.errno, errno.ENOENT)
    eq(new.strerror, os.strerror(errno.ENOENT))
    eq(new.filename, 'fake-filename')
    eq(
        new.args,
        (
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            # EnvironmentError doesn't put filename here, for
            # backwards compat
            ),
        )

def test_wrap_simple():
    @errno_exceptions.wrap
    def broken():
        file('/does-not-exist')

    e = assert_raises(
        errno_exceptions.NoSuchFileOrDirectoryError,
        broken,
        )
    eq(e.errno, errno.ENOENT)
    eq(e.strerror, os.strerror(errno.ENOENT))
    eq(e.filename, '/does-not-exist')
