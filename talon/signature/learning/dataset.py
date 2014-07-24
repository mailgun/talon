# -*- coding: utf-8 -*-

"""The module's functions build datasets to train/assess classifiers.

For signature detection the input should be a folder with two directories
that contain emails with and without signatures.

For signature extraction the input should be a folder with annotated emails.
To indicate that a line is a signature line use #sig# at the start of the line.

A sender of an email could be specified in the same file as
the message body e.g. when .eml format is used or in a separate file.

In the letter case it is assumed that a body filename ends with the `_body`
suffix and the corresponding sender file has the same name except for the
suffix which should be `_sender`.
"""

import os
import regex as re

from talon.signature.constants import SIGNATURE_MAX_LINES
from talon.signature.learning.featurespace import build_pattern, features


SENDER_SUFFIX = '_sender'
BODY_SUFFIX = '_body'

SIGNATURE_ANNOTATION = '#sig#'
REPLY_ANNOTATION = '#reply#'

ANNOTATIONS = [SIGNATURE_ANNOTATION, REPLY_ANNOTATION]


def is_sender_filename(filename):
    """Checks if the file could contain message sender's name."""
    return filename.endswith(SENDER_SUFFIX)


def build_sender_filename(msg_filename):
    """By the message filename gives expected sender's filename."""
    return msg_filename[:-len(BODY_SUFFIX)] + SENDER_SUFFIX


def parse_msg_sender(filename, sender_known=True):
    """Given a filename returns the sender and the message.

    Here the message is assumed to be a whole MIME message or just
    message body.

    >>> sender, msg = parse_msg_sender('msg.eml')
    >>> sender, msg = parse_msg_sender('msg_body')

    If you don't want to consider the sender's name in your classification
    algorithm:
    >>> parse_msg_sender(filename, False)
    """
    sender, msg = None, None
    if os.path.isfile(filename) and not is_sender_filename(filename):
        with open(filename) as f:
            msg = f.read()
            sender = u''
            if sender_known:
                sender_filename = build_sender_filename(filename)
                if os.path.exists(sender_filename):
                    with open(sender_filename) as sender_file:
                        sender = sender_file.read().strip()
                else:
                    # if sender isn't found then the next line fails
                    # and it is ok
                    lines = msg.splitlines()
                    for line in lines:
                        match = re.match('From:(.*)', line)
                        if match:
                            sender = match.group(1)
                            break
    return (sender, msg)


def build_detection_class(folder, dataset_filename,
                          label, sender_known=True):
    """Builds signature detection class.

    Signature detection dataset includes patterns for two classes:
    * class for positive patterns (goes with label 1)
    * class for negative patterns (goes with label -1)

    The patterns are build of emails from `folder` and appended to
    dataset file.

    >>> build_signature_detection_class('emails/P', 'train.data', 1)
    """
    with open(dataset_filename, 'a') as dataset:
        for filename in os.listdir(folder):
            filename = os.path.join(folder, filename)
            sender, msg = parse_msg_sender(filename, sender_known)
            if sender is None or msg is None:
                continue
            msg = re.sub('|'.join(ANNOTATIONS), '', msg)
            X = build_pattern(msg, features(sender))
            X.append(label)
            labeled_pattern = ','.join([str(e) for e in X])
            dataset.write(labeled_pattern + '\n')


def build_detection_dataset(folder, dataset_filename,
                            sender_known=True):
    """Builds signature detection dataset using emails from folder.

    folder should have the following structure:
    x-- folder
    |    x-- P
    |    |    | -- positive sample email 1
    |    |    | -- positive sample email 2
    |    |    | -- ...
    |    x-- N
    |    |    | -- negative sample email 1
    |    |    | -- negative sample email 2
    |    |    | -- ...

    If the dataset file already exist it is rewritten.
    """
    if os.path.exists(dataset_filename):
        os.remove(dataset_filename)
    build_detection_class(os.path.join(folder, u'P'),
                          dataset_filename, 1)
    build_detection_class(os.path.join(folder, u'N'),
                          dataset_filename, -1)


def build_extraction_dataset(folder, dataset_filename,
                             sender_known=True):
    """Builds signature extraction dataset using emails in the `folder`.

    The emails in the `folder` should be annotated i.e. signature lines
    should be marked with `#sig#`.
    """
    if os.path.exists(dataset_filename):
        os.remove(dataset_filename)
    with open(dataset_filename, 'a') as dataset:
        for filename in os.listdir(folder):
            filename = os.path.join(folder, filename)
            sender, msg = parse_msg_sender(filename, sender_known)
            if not sender or not msg:
                continue
            lines = msg.splitlines()
            for i in xrange(1, min(SIGNATURE_MAX_LINES,
                                   len(lines)) + 1):
                line = lines[-i]
                label = -1
                if line[:len(SIGNATURE_ANNOTATION)] == \
                        SIGNATURE_ANNOTATION:
                    label = 1
                    line = line[len(SIGNATURE_ANNOTATION):]
                elif line[:len(REPLY_ANNOTATION)] == REPLY_ANNOTATION:
                    line = line[len(REPLY_ANNOTATION):]

                X = build_pattern(line, features(sender))
                X.append(label)
                labeled_pattern = ','.join([str(e) for e in X])
                dataset.write(labeled_pattern + '\n')
