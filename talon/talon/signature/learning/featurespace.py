# -*- coding: utf-8 -*-

""" The module provides functions for conversion of a message body/body lines
into classifiers features space.

The body and the message sender string are converted into unicode before
applying features to them.
"""

from __future__ import absolute_import
from talon.signature.constants import (SIGNATURE_MAX_LINES,
                                       TOO_LONG_SIGNATURE_LINE)
from talon.signature.learning.helpers import *
from six.moves import zip
from functools import reduce


def features(sender=''):
    '''Returns a list of signature features.'''
    return [
        # This one isn't from paper.
        # Meant to match companies names, sender's names, address.
        many_capitalized_words,
        # This one is not from paper.
        # Line is too long.
        # This one is less aggressive than `Line is too short`
        lambda line: 1 if len(line) > TOO_LONG_SIGNATURE_LINE else 0,
        # Line contains email pattern.
        binary_regex_search(RE_EMAIL),
        # Line contains url.
        binary_regex_search(RE_URL),
        # Line contains phone number pattern.
        binary_regex_search(RE_RELAX_PHONE),
        # Line matches the regular expression "^[\s]*---*[\s]*$".
        binary_regex_match(RE_SEPARATOR),
        # Line has a sequence of 10 or more special characters.
        binary_regex_search(RE_SPECIAL_CHARS),
        # Line contains any typical signature words.
        binary_regex_search(RE_SIGNATURE_WORDS),
        # Line contains a pattern like Vitor R. Carvalho or William W. Cohen.
        binary_regex_search(RE_NAME),
        # Percentage of punctuation symbols in the line is larger than 50%
        lambda line: 1 if punctuation_percent(line) > 50 else 0,
        # Percentage of punctuation symbols in the line is larger than 90%
        lambda line: 1 if punctuation_percent(line) > 90 else 0,
        contains_sender_names(sender)
        ]


def apply_features(body, features):
    '''Applies features to message body lines.

    Returns list of lists. Each of the lists corresponds to the body line
    and is constituted by the numbers of features occurrences (0 or 1).
    E.g. if element j of list i equals 1 this means that
    feature j occurred in line i (counting from the last line of the body).
    '''
    # collect all non empty lines
    lines = [line for line in body.splitlines() if line.strip()]

    # take the last SIGNATURE_MAX_LINES
    last_lines = lines[-SIGNATURE_MAX_LINES:]

    # apply features, fallback to zeros
    return ([[f(line) for f in features] for line in last_lines] or
            [[0 for f in features]])


def build_pattern(body, features):
    '''Converts body into a pattern i.e. a point in the features space.

    Applies features to the body lines and sums up the results.
    Elements of the pattern indicate how many times a certain feature occurred
    in the last lines of the body.
    '''
    line_patterns = apply_features(body, features)
    return reduce(lambda x, y: [i + j for i, j in zip(x, y)], line_patterns)
