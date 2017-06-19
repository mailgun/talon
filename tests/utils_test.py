# coding:utf-8

from __future__ import absolute_import

import cchardet
import six

from talon import utils as u
from . import *


def test_get_delimiter():
    eq_('\r\n', u.get_delimiter('abc\r\n123'))
    eq_('\n', u.get_delimiter('abc\n123'))
    eq_('\n', u.get_delimiter('abc'))


def test_unicode():
    eq_(u'hi', u.to_unicode('hi'))
    eq_(type(u.to_unicode('hi')), six.text_type)
    eq_(type(u.to_unicode(u'hi')), six.text_type)
    eq_(type(u.to_unicode('привет')), six.text_type)
    eq_(type(u.to_unicode(u'привет')), six.text_type)
    eq_(u"привет", u.to_unicode('привет'))
    eq_(u"привет", u.to_unicode(u'привет'))
    # some latin1 stuff
    eq_(u"Versión", u.to_unicode(u'Versi\xf3n'.encode('iso-8859-2'), precise=True))


def test_detect_encoding():
    eq_('ascii', u.detect_encoding(b'qwe').lower())
    ok_(u.detect_encoding(
        u'Versi\xf3n'.encode('iso-8859-2')).lower() in [
            'iso-8859-1', 'iso-8859-2'])
    eq_('utf-8', u.detect_encoding(u'привет'.encode('utf8')).lower())
    # fallback to utf-8
    with patch.object(u.chardet, 'detect') as detect:
        detect.side_effect = Exception
        eq_('utf-8', u.detect_encoding('qwe'.encode('utf8')).lower())


def test_quick_detect_encoding():
    eq_('ascii', u.quick_detect_encoding(b'qwe').lower())
    ok_(u.quick_detect_encoding(
        u'Versi\xf3n'.encode('windows-1252')).lower() in [
            'windows-1252', 'windows-1250'])
    eq_('utf-8', u.quick_detect_encoding(u'привет'.encode('utf8')).lower())


@patch.object(cchardet, 'detect')
@patch.object(u, 'detect_encoding')
def test_quick_detect_encoding_edge_cases(detect_encoding, cchardet_detect):
    cchardet_detect.return_value = {'encoding': 'ascii'}
    eq_('ascii', u.quick_detect_encoding(b"qwe"))
    cchardet_detect.assert_called_once_with(b"qwe")

    # fallback to detect_encoding
    cchardet_detect.return_value = {}
    detect_encoding.return_value = 'utf-8'
    eq_('utf-8', u.quick_detect_encoding(b"qwe"))

    # exception
    detect_encoding.reset_mock()
    cchardet_detect.side_effect = Exception()
    detect_encoding.return_value = 'utf-8'
    eq_('utf-8', u.quick_detect_encoding(b"qwe"))
    ok_(detect_encoding.called)


def test_html_to_text():
    html = """<body>
<p>Hello world!</p>
<br>
<ul>
<li>One!</li>
<li>Two</li>
</ul>
<p>
Haha
</p>
</body>"""
    text = u.html_to_text(html)
    eq_(b"Hello world! \n\n  * One! \n  * Two \nHaha", text)
    eq_(u"привет!", u.html_to_text("<b>привет!</b>").decode('utf8'))

    html = '<body><br/><br/>Hi</body>'
    eq_(b'Hi', u.html_to_text(html))

    html = """Hi
<style type="text/css">

div, p, li {

font: 13px 'Lucida Grande', Arial, sans-serif;

}
</style>

<style type="text/css">

h1 {

font: 13px 'Lucida Grande', Arial, sans-serif;

}
</style>"""
    eq_(b'Hi', u.html_to_text(html))

    html = """<div>
<!-- COMMENT 1 -->
<span>TEXT 1</span>
<p>TEXT 2 <!-- COMMENT 2 --></p>
</div>"""
    eq_(b'TEXT 1 \nTEXT 2', u.html_to_text(html))


def test_comment_no_parent():
    s = b'<!-- COMMENT 1 --> no comment'
    d = u.html_document_fromstring(s)
    eq_(b"no comment", u.html_tree_to_text(d))


@patch.object(u.html5parser, 'fromstring', Mock(side_effect=Exception()))
def test_html_fromstring_exception():
    eq_(None, u.html_fromstring("<html></html>"))


@patch.object(u, 'html_too_big', Mock())
@patch.object(u.html5parser, 'fromstring')
def test_html_fromstring_too_big(fromstring):
    eq_(None, u.html_fromstring("<html></html>"))
    assert_false(fromstring.called)


@patch.object(u.html5parser, 'document_fromstring')
def test_html_document_fromstring_exception(document_fromstring):
    document_fromstring.side_effect = Exception()
    eq_(None, u.html_document_fromstring("<html></html>"))


@patch.object(u, 'html_too_big', Mock())
@patch.object(u.html5parser, 'document_fromstring')
def test_html_document_fromstring_too_big(document_fromstring):
    eq_(None, u.html_document_fromstring("<html></html>"))
    assert_false(document_fromstring.called)


@patch.object(u, 'html_fromstring', Mock(return_value=None))
def test_bad_html_to_text():
    bad_html = "one<br>two<br>three"
    eq_(None, u.html_to_text(bad_html))


@patch.object(u, '_MAX_TAGS_COUNT', 3)
def test_html_too_big():
    eq_(False, u.html_too_big("<div></div>"))
    eq_(True, u.html_too_big("<div><span>Hi</span></div>"))


@patch.object(u, '_MAX_TAGS_COUNT', 3)
def test_html_to_text():
    eq_(b"Hello", u.html_to_text("<div>Hello</div>"))
    eq_(None, u.html_to_text("<div><span>Hi</span></div>"))
