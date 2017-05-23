# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

import numpy
import regex as re
from talon.signature.bruteforce import get_signature_candidate
from talon.signature.learning.featurespace import features, build_pattern
from talon.signature.learning.helpers import has_signature
from talon.utils import get_delimiter

log = logging.getLogger(__name__)

EXTRACTOR = None

# regex signature pattern for reversed lines
# assumes that all long lines have been excluded
RE_REVERSE_SIGNATURE = re.compile(r'''
# signature should consists of blocks like this
(?:
   # it could end with empty line
   e*
   # there could be text lines but no more than 2 in a row
   (te*){,2}
   # every block should end with signature line
   s
)+
''', re.I | re.X | re.M | re.S)


def is_signature_line(line, sender, classifier):
    '''Checks if the line belongs to signature. Returns True or False.'''
    data = numpy.array(build_pattern(line, features(sender)))
    return classifier.predict(data) > 0


def extract(body, sender):
    """Strips signature from the body of the message.

    Returns stripped body and signature as a tuple.
    If no signature is found the corresponding returned value is None.
    """
    try:
        delimiter = get_delimiter(body)

        body = body.strip()

        if has_signature(body, sender):
            lines = body.splitlines()

            markers = _mark_lines(lines, sender)
            text, signature = _process_marked_lines(lines, markers)

            if signature:
                text = delimiter.join(text)
                if text.strip():
                    return (text, delimiter.join(signature))
    except Exception as e:
        log.exception('ERROR when extracting signature with classifiers')

    return (body, None)


def _mark_lines(lines, sender):
    """Mark message lines with markers to distinguish signature lines.

    Markers:

    * e - empty line
    * s - line identified as signature
    * t - other i.e. ordinary text line

    >>> mark_message_lines(['Some text', '', 'Bob'], 'Bob')
    'tes'
    """
    global EXTRACTOR

    candidate = get_signature_candidate(lines)

    # at first consider everything to be text no signature
    markers = list('t' * len(lines))

    # mark lines starting from bottom up
    # mark only lines that belong to candidate
    # no need to mark all lines of the message
    for i, line in reversed(list(enumerate(candidate))):
        # markers correspond to lines not candidate
        # so we need to recalculate our index to be
        # relative to lines not candidate
        j = len(lines) - len(candidate) + i
        if not line.strip():
            markers[j] = 'e'
        elif is_signature_line(line, sender, EXTRACTOR):
            markers[j] = 's'

    return "".join(markers)


def _process_marked_lines(lines, markers):
    """Run regexes against message's marked lines to strip signature.

    >>> _process_marked_lines(['Some text', '', 'Bob'], 'tes')
    (['Some text', ''], ['Bob'])
    """
    # reverse lines and match signature pattern for reversed lines
    signature = RE_REVERSE_SIGNATURE.match(markers[::-1])
    if signature:
        return (lines[:-signature.end()], lines[-signature.end():])

    return (lines, None)

