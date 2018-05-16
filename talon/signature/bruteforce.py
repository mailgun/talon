from __future__ import absolute_import
from talon.signature.extractor import BruteForceExtractor

from talon.signature.constants import (SIGNATURE_MAX_LINES,
                                       TOO_LONG_SIGNATURE_LINE)


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
    brute_force_extractor = BruteForceExtractor(max_lines=SIGNATURE_MAX_LINES, max_line_length=TOO_LONG_SIGNATURE_LINE)
    return brute_force_extractor.extract_signature(msg_body)


def get_signature_candidate(lines):
    """Return lines that could hold signature

    The lines should:

    * be among last SIGNATURE_MAX_LINES non-empty lines.
    * not include first line
    * be shorter than TOO_LONG_SIGNATURE_LINE
    * not include more than one line that starts with dashes
    """
    # non empty lines indexes
    brute_force_extractor = BruteForceExtractor(max_lines=SIGNATURE_MAX_LINES, max_line_length=TOO_LONG_SIGNATURE_LINE)
    return brute_force_extractor._get_signature_candidate(lines)


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
    brute_force_extractor = BruteForceExtractor(max_lines=SIGNATURE_MAX_LINES, max_line_length=TOO_LONG_SIGNATURE_LINE)
    return brute_force_extractor._mark_candidate_indexes(lines, candidate)


def _process_marked_candidate_indexes(candidate, markers):
    """
    Run regexes against candidate's marked indexes to strip
    signature candidate.

    >>> _process_marked_candidate_indexes([9, 12, 14, 15, 17], 'clddc')
    [15, 17]
    """
    brute_force_extractor = BruteForceExtractor(max_lines=SIGNATURE_MAX_LINES, max_line_length=TOO_LONG_SIGNATURE_LINE)
    return brute_force_extractor._process_marked_candidate_indexes(candidate, markers)
