# -*- coding: utf-8 -*-

from __future__ import absolute_import

# noinspection PyUnresolvedReferences
import re

from talon import quotations, utils as u
from . import *
from .fixtures import *
from talon.utils import logger

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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


def test_empty_body():
    eq_('', quotations.extract_from_html_beta(''))


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
    out = quotations.extract_from_html_beta(msg_body)
    ok_('<html>' in out and '</html>' in out,
        'Invalid HTML - <html>/</html> tag not present')
    ok_('<div/>' not in out,
        'Invalid HTML output - <div/> element is not valid')


def test_kayako_mail():
    msg_body = """Reply
<div class="m_-91438592347598kayako-mail-wrapper email-container">
  <div class="k_quote">
    On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:
    <div>
      Test
    </div>
  </div>
</div>"""
    eq_("<html><head></head><body>Reply</body></html>",
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


def test_gmail_quote_compact():
    msg_body = 'Reply' \
               '<div class="gmail_quote">' \
               '<div class="gmail_quote">On 11-Apr-2011, at 6:54 PM, Bob &lt;bob@example.com&gt; wrote:' \
               '<div>Test</div>' \
               '</div>' \
               '</div>'
    eq_("<html><head></head><body>Reply</body></html>",
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


def test_gmail_quote_blockquote():
    msg_body = """Message
<blockquote class="gmail_quote">
  <div class="gmail_default">
    My name is William Shakespeare.
    <br/>
  </div>
</blockquote>"""
    eq_(RE_WHITESPACE.sub('', msg_body),
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


def test_unicode_in_reply():
    msg_body = u"""Reply \xa0 \xa0 Text<br>

<div>
  <br>
</div>

<blockquote>
  Quote
</blockquote>""".encode("utf-8")

    eq_("<html><head></head><body>Reply&#xA0;&#xA0;Text<br><div><br></div>"
        "</body></html>",
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


def test_reply_quotations_share_block():
    stripped_html = quotations.extract_from_plain(REPLY_QUOTATIONS_SHARE_BLOCK)
    ok_(stripped_html)
    ok_('From' not in stripped_html)


def test_OLK_SRC_BODY_SECTION_stripped():
    eq_('<html><head></head><body><div>Reply</div></body></html>',
        RE_WHITESPACE.sub(
            '', quotations.extract_from_html_beta(OLK_SRC_BODY_SECTION)))


def test_reply_separated_by_hr():
    eq_('<html><head></head><body><div>Hi<div>there</div></div></body></html>',
        RE_WHITESPACE.sub(
            '', quotations.extract_from_html_beta(REPLY_SEPARATED_BY_HR)))


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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


def extract_reply_and_check(filename):
    import sys
    kwargs = {}
    if sys.version_info > (3, 0):
        kwargs["encoding"] = "utf8"

    f = open(filename, **kwargs)

    msg_body = f.read()
    reply = quotations.extract_from_html_beta(msg_body)
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
    extracted = quotations.extract_from_html_beta('<html>\r\n</html>')
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
    extracted = quotations.extract_from_html_beta(msg_body)
    assert_false(symbol in extracted)
    # Keep new lines otherwise "My reply" becomes one word - "Myreply" 
    eq_("<html><head></head><body>My\nreply\n</body></html>", extracted)


def test_gmail_forwarded_msg():
    msg_body = """<div dir="ltr"><br><div class="gmail_quote">---------- Forwarded message ----------<br>From: <b class="gmail_sendername">Bob</b> <span dir="ltr">&lt;<a href="mailto:bob@example.com">bob@example.com</a>&gt;</span><br>Date: Fri, Feb 11, 2010 at 5:59 PM<br>Subject: Bob WFH today<br>To: Mary &lt;<a href="mailto:mary@example.com">mary@example.com</a>&gt;<br><br><br><div dir="ltr">eom</div>
</div><br></div>"""
    extracted = quotations.extract_from_html_beta(msg_body)
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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


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
        RE_WHITESPACE.sub('', quotations.extract_from_html_beta(msg_body)))


@patch.object(quotations, 'html_document_fromstring', Mock(return_value=None))
def test_bad_html():
    bad_html = "<html></html>"
    eq_(bad_html, quotations.extract_from_html_beta(bad_html))


def test_emoji_with_russian():
    html_in = '<div dir="ltr">ha ha ha <span style="color:rgb(33,33,33);font-size:29px;white-space:pre-wrap">'\
            'эй чувак, как ты </span>😁<span style="font-size:12.8px"> lol</span></div>'\
            '<div class="gmail_extra"><br>'\
            '<div class="gmail_quote">2017-09-04 18:08 GMT+05:30 Sherub Thakur <span dir="ltr">&lt;'\
            '<a href="mailto:sherub.thakur@lulz.com" target="_blank">sherub.thakur@lulz.com</a>&gt;</span>:<br>'\
            '<blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex">'\
            '<div dir="ltr"><span style="color:rgb(33,33,33);font-size:29px;white-space:pre-wrap">эй чувак, как ты'\
            '</span>😁<span style="font-size:12.8px"> lol</span><br></div></blockquote></div><br></div>'
    html_out = quotations.extract_from_html_beta(html_in)
    html_expected = '<html><head></head><body><div dir="ltr">ha ha ha <span style="color:rgb(33,33,33);font-size:29px;white-space:pre-wrap">'\
                    '&#x44D;&#x439; &#x447;&#x443;&#x432;&#x430;&#x43A;, &#x43A;&#x430;&#x43A; &#x442;&#x44B; </span>&#x1F601;<span style="font-size:12.8px"> lol</span></div>'\
                    '<div class="gmail_extra"><br><br></div></body></html>'
    eq_(html_expected, html_out)


def test_outlook_additional_tags():
    html_in = '''
<html>
<body bgcolor=3D"white" lang=3D"EN-GB" link=3D"#0563C1" vlink=3D"#954F72">
    <div class=3D"WordSection1">
        <p class=3D"MsoNormal">
            <span lang=3D"EN-US" style=3D"font-size:11.0pt">
                Hey jude&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            </span>
            <span style=3D"font-size:11.0pt"><o:p></o:p></span>
        </p>
        <p class=3D"MsoNormal">
            <span lang=3D"EN-US" style=3D"font-size:11.0pt">&nbsp;</span>
            <span style=3D"font-size:11.0pt"><o:p></o:p></span>
        </p>
        <ol style=3D"margin-top:0cm" start=3D"1" type=3D"1">
            <li class=3D"MsoNormal" style=3D"margin-left:0cm;mso-list:l2 level1 lfo1">
                <span lang=3D"EN-US" style=3D"font-size:11.0pt">Asdasdsasadasdsad</span>
                <span style=3D"font-size:11.0pt">
                <o:p></o:p>
                </span>
            </li>
        </ol>
    </div>
    </body>
</html>'''
    html_out = quotations.extract_from_html_beta(html_in)
    html_expected = html_in
    eq_(html_in, html_out)


def test_cite_based_blockquotes():
    html_in = '''<html>\n  <head>\n    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n  </head>\n  <body text="#000000" bgcolor="#FFFFFF">\n    Dear M,<br>\n    <br>\n    As explained I had two meetings pending with James Bond.<br>\n    <br>\n    Also, Dr. Rupert has raised a concern that he would like to\n    communicate to K S and also to be brought to J's\n    attention. The\n    mail comes from <a class="moz-txt-link-abbreviated" href="mailto:sales@lulz.com">sales@lulz.com</a> and with copy to\n    <a class="moz-txt-link-abbreviated" href="mailto:meisha.jardine@lulz.com">meisha.jardine@lulz.com</a>.<br>\n    <br>\n    For you information, the contents of the mail included parts like\n    these:<br>\n    <br>\n    <blockquote>\n      <pre><span style="font-size:14px"><span style="font-family:arial,helvetica,sans-serif">This is a second reminder that your latest payment of USD13.53 for \n&lt;Subscription.Name&gt; was not successfully completed. As a courtesy,\n we’ll try once more in next day.</span></span></pre>\n      <pre><span style="font-size:14px"><span style="font-family:arial,helvetica,sans-serif"></span></span></pre>\n    </blockquote>\n    I will get in touch with you again once I have cleared the active\n    seats situation which I hope I do as soon as possible.<br>\n    <br>\n    Best regards, <br>\n    <span style="font-size:14px"><span\n        style="font-family:arial,helvetica,sans-serif"></span></span><br>\n    <span style="font-size:14px"><span\n        style="font-family:arial,helvetica,sans-serif"></span></span>\n    <pre class="moz-signature" cols="72">Carlos Fernández San Millán\nSystems Engineer, IT Operations\nEMBL Heidelberg\nT +49 6221 387-8559\n</pre>\n    <div class="moz-cite-prefix">On 11/14/2017 06:30 PM, Michael (Lulz Classic) wrote:<br>\n    </div>\n    <blockquote type="cite"\n      cite="mid:7aa822d65041f210241fa0f8ad90e839@lulz.com">\n      <table>\n        <tbody>\n          <tr>\n            <td><br>\n              <table style="font-family: Helvetica,\n                sans-serif;font-size:14px; line-height: 1.6;\n                -webkit-font-smoothing: antialiased;" border="0"\n                cellspacing="0" cellpadding="0">\n                <tbody>\n                  <tr>\n                    <td colspan="2">\n                      <div> Hey C,<br>\n                        <br>\n                        Please see the invoice attached here for the\n                        purchase of 6 *****s. Billing checked your\n                        account and the 3 ****s you previously\n                        purchased didn't have the discussed discount\n                        applied to them so they have created a credit in\n                        the system that will go towards this payment.\n                        Let me know if you require anything further from\n                        me and do keep me updated.<br>\n                        <br> </div>\n                    </td>\n                  </tr>\n                  <tr>\n                    <td colspan="3" style="font-size: 12px; padding-top:\n                      10px; color: #838D94;">\n                      <div style="padding-top:5px;padding-bottom:3px;">\n                        <a\nhref="https://support.lulz.com/api/v1/cases/2258142/messages/3429091/attachments/635426/download"\n                          style="color: #4EAFCB; text-decoration: none;\n                          padding-right:10px;" moz-do-not-send="true">INV00038154_A00005607_11142017.pdf</a>\n                        57KB </div>\n                    </td>\n                  </tr>\n                  <tr>\n                    <td colspan="3">\n                      <p style="padding-top: 5px; padding-bottom: 10px;">\n                        Michael Caminiti<br>\n                        <br>\n                        ---<br>\n                        <br>\n                        lulz.com\n                        [<a class="moz-txt-link-freetext" href="http://www.lulz.com/?utm_source=email_signatures">http://www.lulz.com/?utm_source=email_signatures</a>]\n                        -<br>\n                        @lulz [<a class="moz-txt-link-freetext" href="http://twitter.com/lulz">http://twitter.com/lulz</a>]<br>\n                        <br>\n                        Join us: Wiki\n                        [<a class="moz-txt-link-freetext" href="http://wiki.lulz.com/?utm_source=email_signatures">http://wiki.lulz.com/?utm_source=email_signatures</a>]\n                        -<br>\n                        Blog\n                        [<a class="moz-txt-link-freetext" href="http://blog.lulz.com/?utm_source=email_signatures">http://blog.lulz.com/?utm_source=email_signatures</a>]\n                        - Lulz<br>\n                        Forge\n                        [<a class="moz-txt-link-freetext" href="http://forge.lulz.com/?utm_source=email_signatures">http://forge.lulz.com/?utm_source=email_signatures</a>]\n                        - Forums<br>\n[<a class="moz-txt-link-freetext" href="http://forums.lulz.com/?utm_source=email_signatures">http://forums.lulz.com/?utm_source=email_signatures</a>] </p>\n                    </td>\n                  </tr>\n                </tbody>\n              </table>\n            </td>\n          </tr>\n        </tbody><tfoot><tr>\n            <td>\n              <table ;="" style="padding: 5px 0; font-size: 12px;\n                width:100%; margin: 0 auto;font-family: Helvetica,\n                sans-serif;font-size:14px; line-height: 1.6;\n                -webkit-font-smoothing: antialiased;" border="0"\n                cellspacing="0" cellpadding="0">\n                <tbody>\n                  <tr>\n                    <td>\n                      <div style="padding-top:12px;color:\n                        #838D94;border-top: 1px solid #E0E3E5;"> This is\n                        a Lulz Classic message delivered by <a\n                          href="https://lulz.com"\n                          moz-do-not-send="true">Lulz</a>. </div>\n                    </td>\n                  </tr>\n                </tbody>\n              </table>\n            </td>\n          </tr>\n        </tfoot>\n      </table>\n      <img\nsrc="https://u4709036.ct.sendgrid.net/wf/open?upn=u6a2PqF3vslNNtSRbhxJPUnHzdAKdyfPD8L7UPbW1sxVoZgqUNOrEr91-2FPi0XiDLAzjoQaLDVxdsxN-2F6hQcTuequkGV90f2xz5uA12fFzxE2570N0EQIKoe4NSaJwDG1BREJZtWFNLP5YSEl4Thp-2BSXFXwpvCt6OnHAxM4tBPINuy1N2RMwJ5FRVFqJYPN1qO1BMEjq7Ai2wonElKwreyBuJ9DPZBBHhlrJ5M-2BxECm4LwamrItohnKQimrTVFao3b7RMPow5-2FqGQ55QlO68dgZB3nuHf0Ohtt9S65ngxOtqvZQbgAk3KqBa5zZWVnSmOty5qQpo6DrInDxMoOtwLkMoLG-2BCCVdiyCHakPycLLlq4wHxC-2BuEII3ArKbPgtpdL"\n        alt="" style="height:1px !important;width:1px\n        !important;border-width:0 !important;margin-top:0\n        !important;margin-bottom:0 !important;margin-right:0\n        !important;margin-left:0 !important;padding-top:0\n        !important;padding-bottom:0 !important;padding-right:0\n        !important;padding-left:0 !important;" moz-do-not-send="true"\n        border="0" height="1" width="1">\n    </blockquote>\n    <br>\n  </body>\n</html>\n'''
    html_expected = '''<html><head>\n    \n  </head>\n  <body text="#000000" bgcolor="#FFFFFF">\n    Dear M,<br>\n    <br>\n    As explained I had two meetings pending with James Bond.<br>\n    <br>\n    Also, Dr. Rupert has raised a concern that he would like to\n    communicate to K S and also to be brought to J\'s\n    attention. The\n    mail comes from <a class="moz-txt-link-abbreviated" href="mailto:sales@lulz.com">sales@lulz.com</a> and with copy to\n    <a class="moz-txt-link-abbreviated" href="mailto:meisha.jardine@lulz.com">meisha.jardine@lulz.com</a>.<br>\n    <br>\n    For you information, the contents of the mail included parts like\n    these:<br>\n    <br>\n    <blockquote>\n      <pre><span style="font-size:14px"><span style="font-family:arial,helvetica,sans-serif">This is a second reminder that your latest payment of USD13.53 for \n&lt;Subscription.Name&gt; was not successfully completed. As a courtesy,\n we&#x2019;ll try once more in next day.</span></span></pre>\n      <pre><span style="font-size:14px"><span style="font-family:arial,helvetica,sans-serif"></span></span></pre>\n    </blockquote>\n    I will get in touch with you again once I have cleared the active\n    seats situation which I hope I do as soon as possible.<br>\n    <br>\n    Best regards, <br>\n    <span style="font-size:14px"><span style="font-family:arial,helvetica,sans-serif"></span></span><br>\n    <span style="font-size:14px"><span style="font-family:arial,helvetica,sans-serif"></span></span>\n    <pre class="moz-signature" cols="72">Carlos Fern&#xE1;ndez San Mill&#xE1;n\nSystems Engineer, IT Operations\nEMBL Heidelberg\nT +49 6221 387-8559\n</pre>\n    </body></html>'''
    html_out = quotations.extract_from_html_beta(html_in)
    eq_(html_expected, html_out)


def test_van_is_treated_as_from():
    logger.info('Van:')
    html_in = '''<body lang="NL" link="blue" vlink="purple"><div class="WordSection1"><p class="MsoNormal"><span style="mso-fareast-language:EN-US">Hello Gurpreet and Sandy,</span></p><p class="MsoNormal"><span style="mso-fareast-language:EN-US"> </span></p><p class="MsoNormal"><span style="mso-fareast-language:EN-U
S">Thanks for your answer. We are certainly interested in migrating to the new Lulz and started immediately with the investigation of all steps. We will let you know when we have any questions regarding the migration.</span></p><p class="MsoNormal"><span style="mso-fareast-language:EN-US">C</span><span style="mso-f
areast-language:EN-US">an you please make sure that the answers on this ticket are addressed to me? From Stb I will be the contact person during the migration project. My colleague Manon initiated the start.</span></p><p class="MsoNormal"><span style="mso-fareast-language:EN-US"> </span></p><p class="MsoNormal"><span
 style="mso-fareast-language:EN-US">Best regards, </span></p><p class="MsoNormal"> </p><p class="MsoNormal"><img width="139" height="86" style="width:1.4479in;height:.8958in" id="_x0000_i1028" src="cid:image004.jpg@01D38E0C.90C556C0" alt="cid:image001.jpg@01D1A213.E8631160"></p><p class="MsoNormal"><b><span style="co
lor:#003867">Sinatra Beuling<br></span></b><span style="color:#003867">Project Manager</span></p><p class="MsoNormal"><b><span style="color:#81a1c8"><br>@</span></b><span style="color:#003867"> </span><a href="mailto:sinatra.beuling@stb.nl"><span style="color:#0563c1">sinatra.beuling@stb.nl</span></a><br><b><span
style="color:#81a1c8">m </span></b>06 83 23 60 25<br><b><span style="color:#81a1c8">t</span></b><span style="color:#003867"> </span>030 638 50 63<span style="color:#003867"><br></span><br><span style="mso-fareast-language:EN-US"> </span></p><p class="MsoNormal"><b>Van:</b> Gurpreet Singh (Lulz Support) [mailto:<a h
ref="mailto:support@lulz.com">support@lulz.com</a>] <br><b>Verzonden:</b> zaterdag 13 januari 2018 11:02<br><b>Aan:</b> Manon Vollmann - Stb Goede Doelen &lt;<a href="mailto:manon.vollmann@stb.nl">manon.vollmann@stb.nl</a>&gt;<br><b>Onderwerp:</b> Re: RFC</p><p class="MsoNormal"> </p><div><p class="MsoNormal">Hel
lo Sinatra,<br><br>Allow me to jump in as Sandy out shift today due to the weekend.<br><br>&gt;&gt;In this new year we would like to get started with migrating our data to the cloud. For us it is important to test in a sandbox environment with our own data. Can you please let us know what would be the steps and what
 is needed to start the migration project?<br><br>Thank you for registering your interest in migrating to the new Lulz. This is an update email about your new Lulz migration options and next steps.<br><br><strong><span style="font-family:&quot;Calibri&quot;,sans-serif">Lulz Classic</span></strong><br><br>You’re
 currently using Lulz Classic. Lulz Classic will continue to be supported with new releases alongside the new Lulz. So this means you can keep using your current Lulz for the time being and migrate to the new Lulz later (or, if you prefer to stay with Lulz Classic, you can do so).<br><br>The latest versio
n of Lulz Classic is 4.90 (check out all Lulz Classic release updates <a href="https://classic.lulz.com/section/257-latest-updates">here</a>).<br><br><strong><span style="font-family:&quot;Calibri&quot;,sans-serif">The new Lulz</span></strong><br><br>The new Lulz in the cloud has been completely rebuilt to
introduce big improvements across the board; everything from the user experience to live chat and to business rule automation.<br><br>However, with big improvements come significant changes. A lot is different about the new Lulz: your team will need to learn a brand new interface and your administrators will need t
o rethink automation rules, SLAs and permissions.<br><br>So, it is important that you’re aware of the changes and are comfortable that migrating your team to the new Lulz is something you want to do and you have the space on your agenda to do.<br><br><strong><span style="font-family:&quot;Calibri&quot;,sans-serif">
Interested in migrating to the new Lulz?</span></strong><br><br>We can certainly help you with that:<br><br>Step 1: You’ll first need to sign up for a free trial <a href="https://www.lulz.com/free-trial">here</a>. Sign up using a test domain (ex. <a href="http://yourdomain-test.lulz.com">yourdomain-test.lulz.
com</a>). This keeps the actual domain name available for your final migration.<br><br>Step 2: Have a read through the migration guide <a href="https://support.lulz.com/section/253-upgrading-from-lulz-classic">here</a> on our Help Center to get an understanding for what has changed and where.<br><br>Step 3: Go th
rough the trial onboarding, and use it to test all your existing must-have Lulz Classic workflows. If you have any questions about how your existing workflows will work in the new Lulz, feel free to reach out to us and we’ll be happy to give you a hand..<br><br>Step 4: Familiarize yourself with the migration proc
edure <a href="https://support.lulz.com/article/1206-overview-of-the-upgrade-process">as explained here</a>.<br><br>The above steps should give you a very fair idea of how the new Lulz meets your requirements and what’s involved in migrating. You’ll then be in the best position to determine when your team will be
 ready for migration. Our product experts will be on-hand to help you each step of the way.<br><br>With that, I will wait to hear back from you on how you would like to proceed! :)<br><br>&gt;&gt;We would also like to know if we need to do something with this message that we received from your sales department: For s
elf-hosted Lulz Classic Download customers, remember to download your updated key.php file from <a href="http://my.lulz.com">my.lulz.com</a> [<a href="http://my.lulz.com/">http://my.lulz.com</a>] and replace the existing one on your Lulz instance to extend the expiry date.<br><br>Yeah, since you are using
 Download subscription license, you need to login to your <a href="https://my.lulz.com">https://my.lulz.com</a> account, download the updated <a href="file://key.php">key.php</a> license key file and replace it with the existing key file available in the doc root of your Lulz installation.  This will ensure tha
t you are using the new and valid key.  <br><br>Feel free to drop us a line if you have any question and I shall be happy to help you.<br><br>Kind regards,<br>Gurpreet Singh</p></div><p class="MsoNormal"> </p><div><p class="MsoNormal">—</p></div><p class="MsoNormal"> </p><div><table class="MsoNormalTable" border="0"
cellpadding="0"><tr><td style="padding:.75pt .75pt .75pt .75pt"><table class="MsoNormalTable" border="0" cellspacing="0" cellpadding="0" width="100%" style="width:100.0%"><tr><td style="padding:3.75pt 0cm 3.75pt 0cm"><div style="border:none;border-top:solid #e0e3e5 1.0pt;padding:9.0pt 0cm 0cm 0cm"><p class="MsoNormal
"><span style="font-size:10.5pt;font-family:&quot;Helvetica&quot;,sans-serif;color:#838d94">This is a Lulz Support message delivered by <a href="https://lulz.com" target="_blank">Lulz</a>. </span></p></div></td></tr></table></td></tr></table></div><p class="MsoNormal"> </p><table class="MsoNormalTable" border="
0" cellspacing="0" cellpadding="0" style="max-width:600.0pt"><tr><td style="padding:0cm 0cm 0cm 0cm"><div><div><p class="MsoNormal"><span style="font-size:10.5pt;font-family:&quot;Helvetica&quot;,sans-serif;color:#5f6c73">On Fri, Jan 12, 2018 at 4:13 PM, Sinatra - &lt;<a href="mailto:sinatra@stb.nl">sinatra@stb.nl
</a>&gt; via Mail: </span></p></div><blockquote style="border:none;border-left:solid #dddddd 2.25pt;padding:0cm 0cm 0cm 12.0pt;margin-left:0cm;margin-top:5.0pt;margin-right:0cm;margin-bottom:5.0pt"><table class="MsoNormalTable" border="0" cellpadding="0" width="100%" style="width:100.0%"><tr><td style="padding:.75pt
.75pt .75pt .75pt"><div><p><span style="font-size:10.5pt;color:#5f6c73">Hi Sandy,</span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;color:#5f6c73">In this new year we would like to get started with migrating our data to the cloud. For us it is important to test in
a sandbox environment with our own data.</span></p><p><span style="font-size:10.5pt;color:#5f6c73">Can you please let us know what would be the steps and what is needed to start the migration project?</span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;color:#5f6c73"
>We would also like to know if we need to do something with this message that we received from your sales department: For self-hosted Lulz Classic Download customers, remember to download your updated key.php file from <a href="http://my.lulz.com">my.lulz.com</a> and replace the existing one on your Lulz inst
ance to extend the expiry date.</span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;color:#5f6c73">Thanks for your answer!</span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;color:#5f6c73">Best regards,</span></p><p
><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;color:#5f6c73;border:solid windowtext 1.0pt;padding:0cm"><img border="0" width="139" height="86" style="width:1.4479in;height:.8958in" id="Afbeelding_x0020_1" src="cid:image001.jpg@01D38D88.7B9928A0" alt="Afbeelding verwijderd
door afzender."></span></p><p><b><span style="font-size:10.5pt;color:#5f6c73">Sinatra Beuling<br></span></b><span style="font-size:10.5pt;color:#5f6c73">Project Manager</span></p><p><b><span style="font-size:10.5pt;color:#5f6c73"><br>@</span></b><span style="font-size:10.5pt;color:#5f6c73"> <a href="mailto:sinatra.
beuling@stb.nl">sinatra.beuling@stb.nl</a><br><b>m</b> 06 83 23 60 25<br><b>t</b> 030 638 50 63<br><br>Postbus 257, 3990 GB Houten <br>De Molen 100, 3995 AX Houten <br><b>t</b> 030 634 30 00 <br><b>w</b> <a href="http://www.stb.nl">www.stb.nl</a></span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p>
</div></td></tr></table><div><div><p class="MsoNormal"><span style="font-size:10.5pt;font-family:&quot;Helvetica&quot;,sans-serif;color:#5f6c73">On Thu, Jan 4, 2018 at 11:31 AM, Sandeep Kaur &lt;<a href="mailto:support@lulz.com">support@lulz.com</a>&gt; via Mail: </span></p></div><blockquote style="border:none;bo
rder-left:solid #dddddd 2.25pt;padding:0cm 0cm 0cm 12.0pt;margin-left:0cm;margin-top:5.0pt;margin-right:0cm;margin-bottom:5.0pt"><table class="MsoNormalTable" border="0" cellpadding="0" width="100%" style="width:100.0%"><tr><td style="padding:.75pt .75pt .75pt .75pt"><p class="MsoNormal"><span style="font-size:10.5pt
;color:#5f6c73">Hey Manon and Anne! :)<br><br>No worries. Let me know if you have any questions to get started with the process </span><span style="font-size:10.5pt;font-family:&quot;Segoe UI Emoji&quot;,sans-serif;color:#5f6c73">👨</span><span style="font-size:10.5pt;color:#5f6c73">‍‍‍/span><span style="font -size:10.]
5pt;font-family:&quot;Segoe UI Emoji&quot;,sans-serif;color:#5f6c73">🏭</span><span style="font-size:10.5pt;color:#5f6c73"><br><br>Cheers,<br>Sandy </span></p></td></tr></table><div><div><p class="MsoNormal"><span style="font-size:10.5pt;font-family:&quot;Helvetica&quot;,sans-serif;color:#5f6c73">On Thu, Jan 4, 2018 ]
at 11:07 AM, Manon Vollmann - Stb Goede Doelen &lt;<a href="mailto:manon.vollmann@stb.nl">manon.vollmann@stb.nl</a>&gt; via Mail: </span></p></div><blockquote style="border:none;border-left:solid #dddddd 2.25pt;padding:0cm 0cm 0cm 12.0pt;margin-left:0cm;margin-top:5.0pt;margin-right:0cm;margin-bottom:5.0pt"<table cl]
ass="MsoNormalTable" border="0" cellpadding="0" width="100%" style="width:100.0%"><tr><td style="padding:.75pt .75pt .75pt .75pt"><div><p><span style="font-size:10.5pt;color:#5f6c73">Hi Sandy,</span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;color:#5f6c73">Thanks
for your mail, I’m sorry it took me so long to react.</span></p><p><span style="font-size:10.5pt;color:#5f6c73">We are ready to get started. I’m sending this reply also to my collegue Sinatra Beuling, who is much better in technical issues then I am.</span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span>
</p><p><span style="font-size:10.5pt;color:#5f6c73">She will be contacting you to get things started.</span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;color:#5f6c73">Best regards and best wishes for 2018</span></p><p><span style="font-size:10.5pt;color:#5f6c73"> <
/span></p><p><span style="font-size:10.5pt;color:#5f6c73">Manon</span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;color:#5f6c73;border:solid windowtext 1.0pt;padding:0cm"><img border="0" width="96" height=
"59" style="width:1.0in;height:.6145in" id="_x0000_i1026" src="cid:image002.jpg@01D38D88.7B9928A0" alt="Afbeelding verwijderd door afzender."></span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><b><span style="font-size:10.5pt;color:#5f6c73">Manon Vollmann</span></b></p><p><span style="font-size
:10.5pt;color:#5f6c73">Manager Support</span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><b><span style="font-size:10.5pt;color:#5f6c73">@</span></b><span style="font-size:10.5pt;color:#5f6c73"> <a href="mailto:manon@stb.nl">manon@stb.nl</a></span></p><p><b><span style="font-size:10.5pt;color:#
5f6c73">t</span></b><span style="font-size:10.5pt;color:#5f6c73"> 030 760 29 80</span></p><p><b><span style="font-size:10.5pt;color:#5f6c73">m</span></b><span style="font-size:10.5pt;color:#5f6c73"> 06 86 84 44 45</span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;c
olor:#5f6c73">Postbus 257, 3990 GB Houten</span></p><p><span style="font-size:10.5pt;color:#5f6c73">De Molen 100, Houten</span></p><p><b><span style="font-size:10.5pt;color:#5f6c73">t</span></b><span style="font-size:10.5pt;color:#5f6c73"> 030 638 50 65</span></p><p><b><span style="font-size:10.5pt;color:#5f6c73">w</
span></b><span style="font-size:10.5pt;color:#5f6c73"> <a href="http://www.stb.nl">www.stb.nl</a></span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5pt;color:#5f6c73"> </span></p><p><span style="font-size:10.5
pt;color:#5f6c73"> </span></p></div></td></tr></table><div><div><p class="MsoNormal"><span style="font-size:10.5pt;font-family:&quot;Helvetica&quot;,sans-serif;color:#5f6c73">On Fri, Dec 15, 2017 at 12:28 PM, Sandeep Kaur &lt;<a href="mailto:support@lulz.com">support@lulz.com</a>&gt; via Mail: </span></p></div><b
lockquote style="border:none;border-left:solid #dddddd 2.25pt;padding:0cm 0cm 0cm 12.0pt;margin-left:0cm;margin-top:5.0pt;margin-right:0cm;margin-bottom:5.0pt"><table class="MsoNormalTable" border="0" cellpadding="0" width="100%" style="width:100.0%"><tr><td style="padding:.75pt .75pt .75pt .75pt"><p class="MsoNormal
"><span style="font-size:10.5pt;color:#5f6c73">Hey Manon,<br><br>Piyush passed on your conversation to me for taking on the migration bit :) Let&#39;s get started with it </span><span style="font-size:10.5pt;font-family:&quot;Segoe UI Emoji&quot;,sans-serif;color:#5f6c73">👨</span><span style="font-size:10.5pt;color:]
#5f6c73">‍‍‍/span><span style="font-size:10.5pt;font-family:&quot;Segoe UI Emoji&quot;,sans-serif;color:#5f6c73">🏭🏭/span><span style="font-size:10.5pt;color:#5f6c73"><br><br>Could you please sign up for free trial <a href="https://www.lulz.com/free-trial">here</a> to see how the new Lulz meets your requi rements. ]
Once done, could you please book a 1-1 demo session wherein Ashok will walk you through the product and answer any questions that you might have.<br><br>You can easily book from one of the available sessions <a href="https://calendly.com/lulz-demo">here</a>. If you could please use the same email addressto book s5]
ession) which is linked with this case.<br><br>Also please note, you’ll need this unique session ID to book a session with us: 2210907<br><br>You&#39;ll be given a GoToMeeting link to join the session.......however, if you are more comfortable using TeamViewer, we can use that too. You can drop the Teamviewer Details
 here to connect.<br><br>Have a great weekend </span><span style="font-size:10.5pt;font-family:&quot;Segoe UI Emoji&quot;,sans-serif;color:#5f6c73">🤓</span><span style="font-size:10.5pt;color:#5f6c73"><br><br>Cheers,<br>Sandy </span></p></td></tr></table><div><div><p class="MsoNormal"><span style="font-size:10.5pt;f]
ont-family:&quot;Helvetica&quot;,sans-serif;color:#5f6c73">On Fri, Dec 15, 2017 at 12:12 PM, Piyush Mahajan &lt;<a href="mailto:support@lulz.com">support@lulz.com</a>&gt; via Mail: </span></p></div><blockquote style="border:none;border-left:solid #dddddd 2.25pt;padding:0cm 0cm 0cm 12.0pt;margin-left:0cmmargin-to]
p:5.0pt;margin-right:0cm;margin-bottom:5.0pt"><table class="MsoNormalTable" border="0" cellpadding="0" width="100%" style="width:100.0%"><tr><td style="padding:.75pt .75pt .75pt .75pt"><p class="MsoNormal"><span style="font-size:10.5pt;color:#5f6c73">O I just recalled our last discussion - you said that you wanted to
 do a bank transfer payment.<br><br>Please find our bank details in the link here: <a href="https://support.lulz.com/article/1322-can-i-pay-by-bank-transfer-and-money-wire">https://support.lulz.com/article/1322-can-i-pay-by-bank-transfer-and-money-wire</a> </span></p></td></tr></table><div><div><p class="MsoNorma
l"><span style="font-size:10.5pt;font-family:&quot;Helvetica&quot;,sans-serif;color:#5f6c73">On Fri, Dec 15, 2017 at 12:07 PM, Piyush Mahajan &lt;<a href="mailto:support@lulz.com">support@lulz.com</a>&gt; via Mail: </span></p></div><blockquote style="border:none;border-left:solid #dddddd 2.25pt;padding:0cm 0cm 0c
m 12.0pt;margin-left:0cm;margin-top:5.0pt;margin-right:0cm;margin-bottom:5.0pt"><table class="MsoNormalTable" border="0" cellpadding="0" width="100%" style="width:100.0%"><tr><td style="padding:.75pt .75pt .75pt .75pt"><p class="MsoNormal"><span style="font-size:10.5pt;color:#5f6c73">Thank you Manon.<br><br>I have in
itiated the first round of process towards the upgrade. Please find attached the invoice for the payment.<br><br>Note: This invoice does not include the collaborator add on, as that will be a separate transaction when we will migrate your helpdesk to the new Lulz in the cloud.<br><br>Let me know how would you like
to make the payment.<br><br>At the same time, I am forwarding your case to our Migration team, so that they can start the process from their end. </span></p></td></tr><tr><td style="padding:3.75pt .75pt .75pt .75pt"><p class="MsoNormal"><span style="font-size:9.0pt;color:#838d94">1 attachments </span></p><div><p clas
s="MsoNormal"><span style="font-size:9.0pt;color:#838d94"><a href="https://support.lulz.com/api/v1/cases/2210907/messages/3461419/attachments/642305/download"><span style="color:#4eafcb;text-decoration:none">INV00039846_A00005738_12152017.pdf</span></a> 55KB </span></p></div></td></tr></table></blockquote></div></b
lockquote></div></blockquote></div></blockquote></div></blockquote></div></blockquote></div></td></tr></table><p class="MsoNormal"><span style="border:solid windowtext 1.0pt;padding:0cm"><img border="0" width="1" height="1" style="width:.0104in;height:.0104in" id="_x0000_i1027" src="cid:image003.jpg@01D38D88.7B9928A0
" alt="Afbeelding verwijderd door afzender."></span></p></div></body>
    '''
    html_expected = '''<html><head></head><body lang="NL" link="blue" vlink="purple"><div class="WordSection1"><p class="MsoNormal"><span style="mso-fareast-language:EN-US">Hello Gurpreet and Sandy,</span></p><p class="MsoNormal"><span style="mso-fareast-language:EN-US">&#xA0;</span></p><p class="MsoNormal"><span style="mso-fareast-language:EN-U\nS">Thanks for your answer. We are certainly interested in migrating to the new Lulz and started immediately with the investigation of all steps. We will let you know when we have any questions regarding the migration.</span></p><p class="MsoNormal"><span style="mso-fareast-language:EN-US">C</span><span style="mso-f\nareast-language:EN-US">an you please make sure that the answers on this ticket are addressed to me? From Stb I will be the contact person during the migration project. My colleague Manon initiated the start.</span></p><p class="MsoNormal"><span style="mso-fareast-language:EN-US">&#xA0;</span></p><p class="MsoNormal"><span style="mso-fareast-language:EN-US">Best regards, </span></p><p class="MsoNormal">&#xA0;</p><p class="MsoNormal"><img width="139" height="86" style="width:1.4479in;height:.8958in" id="_x0000_i1028" src="cid:image004.jpg@01D38E0C.90C556C0" alt="cid:image001.jpg@01D1A213.E8631160"></p><p class="MsoNormal"><b><span style="co\nlor:#003867">Sinatra Beuling<br></span></b><span style="color:#003867">Project Manager</span></p><p class="MsoNormal"><b><span style="color:#81a1c8"><br>@</span></b><span style="color:#003867"> </span><a href="mailto:sinatra.beuling@stb.nl"><span style="color:#0563c1">sinatra.beuling@stb.nl</span></a><br><b><span style="color:#81a1c8">m </span></b>06 83 23 60 25<br><b><span style="color:#81a1c8">t</span></b><span style="color:#003867"> </span>030 638 50 63<span style="color:#003867"><br></span><br><span style="mso-fareast-language:EN-US">&#xA0;</span></p></div><p class="MsoNormal"><span style="border:solid windowtext 1.0pt;padding:0cm"><img border="0" width="1" height="1" style="width:.0104in;height:.0104in" id="_x0000_i1027" src="cid:image003.jpg@01D38D88.7B9928A0%0A" alt="Afbeelding verwijderd door afzender."></span></p>\n    </body></html>'''
    html_out = quotations.extract_from_html_beta(html_in)
    eq_(html_expected, html_out)


def test_on_real_data():
    for html in REAL_HTML:
        html_out = quotations.extract_from_html(html)
        logger.info(html_out)
        assert len(html_out) < 3000
