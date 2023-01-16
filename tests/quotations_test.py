# -*- coding: utf-8 -*-

from __future__ import absolute_import
import time
from . import *
from . fixtures import *

from talon import quotations


@patch.object(quotations, 'extract_from_html')
@patch.object(quotations, 'extract_from_plain')
def test_extract_from_respects_content_type(extract_from_plain,
                                            extract_from_html):
    msg_body = "Hi there"

    quotations.extract_from(msg_body, 'text/plain')
    extract_from_plain.assert_called_with(msg_body)

    quotations.extract_from(msg_body, 'text/html')
    extract_from_html.assert_called_with(msg_body)

    eq_(msg_body, quotations.extract_from(msg_body, 'text/blah'))


@patch.object(quotations, 'extract_from_plain', Mock(side_effect=Exception()))
def test_crash_inside_extract_from():
    msg_body = "Hi there"
    eq_(msg_body, quotations.extract_from(msg_body, 'text/plain'))


def test_empty_body():
    eq_('', quotations.extract_from_plain(''))

# How long do we expect the BIG_EMAIL.html file to be processed?
# This should be a little generous just to ensure that slightly slow hardware.
# This html email is tested using plain text processing to simulate exactly
# what happened during downtime related to KAYAKO-40768. SendGrid sent us a request
# with an html email they claimed was a text email (perhaps too big for them to parse).
TIME_LIMIT_SECONDS = 15

def test_succeed_on_kayako_40768_long_line_email():
    t0 = time.time()
    quotations.extract_from_plain(BIG_EMAIL)
    t1 = time.time()
    ok_(
        t1 - t0 < TIME_LIMIT_SECONDS,
        msg='BIG_EMAIL.html is taking too long. Perhaps there is a DoS issue with a regex, see KAYAKO-40768')


def test_missing_html_text():
    ohtml = quotations.extract_from_html_beta(MISSING_TEXT)

    eq_("May I know how much time it takes normally for the migration?" in ohtml, True)
    eq_("Can I say that Kayako Cloud is a combination of different software?" in ohtml, True)
    eq_("I went through some research, and I come across below URL" in ohtml, True)
    eq_("if we decided to go with Email + Whatsapp + Skype, Live Chat not sure" in ohtml, True)
