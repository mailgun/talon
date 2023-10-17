# -*- coding: utf-8 -*-

from __future__ import absolute_import
from ... import *

import regex as re

from talon.signature.learning import helpers as h
from talon.signature.learning.helpers import *
from six.moves import range

# First testing regex constants.
VALID = '''
15615552323
1-561-555-1212
5613333

18008793262
800-879-3262
0-800.879.3262

04 3452488
04 -3452488
04 - 3452499

(610) 310-5555 x5555
533-1123

(021)1234567
(021)123456
(000)000000

+7 920 34 57 23
+7(920) 34 57 23
+7(920)345723
+7920345723
8920345723
21143
2-11-43
2 - 11 - 43
'''

VALID_PHONE_NUMBERS = [e.strip() for e in VALID.splitlines() if e.strip()]


def test_match_phone_numbers():
    for phone in VALID_PHONE_NUMBERS:
        assert RE_RELAX_PHONE.search(phone), "{} should be matched".format(phone)


def test_match_names():
    names = ['John R. Doe']
    for name in names:
        assert RE_NAME.match(name), "{} should be matched".format(name)


# Now test helpers functions
def test_binary_regex_search():
    assert 1 == h.binary_regex_search(re.compile("12"))("12")
    assert 0 == h.binary_regex_search(re.compile("12"))("34")


def binary_regex_match(prog):
    assert 1 == h.binary_regex_match(re.compile("12"))("12 3")
    assert 0 == h.binary_regex_match(re.compile("12"))("3 12")


def test_flatten_list():
    assert [1, 2, 3, 4, 5] == h.flatten_list([[1, 2], [3, 4, 5]])


@patch.object(h.re, 'compile')
def test_contains_sender_names(re_compile):
    with patch.object(h, 'extract_names',
                      Mock(return_value=['bob', 'smith'])) as extract_names:
        has_sender_names = h.contains_sender_names("bob.smith@example.com")
        extract_names.assert_called_with("bob.smith@example.com")
        for name in ["bob", "Bob", "smith", "Smith"]:
            assert has_sender_names(name)

        extract_names.return_value = ''
        has_sender_names = h.contains_sender_names("bob.smith@example.com")
        # if no names could be extracted fallback to the email address
        assert has_sender_names('bob.smith@example.com')

        # don't crash if there are no sender
        extract_names.return_value = ''
        has_sender_names = h.contains_sender_names("")
        assert not has_sender_names('')


