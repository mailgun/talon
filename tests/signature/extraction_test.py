# -*- coding: utf-8 -*-

import os

# from six.moves import range # Removed
from unittest.mock import patch, Mock

from talon.signature import bruteforce, extraction, extract
from talon.signature import extraction as e
from talon.signature.learning import dataset
# from .. import * # Removed


def test_message_shorter_SIGNATURE_MAX_LINES():
    sender = "bob@foo.bar"
    body = """Call me ASAP, please.This is about the last changes you deployed.

Thanks in advance,
Bob"""
    text, extracted_signature = extract(body, sender)
    assert "\n".join(body.splitlines()[:2]) == text
    assert "\n".join(body.splitlines()[-2:]) == extracted_signature


def test_messages_longer_SIGNATURE_MAX_LINES():
    import sys

    kwargs = {}
    if sys.version_info > (3, 0):
        kwargs["encoding"] = "utf8"

    # Need to define STRIPPED, assuming it was from the wildcard import
    # For now, let's use a placeholder or ensure it's defined elsewhere (e.g. conftest.py or imported from fixtures)
    # This path is relative to the workspace root, assuming tests are run from there.
    STRIPPED = "tests/fixtures/signature/emails/stripped/"
    for filename in os.listdir(STRIPPED):
        full_filename = os.path.join(STRIPPED, filename)
        if not full_filename.endswith("_body"):
            continue
        sender, body = dataset.parse_msg_sender(full_filename)
        text, extracted_signature = extract(body, sender)
        extracted_signature = extracted_signature or ""
        with open(full_filename[: -len("body")] + "signature", **kwargs) as ms:
            msg_signature = ms.read()
            assert msg_signature.strip() == extracted_signature.strip()
            stripped_msg = body.strip()[: len(body.strip()) - len(msg_signature)]
            assert stripped_msg.strip() == text.strip()


def test_text_line_in_signature():
    # test signature should consist of one solid part
    sender = "bob@foo.bar"
    body = """Call me ASAP, please.This is about the last changes you deployed.

Thanks in advance,
some text which doesn't seem to be a signature at all
Bob"""

    text, extracted_signature = extract(body, sender)
    assert "\n".join(body.splitlines()[:2]) == text
    assert "\n".join(body.splitlines()[-3:]) == extracted_signature


def test_long_line_in_signature():
    sender = "bob@foo.bar"
    body = """Call me ASAP, please.This is about the last changes you deployed.

Thanks in advance,
some long text here which doesn't seem to be a signature at all
Bob"""

    text, extracted_signature = extract(body, sender)
    assert "\n".join(body.splitlines()[:-1]) == text
    assert "Bob" == extracted_signature

    body = """Thanks David,

    some *long* text here which doesn't seem to be a signature at all
    """
    # Compare rstripped body for robustness against trailing whitespace differences
    extracted_text, extracted_sig = extract(body, "david@example.com")
    assert (
        body.rstrip() == extracted_text.rstrip() if extracted_text else extracted_text
    )
    assert extracted_sig is None


def test_basic():
    msg_body = "Blah\r\n--\r\n\r\nSergey Obukhov"
    assert ("Blah", "--\r\n\r\nSergey Obukhov") == extract(msg_body, "Sergey")


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

    assert sig == extract(msg_body, "Doe")[1]


def test_over_2_text_lines_after_signature():
    body = """Blah

    Bob,
    If there are more than
    2 non signature lines in the end
    It's not signature
    """
    text, extracted_signature = extract(body, "Bob")
    assert extracted_signature is None


def test_no_signature():
    sender, body = "bob@foo.bar", "Hello"
    assert (body, None) == extract(body, sender)


def test_handles_unicode():
    # Need to define UNICODE_MSG, assuming it was from the wildcard import
    # This path is relative to the workspace root.
    UNICODE_MSG = "tests/fixtures/signature/emails/P/unicode_msg"
    sender, body = dataset.parse_msg_sender(UNICODE_MSG)
    text, extracted_signature = extract(body, sender)
    # Add an assertion here if there's an expected outcome
    assert text is not None  # Example assertion


@patch.object(extraction, "has_signature")
def test_signature_extract_crash(has_signature):
    has_signature.side_effect = Exception("Bam!")
    msg_body = "Blah\r\n--\r\n\r\nСергей"
    assert (msg_body, None) == extract(msg_body, "Сергей")


def test_mark_lines():
    with patch.object(bruteforce, "SIGNATURE_MAX_LINES", 2):
        # we analyse the 2nd line as well though it's the 6th line
        # (starting from the bottom) because we don't count empty line
        assert "ttset" == e._mark_lines(
            ["Bob Smith", "Bob Smith", "Bob Smith", "", "some text"], "Bob Smith"
        )

    with patch.object(bruteforce, "SIGNATURE_MAX_LINES", 3):
        # we don't analyse the 1st line because
        # signature cant start from the 1st line
        assert "tset" == e._mark_lines(
            ["Bob Smith", "Bob Smith", "", "some text"], "Bob Smith"
        )


def test_process_marked_lines():
    # no signature found
    assert (list(range(5)), None) == e._process_marked_lines(list(range(5)), "telt")

    # signature in the middle of the text
    assert (list(range(9)), None) == e._process_marked_lines(
        list(range(9)), "tesestelt"
    )

    # long line splits signature
    assert (list(range(7)), [7, 8]) == e._process_marked_lines(
        list(range(9)), "tsslsless"
    )

    assert (list(range(20)), [20]) == e._process_marked_lines(
        list(range(21)), "ttttttstttesllelelets"
    )

    # some signature lines could be identified as text
    assert (([0], list(range(1, 9)))) == e._process_marked_lines(
        list(range(9)), "tsetetest"
    )

    assert (([], list(range(5)))) == e._process_marked_lines(list(range(5)), "ststt")
