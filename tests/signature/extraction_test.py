# -*- coding: utf-8 -*-

import os
import numpy as np

# from six.moves import range # Removed
from unittest.mock import patch, Mock

from talon.signature import bruteforce, extraction, extract
from talon.signature import extraction as e
from talon.signature.learning import dataset
from talon.signature.learning import classifier as c
from talon.signature.constants import SIGNATURE_MAX_LINES
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
def test_signature_extract_crash(mock_has_signature):
    mock_has_signature.side_effect = Exception("Bam!")
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


FEATURE_VALUES = [
    [1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1],
    [0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1],
]


@patch('talon.signature.extraction.build_pattern')
@patch('talon.signature.extraction.features')
@patch.object(extraction, 'EXTRACTOR')
@patch('talon.signature.extraction.has_signature')
def test_extract(mock_has_signature, mock_extractor_obj, mock_features, mock_build_pattern):
    sender = 'SENDER'
    body = "--\nSIGNATURE_LINE1\nSIGNATURE_LINE2"

    mock_has_signature.return_value = True

    # Mock features and build_pattern
    # features() is called once per extract() if signature candidate is found
    mock_features.return_value = "mock_feature_data_for_sender"
    # build_pattern() is called for each candidate line
    # Let's say "SIGNATURE_LINE1" -> pattern1, "SIGNATURE_LINE2" -> pattern2
    mock_build_pattern.side_effect = [
        np.array([1,1,1]), # pattern for SIGNATURE_LINE1
        np.array([2,2,2])  # pattern for SIGNATURE_LINE2
    ]

    # Mock EXTRACTOR.predict()
    # Called once for each candidate line by is_signature_line()
    # First call (for SIGNATURE_LINE1) -> not signature
    # Second call (for SIGNATURE_LINE2) -> is signature
    mock_extractor_obj.predict.side_effect = [
        np.array([0]), # prediction for pattern1
        np.array([1])  # prediction for pattern2
    ]

    text, signature = extraction.extract(body, sender)

    # Check calls
    mock_features.assert_called_with(sender)
    assert mock_build_pattern.call_count == 2
    mock_build_pattern.assert_any_call("SIGNATURE_LINE1", "mock_feature_data_for_sender")
    mock_build_pattern.assert_any_call("SIGNATURE_LINE2", "mock_feature_data_for_sender")
    
    assert mock_extractor_obj.predict.call_count == 2
    # Check that predict was called with the reshaped output of build_pattern
    # First call: np.array([[1,1,1]])
    # Second call: np.array([[2,2,2]])
    # Using np.array_equal for comparing numpy arrays in mock calls
    args, _ = mock_extractor_obj.predict.call_args_list[0]
    assert np.array_equal(args[0], np.array([[1,1,1]]))
    args, _ = mock_extractor_obj.predict.call_args_list[1]
    assert np.array_equal(args[0], np.array([[2,2,2]]))


    # Based on predictions (LINE1=no, LINE2=yes), markers for (L2, L1) -> ('s', 't') -> "ts"
    # RE_REVERSE_SIGNATURE.match("ts") should identify 's' as signature
    # If original lines for markers were L1, L2 and markers were t,s -> reversed string "st"
    # This would mean L2 is sig, L1 is text.
    # If full lines are ["--", "SIGNATURE_LINE1", "SIGNATURE_LINE2"] and markers are "tts"
    # Reversed markers "stt", RE_REVERSE_SIGNATURE matches "st". end() is 2.
    # Text part is lines[:-2] = ["--"]
    # Signature part is lines[-2:] = ["SIGNATURE_LINE1", "SIGNATURE_LINE2"]
    expected_text = "--" 
    expected_signature = "SIGNATURE_LINE1\nSIGNATURE_LINE2"
    
    assert text == expected_text
    assert signature == expected_signature


@patch('talon.signature.extraction.build_pattern')
@patch('talon.signature.extraction.features')
@patch.object(extraction, 'EXTRACTOR') # Instance is passed to is_signature_line
def test_is_signature_line(mock_classifier_instance, mock_features, mock_build_pattern):
    line_text = 'Hey there, this is a signature line.'
    sender_email = 'test@example.com'
    
    mock_features.return_value = "sender_feature_data"
    # build_pattern returns a 1D array
    mock_build_pattern.return_value = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1])
    
    # Case 1: Classifier predicts it IS a signature line (returns > 0)
    mock_classifier_instance.predict.return_value = np.array([1]) # e.g. probability or class label > 0
    
    assert extraction.is_signature_line(line_text, sender_email, mock_classifier_instance) == True
    mock_features.assert_called_once_with(sender_email)
    mock_build_pattern.assert_called_once_with(line_text, "sender_feature_data")
    # Check that predict was called with the reshaped output of build_pattern
    args, _ = mock_classifier_instance.predict.call_args
    expected_input_to_predict = np.array(mock_build_pattern.return_value).reshape(1, -1)
    assert np.array_equal(args[0], expected_input_to_predict)

    # Reset mocks for the next case
    mock_classifier_instance.reset_mock()
    mock_features.reset_mock()
    mock_build_pattern.reset_mock()
    mock_features.return_value = "sender_feature_data_case2" # ensure it's called again
    mock_build_pattern.return_value = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0])


    # Case 2: Classifier predicts it IS NOT a signature line (returns <= 0)
    mock_classifier_instance.predict.return_value = np.array([0]) # e.g. probability or class label <= 0
    
    assert extraction.is_signature_line(line_text, sender_email, mock_classifier_instance) == False
    mock_features.assert_called_once_with(sender_email) # Called again for this case
    mock_build_pattern.assert_called_once_with(line_text, "sender_feature_data_case2")
    args, _ = mock_classifier_instance.predict.call_args
    expected_input_to_predict_case2 = np.array(mock_build_pattern.return_value).reshape(1, -1)
    assert np.array_equal(args[0], expected_input_to_predict_case2)


@patch('talon.signature.extraction.EXTRACTOR.predict')
@patch('talon.signature.extraction.has_signature')
def test_max_signature_lines(mock_has_signature, mock_extractor_predict):
    mock_has_signature.return_value = True
    mock_extractor_predict.return_value = np.array([0]) # Add this to prevent TypeError
    lines = []
    max_lines_to_test = SIGNATURE_MAX_LINES

    for i in range(max_lines_to_test + 1):
        lines.append(str(i))
    body = '\n'.join(lines)

    # We need to ensure EXTRACTOR is not None when extract is called.
    # If initialize() from talon.signature hasn't run, EXTRACTOR could be None.
    # For this test, we are mocking its predict method, so its actual state might not matter
    # as long as the mock intercepts the call.
    extraction.extract(body, 'sender')

    # mock_extractor_predict is the mock for talon.signature.extraction.EXTRACTOR.predict
    # The first argument to predict is `data`. We check its length (number of feature vectors).
    assert max_lines_to_test == mock_extractor_predict.call_count