def test_extract_names():
    senders_names = {
        # from example dataset
        ('Jay Rickerts <eCenter@example.com>@EXAMPLE <XXX-Jay+20Rickerts'
         '+20+3CeCenter+40example+2Ecom+3E+40EXAMPLE@EXAMPLE.com>'):
        ['Jay', 'Rickerts'],
        # if `,` is used in sender's name
        'Williams III, Bill </O=EXAMPLE/OU=NA/CN=RECIPIENTS/CN=BWILLIA5>':
        ['Williams', 'III', 'Bill'],
        # if somehow `'` or `"` are used in sender's name
        'Laura" "Goldberg <laura.goldberg@example.com>':
        ['Laura', 'Goldberg'],
        # extract from senders email address
        '<sergey@xxx.ru>': ['sergey'],
        # extract from sender's email address
        # if dots are used in the email address
        '<sergey.obukhov@xxx.ru>': ['sergey', 'obukhov'],
        # extract from sender's email address
        # if dashes are used in the email address
        '<sergey-obukhov@xxx.ru>': ['sergey', 'obukhov'],
        # extract from sender's email address
        # if `_` are used in the email address
        '<sergey_obukhov@xxx.ru>': ['sergey', 'obukhov'],
        # old style From field, found in jangada dataset
        'wcl@example.com (Wayne Long)': ['Wayne', 'Long'],
        # if only sender's name provided
        'Wayne Long': ['Wayne', 'Long'],
        # if middle name is shortened with dot
        'Sergey N.  Obukhov <serobnic@xxx.ru>': ['Sergey', 'Obukhov'],
        # not only spaces could be used as name splitters
        '  Sergey  Obukhov  <serobnic@xxx.ru>': ['Sergey', 'Obukhov'],
        # finally normal example
        'Sergey <serobnic@xxx.ru>': ['Sergey'],
        # if middle name is shortened with `,`
        'Sergey N, Obukhov': ['Sergey', 'Obukhov'],
        # if mailto used with email address and sender's name is specified
        'Sergey N, Obukhov [mailto: serobnic@xxx.ru]': ['Sergey', 'Obukhov'],
        # when only email address is given
        'serobnic@xxx.ru': ['serobnic'],
        # when nothing is given
        '': [],
        # if phone is specified in the `From:` header
        'wcl@example.com (Wayne Long +7 920 -256 - 35-09)': ['Wayne', 'Long'],
        # from crash reports `nothing to repeat`
        '* * * * <the_pod1@example.com>': ['the', 'pod'],
        '"**Bobby B**" <copymycashsystem@example.com>':
        ['Bobby', 'copymycashsystem'],
        # from crash reports `bad escape`
        '"M Ali B Azlan (GHSE/PETH)" <aliazlan@example.com>':
        ['Ali', 'Azlan'],
        ('"Ridthauddin B A Rahim (DD/PCSB)"'
         ' <ridthauddin_arahim@example.com>'): ['Ridthauddin', 'Rahim'],
        ('"Boland, Patrick (Global Xxx Group, Ireland )"'
         ' <Patrick.Boland@example.com>'): ['Boland', 'Patrick'],
        '"Mates Rate (Wine)" <amen@example.com.com>':
        ['Mates', 'Rate', 'Wine'],
        ('"Morgan, Paul (Business Xxx RI, Xxx Xxx Group)"'
         ' <paul.morgan@example.com>'): ['Morgan', 'Paul'],
        '"David DECOSTER (Domicile)" <decosterdavid@xxx.be>':
        ['David', 'DECOSTER', 'Domicile']
        }

    for sender, expected_names in senders_names.items():
        extracted_names = h.extract_names(sender)
        # check that extracted names could be compiled
        try:
            re.compile(r"|".join(map(re.escape, extracted_names)))
        except Exception as e:
            assert False, ("Failed to compile extracted names {}"
                           "\n\nReason: {}").format(extracted_names, e)
        if expected_names:
            for name in expected_names:
                assert name in extracted_names
        else:
            assert expected_names == extracted_names

    # words like `ru`, `gmail`, `com`, `org`, etc. are not considered
    # sender's names
    for word in h.BAD_SENDER_NAMES:
        assert h.extract_names(word) == []

    # duplicates are not allowed
    assert h.extract_names("sergey <sergey@example.com") == ["sergey"]


def test_categories_percent():
    assert 0.0 == h.categories_percent("qqq ggg hhh", ["Po"])
    assert 50.0 == h.categories_percent("q,w.", ["Po"])
    assert 0.0 == h.categories_percent("qqq ggg hhh", ["Nd"])
    assert 50.0 == h.categories_percent("q5", ["Nd"])
    assert 50.0 == h.categories_percent("s.s,5s", ["Po", "Nd"])
    assert 0.0 == h.categories_percent("", ["Po", "Nd"])


@patch.object(h, 'categories_percent')
def test_punctuation_percent(categories_percent):
    h.punctuation_percent("qqq")
    categories_percent.assert_called_with("qqq", ['Po'])


def test_capitalized_words_percent():
    assert 0.0 == h.capitalized_words_percent('')
    assert 100.0 == h.capitalized_words_percent('Example Corp')
    assert 50.0 == h.capitalized_words_percent('Qqq qqq Aqs 123 sss')
    assert 100.0 == h.capitalized_words_percent('Cell 713-444-7368')
    assert 100.0 == h.capitalized_words_percent('8th Floor')
    assert 0.0 == h.capitalized_words_percent('(212) 230-9276')
    assert 50.0 == h.capitalized_words_percent('Password: REMARKABLE')


def test_has_signature():
    assert h.has_signature('sender', 'sender@example.com')
    assert h.has_signature('http://www.example.com\n555 555 5555',
                           'sender@example.com')
    assert h.has_signature('http://www.example.com\naddress@example.com',
                           'sender@example.com')
    assert not h.has_signature('http://www.example.com/555-555-5555',
                               'sender@example.com')
    long_line = ''.join(['q' for e in range(28)])
    assert not h.has_signature(long_line + ' sender', 'sender@example.com')
    # wont crash on an empty string
    assert not h.has_signature('', '')
    # dont consider empty strings when analysing signature
    with patch.object(h, 'SIGNATURE_MAX_LINES', 1):
        assert 'sender\n\n', 'sender@example.com'
