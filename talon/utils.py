# coding:utf-8

import logging
from random import shuffle

from talon.constants import RE_DELIMITER


log = logging.getLogger(__name__)


def safe_format(format_string, *args, **kwargs):
    """
    Helper: formats string with any combination of bytestrings/unicode
    strings without raising exceptions
    """
    try:
        if not args and not kwargs:
            return format_string
        else:
            return format_string.format(*args, **kwargs)

    # catch encoding errors and transform everything into utf-8 string
    # before logging:
    except (UnicodeEncodeError, UnicodeDecodeError):
        format_string = to_utf8(format_string)
        args = [to_utf8(p) for p in args]
        kwargs = {k: to_utf8(v) for k, v in kwargs.iteritems()}
        return format_string.format(*args, **kwargs)

    # ignore other errors
    except:
        return u''


def to_unicode(str_or_unicode, precise=False):
    """
    Safely returns a unicode version of a given string
    >>> utils.to_unicode('привет')
        u'привет'
    >>> utils.to_unicode(u'привет')
        u'привет'
    If `precise` flag is True, tries to guess the correct encoding first.
    """
    encoding = detect_encoding(str_or_unicode) if precise else 'utf-8'
    if isinstance(str_or_unicode, str):
        return unicode(str_or_unicode, encoding, 'replace')
    return str_or_unicode


def to_utf8(str_or_unicode):
    """
    Safely returns a UTF-8 version of a given string
    >>> utils.to_utf8(u'hi')
        'hi'
    """
    if isinstance(str_or_unicode, unicode):
        return str_or_unicode.encode("utf-8", "ignore")
    return str(str_or_unicode)


def random_token(length=7):
    vals = ("a b c d e f g h i j k l m n o p q r s t u v w x y z "
            "0 1 2 3 4 5 6 7 8 9").split(' ')
    shuffle(vals)
    return ''.join(vals[:length])


def get_delimiter(msg_body):
    delimiter = RE_DELIMITER.search(msg_body)
    if delimiter:
        delimiter = delimiter.group()
    else:
        delimiter = '\n'

    return delimiter
