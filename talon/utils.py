# coding:utf-8

import logging
from random import shuffle
import chardet
import cchardet
import regex as re

from lxml import html
from lxml.cssselect import CSSSelector

from talon.constants import RE_DELIMITER


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
    encoding = quick_detect_encoding(str_or_unicode) if precise else 'utf-8'
    if isinstance(str_or_unicode, str):
        return unicode(str_or_unicode, encoding, 'replace')
    return str_or_unicode


def detect_encoding(string):
    """
    Tries to detect the encoding of the passed string.

    Defaults to UTF-8.
    """
    try:
        detected = chardet.detect(string)
        if detected:
            return detected.get('encoding') or 'utf-8'
    except Exception, e:
        pass
    return 'utf-8'


def quick_detect_encoding(string):
    """
    Tries to detect the encoding of the passed string.

    Uses cchardet. Fallbacks to detect_encoding.
    """
    try:
        detected = cchardet.detect(string)
        if detected:
            return detected.get('encoding') or detect_encoding(string)
    except Exception, e:
        pass
    return detect_encoding(string)


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


def html_to_text(string):
    """
    Dead-simple HTML-to-text converter:
        >>> html_to_text("one<br>two<br>three")
        >>> "one\ntwo\nthree"

    NOTES:
        1. the string is expected to contain UTF-8 encoded HTML!
        2. returns utf-8 encoded str (not unicode)
    """
    s = _prepend_utf8_declaration(string)
    s = s.replace("\n", "")

    tree = html.fromstring(s)

    for style in CSSSelector('style')(tree):
        style.getparent().remove(style)

    for c in tree.xpath('//comment()'):
        c.getparent().remove(c)

    text   = ""
    for el in tree.iter():
        el_text = (el.text or '') + (el.tail or '')
        if len(el_text) > 1:
            if el.tag in _BLOCKTAGS:
                text += "\n"
            if el.tag == 'li':
                text += "  * "
            text += el_text.strip() + " "

            # add href to the output
            href = el.attrib.get('href')
            if href:
                text += "(%s) " % href

        if el.tag in _HARDBREAKS and text and not text.endswith("\n"):
            text += "\n"

    retval = _rm_excessive_newlines(text)
    return _encode_utf8(retval)


def _contains_charset_spec(s):
    """Return True if the first 4KB contain charset spec
    """
    return s.lower().find('html; charset=', 0, 4096) != -1


def _prepend_utf8_declaration(s):
    """Prepend 'utf-8' encoding declaration if the first 4KB don't have any
    """
    return s if _contains_charset_spec(s) else _UTF8_DECLARATION + s


def _rm_excessive_newlines(s):
    """Remove excessive newlines that often happen due to tons of divs
    """
    return _RE_EXCESSIVE_NEWLINES.sub("\n\n", s).strip()


def _encode_utf8(s):
    """Encode in 'utf-8' if unicode
    """
    return s.encode('utf-8') if isinstance(s, unicode) else s


_UTF8_DECLARATION = ('<meta http-equiv="Content-Type" content="text/html;'
                     'charset=utf-8">')


_BLOCKTAGS  = ['div', 'p', 'ul', 'li', 'h1', 'h2', 'h3']
_HARDBREAKS = ['br', 'hr', 'tr']


_RE_EXCESSIVE_NEWLINES = re.compile("\n{2,10}")
