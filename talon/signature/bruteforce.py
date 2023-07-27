from __future__ import absolute_import

import logging
from talon.constants import (SIGNATURE_MAX_LINES,TOO_LONG_SIGNATURE_LINE,RE_SIGNATURE,RE_FOOTER_WORDS,RE_PHONE_SIGNATURE,RE_SIGNATURE_CANDIDATE)
from talon.utils import get_delimiter

log = logging.getLogger(__name__)

def extract_signature(msg_body):
    '''
    Analyzes message for a presence of signature block (by common patterns)
    and returns tuple with two elements: message text without signature block
    and the signature itself.

    >>> extract_signature('Hey man! How r u?\n\n--\nRegards,\nRoman')
    ('Hey man! How r u?', '--\nRegards,\nRoman')

    >>> extract_signature('Hey man!')
    ('Hey man!', None)
    '''
    try:
        # identify line delimiter first
        delimiter = get_delimiter(msg_body)

        # make an assumption
        stripped_body = msg_body.strip()
        phone_signature = None

        # strip off phone signature
        phone_signature = RE_PHONE_SIGNATURE.search(msg_body)
        if phone_signature:
            stripped_body = stripped_body[:phone_signature.start()]
            phone_signature = phone_signature.group()

        # decide on signature candidate
        lines = stripped_body.splitlines()
        candidate = get_signature_candidate(lines)
        candidate = delimiter.join(candidate)

        # try to extract signature
        signature = RE_SIGNATURE.search(candidate)
        if not signature:
            return (stripped_body.strip(), phone_signature)
        else:
            signature = signature.group()
            # when we splitlines() and then join them
            # we can lose a new line at the end
            # we did it when identifying a candidate
            # so we had to do it for stripped_body now
            stripped_body = delimiter.join(lines)
            stripped_body = stripped_body[:-len(signature)]

            if phone_signature:
                signature = delimiter.join([signature, phone_signature])

            return (stripped_body.strip(),
                    signature.strip())
    except Exception:
        log.exception('ERROR extracting signature')
        return (msg_body, None)


def get_signature_candidate(lines):
    """Return lines that could hold signature

    The lines should:

    * be among last SIGNATURE_MAX_LINES non-empty lines.
    * not include first line
    * be shorter than TOO_LONG_SIGNATURE_LINE
    * not include more than one line that starts with dashes
    """
    # non empty lines indexes
    non_empty = [i for i, line in enumerate(lines) if line.strip()]

    # if message is empty or just one line then there is no signature
    if len(non_empty) <= 1:
        return []

    # we don't expect signature to start at the 1st line
    candidate = non_empty[1:]
    # signature shouldn't be longer then SIGNATURE_MAX_LINES
    candidate = candidate[-SIGNATURE_MAX_LINES:]

    markers = _mark_candidate_indexes(lines, candidate)
    candidate = _process_marked_candidate_indexes(candidate, markers)

    # get actual lines for the candidate instead of indexes
    if candidate:
        candidate = lines[candidate[0]:]
        return candidate

    return []


def _mark_candidate_indexes(lines, candidate):
    """Mark candidate indexes with markers

    Markers:

    * c - line that could be a signature line
    * l - long line
    * d - line that starts with dashes but has other chars as well

    >>> _mark_candidate_lines(['Some text', '', '-', 'Bob'], [0, 2, 3])
    'cdc'
    """
    # Footers start at the last line whene we traverse backwords. So once it's broken, we don't accept matches to the word.
    search_for_footer = True
    # at first consider everything to be potential signature lines
    markers = list('c' * len(candidate))
    # mark lines starting from bottom up
    for i, line_idx in reversed(list(enumerate(candidate))):
        # This allows us to keep longer footer lines as potential candidates until we see a break in a signature footer
        if search_for_footer and RE_FOOTER_WORDS.search(lines[line_idx]):
            markers[i] = 'c'
        elif search_for_footer and RE_SIGNATURE.search(lines[line_idx]):
            markers[i] = 'c'
            search_for_footer = False
        elif len(lines[line_idx].strip()) > TOO_LONG_SIGNATURE_LINE:
            markers[i] = 'l'
            search_for_footer = False
        else:
            line = lines[line_idx].strip()
            if (line.startswith('-') and line.strip("-")):
                markers[i] = 'd'
            search_for_footer = False

    return "".join(markers)


def _process_marked_candidate_indexes(candidate, markers):
    """
    Run regexes against candidate's marked indexes to strip
    signature candidate.

    >>> _process_marked_candidate_indexes([9, 12, 14, 15, 17], 'clddc')
    [15, 17]
    """
    match = RE_SIGNATURE_CANDIDATE.match(markers[::-1])
    return candidate[-match.end('candidate'):] if match else []
