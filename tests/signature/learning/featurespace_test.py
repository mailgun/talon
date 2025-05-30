# -*- coding: utf-8 -*-

# from ... import * # Removed
from unittest.mock import patch, Mock  # Added

from talon.signature.learning import featurespace as fs


def test_apply_features():
    s = """This is John Doe

Tuesday @3pm suits. I'll chat to you then.

VP Research and Development, Xxxx Xxxx Xxxxx

555-226-2345

john@example.com"""
    sender = "John <john@example.com>"
    features_extracted = fs.features(
        sender
    )  # Renamed to avoid conflict with imported module alias
    result = fs.apply_features(s, features_extracted)
    # note that we don't consider the first line because signatures don't
    # usually take all the text, empty lines are not considered
    assert result == [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    with patch.object(fs, "SIGNATURE_MAX_LINES", 5):
        features_extracted_new = fs.features(sender)  # Renamed
        new_result = fs.apply_features(s, features_extracted_new)
        # result remains the same because we don't consider empty lines
        assert result == new_result


def test_build_pattern():
    s = """John Doe

VP Research and Development, Xxxx Xxxx Xxxxx

555-226-2345

john@example.com"""
    sender = "John <john@example.com>"
    features_extracted = fs.features(sender)  # Renamed
    result = fs.build_pattern(s, features_extracted)
    assert result == [2, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1]
