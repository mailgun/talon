# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os

from six.moves import range

from talon.signature import bruteforce, extraction, extract
from talon.signature import extraction as e
from talon.signature.learning import dataset
from .. import *


def test_message_shorter_SIGNATURE_MAX_LINES():
    sender = "bob@foo.bar"
    body = """Call me ASAP, please.This is about the last changes you deployed.

Thanks in advance,
Bob"""
    text, extracted_signature = extract(body, sender)
    eq_('\n'.join(body.splitlines()[:2]), text)
    eq_('\n'.join(body.splitlines()[-2:]), extracted_signature)


def test_messages_longer_SIGNATURE_MAX_LINES():
    import sys
    kwargs = {}
    if sys.version_info > (3, 0):
        kwargs["encoding"] = "utf8"

    for filename in os.listdir(STRIPPED):
        filename = os.path.join(STRIPPED, filename)
        if not filename.endswith('_body'):
            continue
        sender, body = dataset.parse_msg_sender(filename)
        text, extracted_signature = extract(body, sender)
        extracted_signature = extracted_signature or ''
        with open(filename[:-len('body')] + 'signature', **kwargs) as ms:
            msg_signature = ms.read()
            eq_(msg_signature.strip(), extracted_signature.strip())
            stripped_msg = body.strip()[:len(body.strip()) - len(msg_signature)]
            eq_(stripped_msg.strip(), text.strip())


def test_text_line_in_signature():
    # test signature should consist of one solid part
    sender = "bob@foo.bar"
    body = """Call me ASAP, please.This is about the last changes you deployed.

Thanks in advance,
some text which doesn't seem to be a signature at all
Bob"""

    text, extracted_signature = extract(body, sender)
    eq_('\n'.join(body.splitlines()[:2]), text)
    eq_('\n'.join(body.splitlines()[-3:]), extracted_signature)


def test_long_line_in_signature():
    sender = "bob@foo.bar"
    body = """Call me ASAP, please.This is about the last changes you deployed.

Thanks in advance,
some long text here which doesn't seem to be a signature at all
Bob"""

    text, extracted_signature = extract(body, sender)
    eq_('\n'.join(body.splitlines()[:-1]), text)
    eq_('Bob', extracted_signature)

    body = """Thanks David,

    some *long* text here which doesn't seem to be a signature at all
    """
    ((body, None), extract(body, "david@example.com"))


def test_basic():
    msg_body = 'Blah\r\n--\r\n\r\nSergey Obukhov'
    eq_(('Blah', '--\r\n\r\nSergey Obukhov'),
        extract(msg_body, 'Sergey'))


def test_capitalized():
    msg_body = """Hi Mary,

Do you still need a DJ for your wedding? I've included a video demo of one of our DJs available for your wedding date.

DJ Doe 
http://example.com
Password: SUPERPASSWORD

Would you like to check out more?


At your service,

John Smith
Doe Inc
555-531-7967"""

    sig = """John Smith
Doe Inc
555-531-7967"""

    eq_(sig, extract(msg_body, 'Doe')[1])


def test_over_2_text_lines_after_signature():
    body = """Blah

    Bob,
    If there are more than
    2 non signature lines in the end
    It's not signature
    """
    text, extracted_signature = extract(body, "Bob")
    eq_(extracted_signature, None)


def test_no_signature():
    sender, body = "bob@foo.bar", "Hello"
    eq_((body, None), extract(body, sender))


def test_handles_unicode():
    sender, body = dataset.parse_msg_sender(UNICODE_MSG)
    text, extracted_signature = extract(body, sender)


@patch.object(extraction, 'has_signature')
def test_signature_extract_crash(has_signature):
    has_signature.side_effect = Exception('Bam!')
    msg_body = u'Blah\r\n--\r\n\r\nСергей'
    eq_((msg_body, None), extract(msg_body, 'Сергей'))


def test_mark_lines():
    with patch.object(bruteforce, 'SIGNATURE_MAX_LINES', 2):
        # we analyse the 2nd line as well though it's the 6th line
        # (starting from the bottom) because we don't count empty line
        eq_('ttset',
            e._mark_lines(['Bob Smith',
                           'Bob Smith',
                           'Bob Smith',
                           '',
                           'some text'], 'Bob Smith'))

    with patch.object(bruteforce, 'SIGNATURE_MAX_LINES', 3):
        # we don't analyse the 1st line because
        # signature cant start from the 1st line
        eq_('tset',
            e._mark_lines(['Bob Smith',
                           'Bob Smith',
                           '',
                           'some text'], 'Bob Smith'))


def test_process_marked_lines():
    # no signature found
    eq_((list(range(5)), None), e._process_marked_lines(list(range(5)), 'telt'))

    # signature in the middle of the text
    eq_((list(range(9)), None), e._process_marked_lines(list(range(9)), 'tesestelt'))

    # long line splits signature
    eq_((list(range(7)), [7, 8]),
        e._process_marked_lines(list(range(9)), 'tsslsless'))

    eq_((list(range(20)), [20]),
        e._process_marked_lines(list(range(21)), 'ttttttstttesllelelets'))

    # some signature lines could be identified as text
    eq_(([0], list(range(1, 9))), e._process_marked_lines(list(range(9)), 'tsetetest'))

    eq_(([], list(range(5))),
        e._process_marked_lines(list(range(5)), "ststt"))
