# -*- coding: utf-8 -*-

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
