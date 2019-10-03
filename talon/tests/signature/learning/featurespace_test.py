# -*- coding: utf-8 -*-

from __future__ import absolute_import
from ... import *

from talon.signature.learning import featurespace as fs


def test_apply_features():
    s = '''This is John Doe

Tuesday @3pm suits. I'll chat to you then.

VP Research and Development, Xxxx Xxxx Xxxxx

555-226-2345

john@example.com'''
    sender = 'John <john@example.com>'
    features = fs.features(sender)
    result = fs.apply_features(s, features)
    # note that we don't consider the first line because signatures don't
    # usually take all the text, empty lines are not considered
    eq_(result, [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

    with patch.object(fs, 'SIGNATURE_MAX_LINES', 5):
        features = fs.features(sender)
        new_result = fs.apply_features(s, features)
        # result remains the same because we don't consider empty lines
        eq_(result, new_result)


def test_build_pattern():
    s = '''John Doe

VP Research and Development, Xxxx Xxxx Xxxxx

555-226-2345

john@example.com'''
    sender = 'John <john@example.com>'
    features = fs.features(sender)
    result = fs.build_pattern(s, features)
    eq_(result, [2, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1])
