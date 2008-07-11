import errno
import os
import string

class ErrnoException(Exception):
    """
    Base class for all errno-based exceptions.
    """

    def __init__(self, original):
        self.original = original
        self.args = original.args
        self.filename = original.filename

    def __str__(self):
        return os.strerror(self.errno)

_ALLOWED = string.ascii_letters + string.digits

def _munge_name(s):
    result = ''.join(
        ''.join(c for c in word if c in _ALLOWED).capitalize()
        for word in s.split(None)
        )
    return result

def _init(errors):
    for num, abbrev in errors.items():
        errstr = os.strerror(num)
        classname = '%sError' % _munge_name(errstr)
        class_ = type(
            classname,
            (ErrnoException,),
            dict(
                errno=num,
                strerror=errstr
                ),
            )
        globals()[classname] = class_
        globals()['%s_Error' % abbrev] = class_

_init(errno.errorcode)

def adapt(e):
    if not isinstance(e, EnvironmentError):
        # we only handle exceptions known to always have errno
        return e

    if isinstance(e, ErrnoException):
        # already wrapped
        return e

    abbrev = errno.errorcode.get(e.errno)
    if abbrev is None:
        # dunno what happened, but can't map it
        return e

    class_ = globals().get('%s_Error' % abbrev)
    if class_ is None:
        # dunno what happened, but can't map it
        return e

    new = class_(e)
    return new

def wrap(fn):
    def handle(*a, **kw):
        try:
            return fn(*a, **kw)
        except EnvironmentError, e:
            raise adapt(e)
    return handle
