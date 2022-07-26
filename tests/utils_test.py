# coding:utf-8

from __future__ import absolute_import

from talon import utils as u
from . import *


def test_get_delimiter():
    eq_('\r\n', u.get_delimiter('abc\r\n123'))
    eq_('\n', u.get_delimiter('abc\n123'))
    eq_('\n', u.get_delimiter('abc'))


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
    eq_("Hello world! \n\n  * One! \n  * Two \nHaha", text)
    eq_(u"привет!", u.html_to_text("<b>привет!</b>"))

    html = '<body><br/><br/>Hi</body>'
    eq_('Hi', u.html_to_text(html))

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
    eq_('Hi', u.html_to_text(html))

    html = """<div>
<!-- COMMENT 1 -->
<span>TEXT 1</span>
<p>TEXT 2 <!-- COMMENT 2 --></p>
</div>"""
    eq_('TEXT 1 \nTEXT 2', u.html_to_text(html))


def test_comment_no_parent():
    s = '<!-- COMMENT 1 --> no comment'
    d = u.html_document_fromstring(s)
    eq_("no comment", u.html_tree_to_text(d))


@patch.object(u, 'html_fromstring', Mock(return_value=None))
def test_bad_html_to_text():
    bad_html = "one<br>two<br>three"
    eq_(None, u.html_to_text(bad_html))
