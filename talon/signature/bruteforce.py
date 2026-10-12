from __future__ import absolute_import, annotations

import logging

import regex as re

from talon.signature.constants import (SIGNATURE_MAX_LINES,
                                       TOO_LONG_SIGNATURE_LINE)
from talon.signature.learning.helpers import is_url_only_line
from talon.utils import get_delimiter

log = logging.getLogger(__name__)

# regex to fetch signature based on common signature words
RE_SIGNATURE = re.compile(r'''
               (
                   (?:
                       ^[\s]*--*[\s]*[a-z \.]*$
                       |
                       ^thanks[\s,!]*$
                       |
                       ^regards[\s,!]*$
                       |
                       ^cheers[\s,!]*$
                       |
                       ^best[ a-z]*[\s,!]*$
                   )
                   .*
               )
               ''', re.I | re.X | re.M | re.S)

# signatures appended by phone email clients
RE_PHONE_SIGNATURE = re.compile(r'''
               (
                   (?:
                       ^sent[ ]{1}from[ ]{1}my[\s,!\w]*$
                       |
                       ^sent[ ]from[ ]Mailbox[ ]for[ ]iPhone.*$
                       |
                       ^sent[ ]([\S]*[ ])?from[ ]my[ ]BlackBerry.*$
                       |
                       ^Enviado[ ]desde[ ]mi[ ]([\S]+[ ]){0,2}BlackBerry.*$
                       |
                       ^sent[ ]from[ ]my[ ]Android[\S ]*K-9[\S ]*$
                       |
                       ^Envoyé[ ]de[ ]mon[ ]appareil[ ]Android[\S ]*K-9[\S ]*$
                   )
                   .*
               )
               ''', re.I | re.X | re.M | re.S)

# see _mark_candidate_indexes() for details
# c - could be signature line
# d - line starts with dashes (could be signature or list item)
# l - long line
RE_SIGNATURE_CANDIDATE = re.compile(r'''
    (?P<candidate>c+d)[^d]
    |
    (?P<candidate>c+d)$
    |
    (?P<candidate>c+)
    |
    (?P<candidate>d)[^d]
    |
    (?P<candidate>d)$
''', re.I | re.X | re.M | re.S)


def extract_signature(msg_body: str) -> tuple[str, str | None]:
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
        phone_signature_match = RE_PHONE_SIGNATURE.search(msg_body)
        if phone_signature_match:
            stripped_body = stripped_body[:phone_signature_match.start()]
            phone_signature = phone_signature_match.group()

        # decide on signature candidate
        lines = stripped_body.splitlines()
        candidate = delimiter.join(get_signature_candidate(lines))

        # try to extract signature
        signature_match = RE_SIGNATURE.search(candidate)
        if not signature_match:
            return (stripped_body.strip(), phone_signature)
        else:
            signature = signature_match.group()
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


def get_signature_candidate(lines: list[str]) -> list[str]:
    """Return lines that could hold signature

    The lines should:

    * be among last SIGNATURE_MAX_LINES non-empty lines.
      A URL-only line does not consume one of those slots.
    * not include first line
    * be shorter than TOO_LONG_SIGNATURE_LINE, unless the line is a URL
    * not include more than one line that starts with dashes
    """
    # non empty lines indexes
    non_empty = [i for i, line in enumerate(lines) if line.strip()]

    # if message is empty or just one line then there is no signature
    if len(non_empty) <= 1:
        return []

    # we don't expect signature to start at the 1st line
    tail = non_empty[1:]
    # URL-only lines stay in the slice but do not use the line budget,
    # same as blank lines. Otherwise a stack of long links pushes the
    # signature header (for example "--") out of the window.
    substantive = [i for i in tail if not is_url_only_line(lines[i])]
    budget = substantive[-SIGNATURE_MAX_LINES:]
    if budget:
        start = budget[0]
        candidate = [i for i in tail if i >= start]
    else:
        candidate = tail

    markers = _mark_candidate_indexes(lines, candidate)
    candidate = _process_marked_candidate_indexes(candidate, markers)

    # get actual lines for the candidate instead of indexes
    if candidate:
        return lines[candidate[0]:]

    return []


def _mark_candidate_indexes(lines: list[str], candidate: list[int]) -> str:
    """Mark candidate indexes with markers

    Markers:

    * c - line that could be a signature line
    * l - long line
    * d - line that starts with dashes but has other chars as well

    >>> _mark_candidate_lines(['Some text', '', '-', 'Bob'], [0, 2, 3])
    'cdc'
    """
    # at first consider everything to be potential signature lines
    markers = list('c' * len(candidate))

    # mark lines starting from bottom up
    for i, line_idx in reversed(list(enumerate(candidate))):
        line = lines[line_idx].strip()
        # Long links are signature content. Long prose still splits it.
        if len(line) > TOO_LONG_SIGNATURE_LINE and not is_url_only_line(line):
            markers[i] = 'l'
        elif line.startswith('-') and line.strip("-"):
            markers[i] = 'd'

    return "".join(markers)


def _process_marked_candidate_indexes(candidate: list[int],
                                      markers: str) -> list[int]:
    """
    Run regexes against candidate's marked indexes to strip
    signature candidate.

    >>> _process_marked_candidate_indexes([9, 12, 14, 15, 17], 'clddc')
    [15, 17]
    """
    match = RE_SIGNATURE_CANDIDATE.match(markers[::-1])
    return candidate[-match.end('candidate'):] if match else []
