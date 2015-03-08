# -*- coding: utf-8 -*-

from ... import *
import os

from numpy import genfromtxt

from talon.signature.learning import dataset as d

from talon.signature.learning.featurespace import features


def test_is_sender_filename():
    assert_false(d.is_sender_filename("foo/bar"))
    assert_false(d.is_sender_filename("foo/bar_body"))
    ok_(d.is_sender_filename("foo/bar_sender"))


def test_build_sender_filename():
    eq_("foo/bar_sender", d.build_sender_filename("foo/bar_body"))


def test_parse_msg_sender():
    sender, msg = d.parse_msg_sender(EML_MSG_FILENAME)
    # if the message in eml format
    with open(EML_MSG_FILENAME) as f:
        eq_(sender,
            " Alex Q <xxx@yahoo.com>")
        eq_(msg, f.read())

    # if the message sender is stored in a separate file
    sender, msg = d.parse_msg_sender(MSG_FILENAME_WITH_BODY_SUFFIX)
    with open(MSG_FILENAME_WITH_BODY_SUFFIX) as f:
        eq_(sender, u"john@example.com")
        eq_(msg, f.read())


def test_build_extraction_dataset():
    if os.path.exists(os.path.join(TMP_DIR, 'extraction.data')):
        os.remove(os.path.join(TMP_DIR, 'extraction.data'))
    d.build_extraction_dataset(os.path.join(EMAILS_DIR, 'P'),
                               os.path.join(TMP_DIR,
                                            'extraction.data'), 1)

    filename = os.path.join(TMP_DIR, 'extraction.data')
    file_data = genfromtxt(filename, delimiter=",")
    test_data = file_data[:, :-1]

    # the result is a loadable signature extraction dataset
    # 32 comes from 3 emails in emails/P folder, 11 lines checked to be
    # a signature, one email has only 10 lines
    eq_(test_data.shape[0], 32)
    eq_(len(features('')), test_data.shape[1])
