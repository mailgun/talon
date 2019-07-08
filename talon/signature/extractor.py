"""
Module with object oriented approach to signature extractions. Built to be more
flexible and to support more languages.
"""
from __future__ import absolute_import
import re
import logging

from abc import ABC, abstractmethod
from talon.utils import get_delimiter
from talon.signature.constants import (SIGNATURE_MAX_LINES,
                                       TOO_LONG_SIGNATURE_LINE,
                                       RE_SIGNATURE_CANDIDATE,
                                       RE_PHONE_SIGNATURE)

log = logging.getLogger(__name__)

# Defaults taken from bruteforce.py
DEFAULT_GREETINGS = (
    '[\s]*--*[\s]*[a-z \.]',
    'thanks[\s,!]',
    'regards[\s,!]',
    'cheers[\s,!]',
    'best[ a-z]*[\s,!]'
)


class AbstractExtractor(ABC):
    """
    Abstract base class for signature extractors.
    """

    @abstractmethod
    def extract_signature(self, message):
        """
        Extract the signature from message and return the text and signature

        :param message: str
        :return: (text: str, signature: str)
        """
        pass


class BruteForceExtractor(AbstractExtractor):
    """
    Brute force signature extractor.
    More flexible OO approach to
    talon.signatures.bruteforce.extract_signature
    """

    def __init__(self, max_lines=SIGNATURE_MAX_LINES, max_line_length=TOO_LONG_SIGNATURE_LINE,
                 greetings=DEFAULT_GREETINGS):
        """
        Create a new brute force extractor. Allows override max signature length, 
        max signature line length and common greetings (allows multi language support).
        """
        self.max_lines = max_lines
        self.max_line_length = max_line_length
        self._compile_greetings(greetings)

    def extract_signature(self, msg_body):
        """
        Use brute force to extract the signature (ie. regex and string matching)

        :param message: str
        :return: (text: str, signature: str)
        """
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
            candidate = self._get_signature_candidate(lines)
            candidate = delimiter.join(candidate)

            # try to extract signature
            signature = self.re_signature.search(candidate)
            if not signature:
                return (stripped_body.strip(), phone_signature)
            else:
                signature = signature.group()
                # when we splitlines() and then join them we can lose a new line at the end
                # we did it when identifying a candidate so we had to do it for stripped_body now
                stripped_body = delimiter.join(lines)
                stripped_body = stripped_body[:-len(signature)]

                if phone_signature:
                    signature = delimiter.join([signature, phone_signature])

                return (stripped_body.strip(),
                        signature.strip())
        except Exception:
            log.exception('ERROR extracting signature')
            return (msg_body, None)

    def _compile_greetings(self, greetings):
        """
        Init the regex to detect the
        greeting based on the passed
        greetings

        :param greetings:
        """
        greetings = ['^{}*$'.format(greeting) for greeting in greetings]
        greetings = '|'.join(greetings)
        self.re_signature = re.compile(r'((?:{}).*)'.format(greetings), re.I | re.X | re.M | re.S)

    def _get_signature_candidate(self, lines):
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
        candidate = candidate[-self.max_lines:]

        markers = self._mark_candidate_indexes(lines, candidate)
        candidate = self._process_marked_candidate_indexes(candidate, markers)

        # get actual lines for the candidate instead of indexes
        if candidate:
            candidate = lines[candidate[0]:]
            return candidate

        return []

    def _mark_candidate_indexes(self, lines, candidate):
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
            if len(lines[line_idx].strip()) > self.max_line_length:
                markers[i] = 'l'
            else:
                line = lines[line_idx].strip()
                if line.startswith('-') and line.strip("-"):
                    markers[i] = 'd'

        return "".join(markers)

    def _process_marked_candidate_indexes(self, candidate, markers):
        """
        Run regexes against candidate's marked indexes to strip signature candidate.

        >>> _process_marked_candidate_indexes([9, 12, 14, 15, 17], 'clddc')
        [15, 17]
        """
        match = RE_SIGNATURE_CANDIDATE.match(markers[::-1])
        return candidate[-match.end('candidate'):] if match else []
