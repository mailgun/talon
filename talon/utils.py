# coding:utf-8
from __future__ import annotations

import html5lib
import regex as re
from html5lib import HTMLParser
from lxml.cssselect import CSSSelector
from lxml.etree import _Element
from lxml.html import html5parser

from talon.constants import RE_DELIMITER


def get_delimiter(msg_body: str) -> str:
    delimiter = RE_DELIMITER.search(msg_body)
    if delimiter:
        delimiter = delimiter.group()
    else:
        delimiter = '\n'

    return delimiter


def html_tree_to_text(tree: _Element) -> str:
    for style in CSSSelector('style')(tree):
        style.getparent().remove(style)

    for c in tree.xpath('//comment()'):
        parent = c.getparent()

        # comment with no parent does not impact produced text
        if parent is None:
            continue

        parent.remove(c)

    text = ""
    for el in tree.iter():
        el_text = (el.text or '') + (el.tail or '')
        if len(el_text) > 1:
            if el.tag in _BLOCKTAGS + _HARDBREAKS:
                text += "\n"
            if el.tag == 'li':
                text += "  * "
            text += el_text.strip() + " "

            # add href to the output
            href = el.attrib.get('href')
            if href:
                text += "(%s) " % href

        if (el.tag in _HARDBREAKS and text and
            not text.endswith("\n") and not el_text):
            text += "\n"

    text = _rm_excessive_newlines(text)
    return text


def html_to_text(s: str) -> str | None:
    """
    Dead-simple HTML-to-text converter:
        >>> html_to_text("one<br>two<br>three")
        <<< "one\ntwo\nthree"

    NOTES:
        1. the string is expected to contain UTF-8 encoded HTML!
        3. if html can't be parsed returns None
    """
    s = _prepend_utf8_declaration(s)
    s = s.replace("\n", "")
    tree = html_fromstring(s)

    if tree is None:
        return None

    return html_tree_to_text(tree)


def html_fromstring(s: str) -> _Element:
    """Parse html tree from string. Return None if the string can't be parsed.
    """
    return html5parser.fromstring(s, parser=_html5lib_parser())


def html_document_fromstring(s: str) -> _Element:
    """Parse html tree from string. Return None if the string can't be parsed.
    """
    return html5parser.document_fromstring(s, parser=_html5lib_parser())


def cssselect(expr: str, tree: str) -> list[_Element]:
    return CSSSelector(expr)(tree)


def _contains_charset_spec(s: str) -> str:
    """Return True if the first 4KB contain charset spec
    """
    return s.lower().find('html; charset=', 0, 4096) != -1


def _prepend_utf8_declaration(s: str) -> str:
    """Prepend 'utf-8' encoding declaration if the first 4KB don't have any
    """
    return s if _contains_charset_spec(s) else _UTF8_DECLARATION + s


def _rm_excessive_newlines(s: str) -> str:
    """Remove excessive newlines that often happen due to tons of divs
    """
    return _RE_EXCESSIVE_NEWLINES.sub("\n\n", s).strip()


def _html5lib_parser() -> HTMLParser:
    """
    html5lib is a pure-python library that conforms to the WHATWG HTML spec
    and is not vulnarable to certain attacks common for XML libraries
    """
    return HTMLParser(
        # build lxml tree
        html5lib.treebuilders.getTreeBuilder("lxml"),
        # remove namespace value from inside lxml.html.html5paser element tag
        # otherwise it yields something like "{http://www.w3.org/1999/xhtml}div"
        # instead of "div", throwing the algo off
        namespaceHTMLElements=False
    )


_UTF8_DECLARATION = ('<meta http-equiv="Content-Type" content="text/html;'
                     'charset=utf-8">')

_BLOCKTAGS = ['div', 'p', 'ul', 'li', 'h1', 'h2', 'h3']
_HARDBREAKS = ['br', 'hr', 'tr']

_RE_EXCESSIVE_NEWLINES = re.compile("\n{2,10}")
