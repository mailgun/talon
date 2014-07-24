# -*- coding: utf-8 -*-

from . import *
from . fixtures import *

import regex as re
from flanker import mime

from talon import quotations

import html2text


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

    eq_("<html><body><p>Reply</p></body></html>",
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
    eq_("<html><body><p>Reply</p><div></div></body></html>",
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
    eq_("<html><body><p>Reply</p></body></html>",
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_unicode_in_reply():
    msg_body = u"""Reply \xa0 \xa0 Text<br>

<div>
  <br>
</div>

<blockquote class="gmail_quote">
  Quote
</blockquote>""".encode("utf-8")

    eq_("<html><body><p>Reply&#160;&#160;Text<br></p><div><br></div>"
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
    eq_('<html><body><div>message<br></div></body></html>',
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
    eq_('<html><body><div>message<br></div></body></html>',
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
    eq_('<html><body><div>Blah<br><br></div></body></html>',
        RE_WHITESPACE.sub('', quotations.extract_from_html(msg_body)))


def test_reply_quotations_share_block():
    msg = mime.from_string(REPLY_QUOTATIONS_SHARE_BLOCK)
    html_part = list(msg.walk())[1]
    assert html_part.content_type == 'text/html'
    stripped_html = quotations.extract_from_html(html_part.body)
    ok_(stripped_html)
    ok_('From' not in stripped_html)


def test_OLK_SRC_BODY_SECTION_stripped():
    eq_('<html><body><div>Reply</div></body></html>',
        RE_WHITESPACE.sub(
            '', quotations.extract_from_html(OLK_SRC_BODY_SECTION)))


def test_reply_separated_by_hr():
    eq_('<html><body><div>Hi<div>there</div></div></body></html>',
        RE_WHITESPACE.sub(
            '', quotations.extract_from_html(REPLY_SEPARATED_BY_HR)))


RE_REPLY = re.compile(r"^Hi\. I am fine\.\s*\n\s*Thanks,\s*\n\s*Alex\s*$")


def extract_reply_and_check(filename):
    f = open(filename)

    msg_body = f.read().decode("utf-8")
    reply = quotations.extract_from_html(msg_body)

    h = html2text.HTML2Text()
    h.body_width = 0
    plain_reply = h.handle(reply)

    #remove &nbsp; spaces
    plain_reply = plain_reply.replace(u'\xa0', u' ')

    if RE_REPLY.match(plain_reply):
        eq_(1, 1)
    else:
        eq_("Hi. I am fine.\n\nThanks,\nAlex", plain_reply)


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


def test_thunderbird_reply():
    extract_reply_and_check("tests/fixtures/html_replies/thunderbird.html")


def test_windows_mail_reply():
    extract_reply_and_check("tests/fixtures/html_replies/windows_mail.html")


def test_yandex_ru_reply():
    extract_reply_and_check("tests/fixtures/html_replies/yandex_ru.html")
