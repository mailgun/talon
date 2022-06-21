from __future__ import absolute_import
import regex as re


RE_DELIMITER = re.compile('\r?\n')

# One of the regular expressions has horrible performance
# on strings with very long lines, so any email with a line
# longer than this will simply skip a step or two in processing.
MAX_LINE_LENGTH_FOR_REGEX_SUB = 32768
