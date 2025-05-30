# -*- coding: utf-8 -*-

from __future__ import absolute_import

# from ... import *
from unittest.mock import patch, Mock  # Added

import regex as re
import pytest  # Added for assert_raises equivalent (though not used yet)

from talon.constants import RE_DELIMITER
from talon.signature.constants import TOO_LONG_SIGNATURE_LINE
from talon.signature.learning import helpers as h
# from talon.signature.learning.helpers import *
# from six.moves import range # Removed

from talon.signature.learning.helpers import (
    binary_regex_match,
    binary_regex_search,
    contains_sender_names,
    has_signature,
    many_capitalized_words,
    punctuation_percent,
    RE_EMAIL,
    RE_RELAX_PHONE,
    RE_URL,
    RE_SEPARATOR,
    RE_SIGNATURE_WORDS,
    RE_SPECIAL_CHARS,
    RE_NAME,
)

# First testing regex constants.
VALID = """
15615552323
1-561-555-1212
5613333

(305) 555 1212
(305) 555-1212
(305) 555 1212
(305) 555 1212
(561) 555 1212
(561) 555-1212
(561) 5551212
(561)5551212

+1 (561) 555 1212
+1 (561) 555-1212
+1 (561) 5551212
+1(561)5551212

1 561 555 1212
1 561 555-1212
1 561 5551212

561 555 1212
561.555.1212
561 5551212
561-555-1212
"""

INVALID = """
word
"""


def test_re_relax_phone_constant():
    for s in VALID.splitlines():
        if s.strip():
            assert RE_RELAX_PHONE.search(s)

    for s in INVALID.splitlines():
        if s.strip():
            assert not RE_RELAX_PHONE.search(s)


def test_binary_regex_search():
    fn = binary_regex_search(re.compile(r"12"))
    assert 1 == fn("12")
    assert 0 == fn("34")


def test_binary_regex_match():
    fn = binary_regex_match(re.compile(r"12"))
    assert 1 == fn("12 3")
    assert 0 == fn("3 12")


def test_contains_sender_names():
    # standard case
    fn = contains_sender_names("Sergey N.  Obukhov <xxx@example.com>")
    assert 1 == fn("Sergey Obukhov")
    assert 1 == fn("BR, Sergey N.")
    assert 1 == fn("Sergey")
    assert 0 == fn("Bob")

    # only email, no name
    fn = contains_sender_names("<serobnic@mail.ru>")
    assert 1 == fn("Serobnic")
    assert 1 == fn("serobnic")
    assert 0 == fn("Bob")

    # empty sender
    fn = contains_sender_names("")
    assert 0 == fn("Serobnic")

    # sender name equals some common words like From, Sender etc
    fn = contains_sender_names("Sender Serobnic")
    assert 1 == fn("Serobnic")
    assert 0 == fn("Sender")


def test_has_signature():
    body = """
    Blah blah
    --
    Bob Smith
    www.example.com
    """
    assert has_signature(body, "Bob Smith <bob@example.com>")

    body = """
    Blah blah
    --
    Bob Smith
    actor
    www.example.com
    """
    assert has_signature(body, "Bob Smith <bob@example.com>")

    body = """
    Blah blah
    --
    Bob Smith
    actor
    painter
    www.example.com
    """
    assert not has_signature(body, "Bob Smith <bob@example.com>")

    body = """
    Blah blah
    --
    Bob Smith
    actor
    painter
    president
    www.example.com
    """
    assert not has_signature(body, "Bob Smith <bob@example.com>")

    body = """
    Blah blah
    Bob Smith
    www.example.com
    """
    assert has_signature(body, "Bob Smith <bob@example.com>")

    body = """
    Blah blah
    Bob Smith
    actor
    www.example.com
    """
    assert has_signature(body, "Bob Smith <bob@example.com>")

    body = """
    Blah blah
    Bob Smith
    actor
    painter
    www.example.com
    """
    assert not has_signature(body, "Bob Smith <bob@example.com>")

    body = """
    Blah blah
    Bob Smith
    actor
    painter
    president
    www.example.com
    """
    assert not has_signature(body, "Bob Smith <bob@example.com>")

    # Don't detect signature if sender is not in it
    body = """
    Blah blah
    --
    Bob Smith
    www.example.com
    """
    assert not has_signature(body, "Alice <alice@example.com>")

    # Detect signature if phone number is present
    body = """
    Blah blah
    --
    Bob Smith
    1-561-555-1212
    """
    assert has_signature(body, "Alice <alice@example.com>")

    # Detect signature if email is present
    body = """
    Blah blah
    --
    Bob Smith
    bob@example.com
    """
    assert has_signature(body, "Alice <alice@example.com>")

    # Phone and email
    body = """
    Blah blah
    --
    Bob Smith
    1-561-555-1212
    bob@example.com
    """
    assert has_signature(body, "Alice <alice@example.com>")

    # No signature if only one of phone/email/url is present in body
    # (and sender is not in body)
    body = """
    Blah blah
    --
    Bob Smith
    www.example.com
    """
    assert not has_signature(body, "Alice <alice@example.com>")

    body = """
    Blah blah
    --
    Bob Smith
    1-561-555-1212
    """
    assert not has_signature(body, "Alice <alice@example.com>")

    body = """
    Blah blah
    --
    Bob Smith
    bob@example.com
    """
    assert not has_signature(body, "Alice <alice@example.com>")


@patch.object(h, 'SIGNATURE_MAX_LINES', 2)
def test_too_many_signature_lines():
    body = """
    One
    Two
    Three
    """
    assert not h.has_signature(body, "sender")


def test_many_capitalized_words():
    # line has many capitalized words
    assert not h.many_capitalized_words("WORD WORD WORD word word")
    assert h.many_capitalized_words("Word Word Word word word") == 0
    # line doesn't have many capitalized words
    assert not h.many_capitalized_words("word word word word word")
    assert not h.many_capitalized_words("WORD woRD woRD")


def test_re_delimiter_search():
    s = "\nblahblahblah\n\n"
    # check that RE_DELIMITER searches from the beginning only
    # and that it includes the new line symbol \n
    # search from the beginning of the string
    assert RE_DELIMITER.search(s).group() == "\n"
    assert RE_DELIMITER.search(s).end() == 1
    # search from some position
    assert RE_DELIMITER.search(s, 1).group() == "\n"


def test_re_relax_phone():
    # check that it does not fail like this
    # self.assertTrue(RE_RELAX_PHONE.search(s)) FAILED
    # Sunday, March 20, 2011 1:04 AM
    s = "Sunday, March 20, 2011 1:04 AM"
    assert RE_RELAX_PHONE.search(s)

    # check that it finds the phone number
    s = "(123) 456-7890"
    assert RE_RELAX_PHONE.search(s)


def test_re_signature_words():
    # String does not contain signature words
    s = "Some text --- Name"
    assert not RE_SIGNATURE_WORDS.search(s)

    # String contains signature words
    s = "Thanks, Bob"
    assert RE_SIGNATURE_WORDS.search(s)
