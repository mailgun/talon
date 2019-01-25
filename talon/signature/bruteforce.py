from __future__ import absolute_import

import logging

import regex

from talon.signature.constants import (SIGNATURE_MAX_LINES,
                                       TOO_LONG_SIGNATURE_LINE,
                                       MAX_BLOCK_SIGNATURE_LINES)
from talon.utils import get_delimiter

log = logging.getLogger(__name__)

# regex to fetch signature based on common signature words
RE_SIGNATURE = regex.compile(r'''
               (
                   (?:
                       ^[\s]*--*[\s]*[a-z \.]*$
                       |
                       ^[\s]*—+[\s]*$
                       |
                       ^thanks[\s,!]*$
                       |
                       ^regards[\s,!]*$
                       |
                       ^kind\sregards[\s,!]*$
                       |
                       ^take\scare[\s,!]*$
                       |
                       ^cheers[\s,!]*$
                       |
                       ^sincerely[\s,!]*$
                       |
                       ^best[ a-z]*[\s,!]*$
                   )
                   .*
               )
               ''', regex.I | regex.X | regex.M | regex.S)

# signatures appended by phone email clients
RE_PHONE_SIGNATURE = regex.compile(r'''
               (
                   (?:
                       ^sent[ ]{1}from[ ]{1}my[\s,!\w]*$
                       |
                       ^sent[ ]from[ ]Mailbox[ ]for[ ]iPhone.*$
                       |
                       ^sent[ ]([\S]*[ ])?from[ ]my[ ]BlackBerry.*$
                       |
                       ^Enviado[ ]desde[ ]mi[ ]([\S]+[ ]){0,2}BlackBerry.*$
                   )
                   .*
               )
               ''', regex.I | regex.X | regex.M | regex.S)

# see _mark_candidate_indexes() for details
# c - could be signature line
# d - line starts with dashes (could be signature or list item)
# l - long line
RE_SIGNATURE_CANDIDATE = regex.compile(r'''
    (?P<candidate>c+d)[^d]
    |
    (?P<candidate>c+d)$
    |
    (?P<candidate>c+)
    |
    (?P<candidate>d)[^d]
    |
    (?P<candidate>d)$
''', regex.I | regex.X | regex.M | regex.S)

RE_PHONE_NUMBER = regex.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
RE_EMAIL_ADDRESS = regex.compile(r'[^@]+@[^@]+\.[^@]+')

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
            signature = _check_block_signature(stripped_body)
        else:
            signature = signature.group()

        if not signature:
            return (stripped_body.strip(), phone_signature)
        else:
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
    # at first consider everything to be potential signature lines
    markers = list('c' * len(candidate))

    # mark lines starting from bottom up
    for i, line_idx in reversed(list(enumerate(candidate))):
        if len(lines[line_idx].strip()) > TOO_LONG_SIGNATURE_LINE:
            markers[i] = 'l'
        else:
            line = lines[line_idx].strip()
            if line.startswith('-') and line.strip("-"):
                markers[i] = 'd'

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


def _check_block_signature(msg_body):
    """
    Attempts to identify signatures of the form:

    > Blah Blah Blah
    > Blah Blah
    >
    > John Smith
    > Email Writer
    > Phone: 555-5555

    It will match any couple lines of text at the bottom of an email
    that contain a phone number and/or an email address.
    """

    # Save the delimiter for joining later
    delimiter = get_delimiter(msg_body)

    lines = msg_body.splitlines()

    found_content = False

    found_phone = False
    found_email = False

    line_count = len(lines)

    # Loop through the email lines from the bottom
    for i in range(line_count - 1, max(line_count - MAX_BLOCK_SIGNATURE_LINES - 2, 0), -1):
        if len(lines[i]) > TOO_LONG_SIGNATURE_LINE:
            # Too long line, not a signature
            return None
        
        if lines[i].strip() == '':
            if not found_content:
                # Haven't hit any text yet, so keep continuing
                continue
            else:
                if found_phone or found_email:
                    # It's a signature
                    return delimiter.join(lines[(i + 1):len(lines)])
                else:
                    # It's not a signature
                    return None
        else:
            found_content = True

            if RE_PHONE_NUMBER.match(lines[i]):
                found_phone = True
            if RE_EMAIL_ADDRESS.match(lines[i]):
                found_email = True
    
    return None