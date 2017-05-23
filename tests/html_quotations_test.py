# -*- coding: utf-8 -*-

from __future__ import absolute_import

# noinspection PyUnresolvedReferences
import re

from talon import quotations, utils as u
from . import *
from .fixtures import *

RE_WHITESPACE = re.compile("\s")
RE_DOUBLE_WHITESPACE = re.compile("\s")


def test_quotation_splitter_inside_blockquote():
    msg_body = """Reply
<blockquote>

  <div>
    On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:
  </div>

  <div>
    Test
  </div>

</blockquote>"""

    eq_("<html><head></head><body>Reply</body></html>",
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_quotation_splitter_outside_blockquote():
    msg_body = """Reply

<div>
  On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:
</div>

<blockquote>
  <div>
    Test
  </div>
</blockquote>
"""
    eq_("<html><head></head><body>Reply</body></html>",
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_regular_blockquote():
    msg_body = """Reply
<blockquote>Regular</blockquote>

<div>
  On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:
</div>

<blockquote>
  <div>
    <blockquote>Nested</blockquote>
  </div>
</blockquote>
"""
    eq_("<html><head></head><body>Reply<blockquote>Regular</blockquote></body></html>",
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_no_blockquote():
    msg_body = """
<html>
<body>
Reply

<div>
  On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:
</div>

<div>
  Test
</div>
</body>
</html>
"""

    reply = """
<html>
<head></head>
<body>
Reply

</body></html>"""
    eq_(RE_WHITESPACE.sub('', reply),
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_empty_body():
    eq_('', quotations.extract_from_html(''))


def test_validate_output_html():
    msg_body = """Reply
<div>
  On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:

    <blockquote>
      <div>
        Test
      </div>
    </blockquote>
</div>

<div/>
"""
    out = quotations.extract_from_html(msg_body)
    ok_('<html>' in out and '</html>' in out,
        'Invalid HTML - <html>/</html> tag not present')
    ok_('<div/>' not in out,
        'Invalid HTML output - <div/> element is not valid')


def test_gmail_quote():
    msg_body = """Reply
<div class="gmail_quote">
  <div class="gmail_quote">
    On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:
    <div>
      Test
    </div>
  </div>
</div>"""
    eq_("<html><head></head><body>Reply</body></html>",
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_gmail_quote_compact():
    msg_body = 'Reply' \
               '<div class="gmail_quote">' \
               '<div class="gmail_quote">On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:' \
               '<div>Test</div>' \
               '</div>' \
               '</div>'
    eq_("<html><head></head><body>Reply</body></html>",
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_gmail_quote_blockquote():
    msg_body = """Message
<blockquote class="gmail_quote">
  <div class="gmail_default">
    My name is William Shakespeare.
    <br/>
  </div>
</blockquote>"""
    eq_(RE_WHITESPACE.sub('', msg_body),
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_unicode_in_reply():
    msg_body = u"""Reply \xa0 \xa0 Text<br>

<div>
  <br>
</div>

<blockquote>
  Quote
</blockquote>""".encode("utf-8")

    eq_("<html><head></head><body>Reply&#160;&#160;Text<br><div><br></div>"
        "</body></html>",
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_blockquote_disclaimer():
    msg_body = """
<html>
  <body>
  <div>
    <div>
      message
    </div>
    <blockquote>
      Quote
    </blockquote>
  </div>
  <div>
    disclaimer
  </div>
  </body>
</html>
"""

    stripped_html = """
<html>
  <head></head>
  <body>
  <div>
    <div>
      message
    </div>
  </div>
  <div>
    disclaimer
  </div>
  </body>
</html>
"""
    eq_(RE_WHITESPACE.sub('', stripped_html),
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_date_block():
    msg_body = """
<div>
  message<br>
  <div>
    <hr>
    Date: Fri, 23 Mar 2012 12:35:31 -0600<br>
    To: <a href="mailto:bob@example.com">bob@example.com</a><br>
    From: <a href="mailto:rob@example.com">rob@example.com</a><br>
    Subject: You Have New Mail From Mary!<br><br>

    text
  </div>
</div>
"""
    eq_('<html><head></head><body><div>message<br></div></body></html>',
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_from_block():
    msg_body = """<div>
message<br>
<div>
<hr>
From: <a href="mailto:bob@example.com">bob@example.com</a><br>
Date: Fri, 23 Mar 2012 12:35:31 -0600<br>
To: <a href="mailto:rob@example.com">rob@example.com</a><br>
Subject: You Have New Mail From Mary!<br><br>

text
</div></div>
"""
    eq_('<html><head></head><body><div>message<br></div></body></html>',
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_reply_shares_div_with_from_block():
    msg_body = '''
<body>
  <div>

    Blah<br><br>

    <hr>Date: Tue, 22 May 2012 18:29:16 -0600<br>
    To: xx@hotmail.ca<br>
    From: quickemail@ashleymadison.com<br>
    Subject: You Have New Mail From x!<br><br>

  </div>
</body>'''
    eq_('<html><head></head><body><div>Blah<br><br></div></body></html>',
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_reply_quotations_share_block():
    stripped_html = quotations.extract_from_plain(REPLY_QUOTATIONS_SHARE_BLOCK)
    ok_(stripped_html)
    ok_('From' not in stripped_html)


def test_OLK_SRC_BODY_SECTION_stripped():
    eq_('<html><head></head><body><div>Reply</div></body></html>',
        RE_WHITESPACE.sub(
            '', quotations.extract_from_html(OLK_SRC_BODY_SECTION)))


def test_reply_separated_by_hr():
    eq_('<html><head></head><body><div>Hi<div>there</div></div></body></html>',
        RE_WHITESPACE.sub(
            '', quotations.extract_from_html(REPLY_SEPARATED_BY_HR)))


def test_from_block_and_quotations_in_separate_divs():
    msg_body = '''
Reply
<div>
  <hr/>
  <div>
    <font>
      <b>From: bob@example.com</b>
      <b>Date: Thu, 24 Mar 2016 08:07:12 -0700</b>
    </font>
  </div>
  <div>
    Quoted message
  </div>
</div>
'''
    eq_('<html><head></head><body>Reply<div><hr></div></body></html>',
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def extract_reply_and_check(filename):
    import sys
    kwargs = {}
    if sys.version_info > (3, 0):
        kwargs["encoding"] = "utf8"

    f = open(filename, **kwargs)

    msg_body = f.read()
    reply = quotations.extract_from_html(msg_body)
    plain_reply = u.html_to_text(reply)
    plain_reply = plain_reply.decode('utf8')

    eq_(RE_WHITESPACE.sub('', "Hi. I am fine.\n\nThanks,\nAlex"),
        RE_WHITESPACE.sub('', plain_reply))


def test_gmail_reply():
    extract_reply_and_check("tests/fixtures/html_replies/gmail.html")


def test_mail_ru_reply():
    extract_reply_and_check("tests/fixtures/html_replies/mail_ru.html")


def test_hotmail_reply():
    extract_reply_and_check("tests/fixtures/html_replies/hotmail.html")


def test_ms_outlook_2003_reply():
    extract_reply_and_check("tests/fixtures/html_replies/ms_outlook_2003.html")


def test_ms_outlook_2007_reply():
    extract_reply_and_check("tests/fixtures/html_replies/ms_outlook_2007.html")


def test_ms_outlook_2010_reply():
    extract_reply_and_check("tests/fixtures/html_replies/ms_outlook_2010.html")


def test_thunderbird_reply():
    extract_reply_and_check("tests/fixtures/html_replies/thunderbird.html")


def test_windows_mail_reply():
    extract_reply_and_check("tests/fixtures/html_replies/windows_mail.html")


def test_yandex_ru_reply():
    extract_reply_and_check("tests/fixtures/html_replies/yandex_ru.html")


def test_CRLF():
    """CR is not converted to '&#13;'
    """
    symbol = '&#13;'
    extracted = quotations.extract_from_html('<html>\r\n</html>')
    assert_false(symbol in extracted)
    eq_('<html></html>', RE_WHITESPACE.sub('', extracted))

    msg_body = """My
reply
<blockquote>

  <div>
    On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:
  </div>

  <div>
    Test
  </div>

</blockquote>"""
    msg_body = msg_body.replace('\n', '\r\n')
    extracted = quotations.extract_from_html(msg_body)
    assert_false(symbol in extracted)
    # Keep new lines otherwise "My reply" becomes one word - "Myreply" 
    eq_("<html><head></head><body>My\nreply\n</body></html>", extracted)


def test_gmail_forwarded_msg():
    msg_body = """<div dir="ltr"><br><div class="gmail_quote">---------- Forwarded message ----------<br>From: <b class="gmail_sendername">Bob</b> <span dir="ltr">&lt;<a href="mailto:bob@example.com">bob@example.com</a>&gt;</span><br>Date: Fri, Feb 11, 2010 at 5:59 PM<br>Subject: Bob WFH today<br>To: Mary &lt;<a href="mailto:mary@example.com">mary@example.com</a>&gt;<br><br><br><div dir="ltr">eom</div>
</div><br></div>"""
    extracted = quotations.extract_from_html(msg_body)
    eq_(RE_WHITESPACE.sub('', msg_body), RE_WHITESPACE.sub('', extracted))


@patch.object(u, '_MAX_TAGS_COUNT', 4)
def test_too_large_html():
    msg_body = 'Reply' \
               '<div class="gmail_quote">' \
               '<div class="gmail_quote">On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:' \
               '<div>Test</div>' \
               '</div>' \
               '</div>'
    eq_(RE_WHITESPACE.sub('', msg_body),
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_readable_html_empty():
    msg_body = """
<blockquote>
  Reply
  <div>
    On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:
  </div>

  <div>
    Test
  </div>

</blockquote>"""

    eq_(RE_WHITESPACE.sub('', msg_body),
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


@patch.object(quotations, 'html_document_fromstring', Mock(return_value=None))
def test_bad_html():
    bad_html = "<html></html>"
    eq_(bad_html, quotations.extract_from_html(bad_html))
