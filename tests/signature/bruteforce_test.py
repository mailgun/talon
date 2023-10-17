# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .. import *

from talon.signature import bruteforce


def test_empty_body():
    assert ('', None) == bruteforce.extract_signature('')


def test_no_signature():
    msg_body = 'Hey man!'
    assert (msg_body, None) == bruteforce.extract_signature(msg_body)


def test_signature_only():
    msg_body = '--\nRoman'
    assert (msg_body, None) == bruteforce.extract_signature(msg_body)


def test_signature_separated_by_dashes():
    msg_body = '''Hey man! How r u?
---
Roman'''
    assert ('Hey man! How r u?', '---\nRoman') == \
        bruteforce.extract_signature(msg_body)

    msg_body = '''Hey!
-roman'''
    assert ('Hey!', '-roman') == bruteforce.extract_signature(msg_body)

    msg_body = '''Hey!

- roman'''
    assert ('Hey!', '- roman') == bruteforce.extract_signature(msg_body)

    msg_body = '''Wow. Awesome!
--
Bob Smith'''
    assert ('Wow. Awesome!', '--\nBob Smith') == \
        bruteforce.extract_signature(msg_body)


def test_signature_words():
    msg_body = '''Hey!

Thanks!
Roman'''
    assert ('Hey!', 'Thanks!\nRoman') == \
        bruteforce.extract_signature(msg_body)

    msg_body = '''Hey!
--
Best regards,

Roman'''
    assert ('Hey!', '--\nBest regards,\n\nRoman') == \
        bruteforce.extract_signature(msg_body)

    msg_body = '''Hey!
--
--
Regards,
Roman'''
    assert ('Hey!', '--\n--\nRegards,\nRoman') == \
        bruteforce.extract_signature(msg_body)


def test_iphone_signature():
    msg_body = '''Hey!

Sent from my iPhone!'''
    assert ('Hey!', 'Sent from my iPhone!') == \
        bruteforce.extract_signature(msg_body)


def test_mailbox_for_iphone_signature():
    msg_body = """Blah
Sent from Mailbox for iPhone"""
    assert ("Blah", "Sent from Mailbox for iPhone") == \
        bruteforce.extract_signature(msg_body)


def test_line_starts_with_signature_word():
    msg_body = '''Hey man!
Thanks for your attention.
--
Thanks!
Roman'''
    assert ('Hey man!\nThanks for your attention.', '--\nThanks!\nRoman') == \
        bruteforce.extract_signature(msg_body)


def test_line_starts_with_dashes():
    msg_body = '''Hey man!
Look at this:

--> one
--> two
--
Roman'''
    assert ('Hey man!\nLook at this:\n\n--> one\n--> two', '--\nRoman') == \
        bruteforce.extract_signature(msg_body)


def test_blank_lines_inside_signature():
    msg_body = '''Blah.

-Lev.

Sent from my HTC smartphone!'''
    assert ('Blah.', '-Lev.\n\nSent from my HTC smartphone!') == \
        bruteforce.extract_signature(msg_body)

    msg_body = '''Blah
--

John Doe'''
    assert ('Blah', '--\n\nJohn Doe') == bruteforce.extract_signature(msg_body)


def test_blackberry_signature():
    msg_body = """Heeyyoooo.
Sent wirelessly from my BlackBerry device on the Bell network.
Envoyé sans fil par mon terminal mobile BlackBerry sur le réseau de Bell."""
    assert ('Heeyyoooo.', msg_body[len('Heeyyoooo.\n'):]) == \
        bruteforce.extract_signature(msg_body)

    msg_body = u"""Blah
Enviado desde mi oficina mÃ³vil BlackBerryÂ® de Telcel"""

    assert ('Blah', u'Enviado desde mi oficina mÃ³vil BlackBerryÂ® de Telcel') == \
        bruteforce.extract_signature(msg_body)


@patch.object(bruteforce, 'get_delimiter', Mock(side_effect=Exception()))
def test_crash_in_extract_signature():
    msg_body = '''Hey!
-roman'''
    assert (msg_body, None) == bruteforce.extract_signature(msg_body)


def test_signature_cant_start_from_first_line():
    msg_body = """Thanks,

Blah

regards

John Doe"""
    assert ('Thanks,\n\nBlah', 'regards\n\nJohn Doe') == \
        bruteforce.extract_signature(msg_body)


@patch.object(bruteforce, 'SIGNATURE_MAX_LINES', 2)
def test_signature_max_lines_ignores_empty_lines():
    msg_body = """Thanks,
Blah

regards


John Doe"""
    assert ('Thanks,\nBlah', 'regards\n\n\nJohn Doe') == \
        bruteforce.extract_signature(msg_body)


def test_get_signature_candidate():
    # if there aren't at least 2 non-empty lines there should be no signature
    for lines in [], [''], ['', ''], ['abc']:
        assert [] == bruteforce.get_signature_candidate(lines)

    # first line never included
    lines = ['text', 'signature']
    assert ['signature'] == bruteforce.get_signature_candidate(lines)

    # test when message is shorter then SIGNATURE_MAX_LINES
    with patch.object(bruteforce, 'SIGNATURE_MAX_LINES', 3):
        lines = ['text', '', '', 'signature']
        assert ['signature'] == bruteforce.get_signature_candidate(lines)

    # test when message is longer then the SIGNATURE_MAX_LINES
    with patch.object(bruteforce, 'SIGNATURE_MAX_LINES', 2):
        lines = ['text1', 'text2', 'signature1', '', 'signature2']
        assert ['signature1', '', 'signature2'] == \
            bruteforce.get_signature_candidate(lines)

    # test long lines not encluded
    with patch.object(bruteforce, 'TOO_LONG_SIGNATURE_LINE', 3):
        lines = ['BR,', 'long', 'Bob']
        assert ['Bob'] == bruteforce.get_signature_candidate(lines)

    # test list (with dashes as bullet points) not included
    lines = ['List:,', '- item 1', '- item 2', '--', 'Bob']
    assert ['--', 'Bob'] == bruteforce.get_signature_candidate(lines)


def test_mark_candidate_indexes():
    with patch.object(bruteforce, 'TOO_LONG_SIGNATURE_LINE', 3):
        # spaces are not considered when checking line length
        assert 'clc' == \
            bruteforce._mark_candidate_indexes(
                ['BR,  ', 'long', 'Bob'],
                [0, 1, 2])

        # only candidate lines are marked
        # if line has only dashes it's a candidate line
        assert 'ccdc' == \
            bruteforce._mark_candidate_indexes(
                ['-', 'long', '-', '- i', 'Bob'],
                [0, 2, 3, 4])


def test_process_marked_candidate_indexes():
    assert [2, 13, 15] == \
        bruteforce._process_marked_candidate_indexes(
            [2, 13, 15], 'dcc')

    assert [15] == \
        bruteforce._process_marked_candidate_indexes(
            [2, 13, 15], 'ddc')

    assert [13, 15] == \
        bruteforce._process_marked_candidate_indexes(
            [13, 15], 'cc')

    assert [15] == \
        bruteforce._process_marked_candidate_indexes(
            [15], 'lc')

    assert [15] == \
        bruteforce._process_marked_candidate_indexes(
            [13, 15], 'ld')
