# -*- coding: utf-8 -*-

""" The module provides:
* functions used when evaluating signature's features
* regexp's constants used when evaluating signature's features

"""

import unicodedata
import regex as re

from talon.utils import to_unicode

from talon.signature.constants import SIGNATURE_MAX_LINES


rc = re.compile

RE_EMAIL = rc('\S@\S')
RE_RELAX_PHONE = rc('(\(? ?[\d]{2,3} ?\)?.{,3}?){2,}')
RE_URL = rc(r'''https?://|www\.[\S]+\.[\S]''')

# Taken from:
# http://www.cs.cmu.edu/~vitor/papers/sigFilePaper_finalversion.pdf
# Line matches the regular expression "^[\s]*---*[\s]*$".
RE_SEPARATOR = rc('^[\s]*---*[\s]*$')

# Taken from:
# http://www.cs.cmu.edu/~vitor/papers/sigFilePaper_finalversion.pdf
# Line has a sequence of 10 or more special characters.
RE_SPECIAL_CHARS = rc(('^[\s]*([\*]|#|[\+]|[\^]|-|[\~]|[\&]|[\$]|_|[\!]|'
                       '[\/]|[\%]|[\:]|[\=]){10,}[\s]*$'))

RE_SIGNATURE_WORDS = rc(('(T|t)hank.*,|(B|b)est|(R|r)egards|'
                         '^sent[ ]{1}from[ ]{1}my[\s,!\w]*$|BR|(S|s)incerely|'
                         '(C|c)orporation|Group'))

# Taken from:
# http://www.cs.cmu.edu/~vitor/papers/sigFilePaper_finalversion.pdf
# Line contains a pattern like Vitor R. Carvalho or William W. Cohen.
RE_NAME = rc('[A-Z][a-z]+\s\s?[A-Z][\.]?\s\s?[A-Z][a-z]+')

INVALID_WORD_START = rc('\(|\+|[\d]')

BAD_SENDER_NAMES = [
    # known mail domains
    'hotmail', 'gmail', 'yandex', 'mail', 'yahoo', 'mailgun', 'mailgunhq',
    'example',
    # first level domains
    'com', 'org', 'net', 'ru',
    # bad words
    'mailto'
    ]


def binary_regex_search(prog):
    '''Returns a function that returns 1 or 0 depending on regex search result.

    If regular expression compiled into prog is present in a string
    the result of calling the returned function with the string will be 1
    and 0 otherwise.

    >>> import regex as re
    >>> binary_regex_search(re.compile("12"))("12")
    1
    >>> binary_regex_search(re.compile("12"))("34")
    0
    '''
    return lambda s: 1 if prog.search(s) else 0


def binary_regex_match(prog):
    '''Returns a function that returns 1 or 0 depending on regex match result.

    If a string matches regular expression compiled into prog
    the result of calling the returned function with the string will be 1
    and 0 otherwise.

    >>> import regex as re
    >>> binary_regex_match(re.compile("12"))("12 3")
    1
    >>> binary_regex_match(re.compile("12"))("3 12")
    0
    '''
    return lambda s: 1 if prog.match(s) else 0


def flatten_list(list_to_flatten):
    """Simple list comprehension to flatten list.

    >>> flatten_list([[1, 2], [3, 4, 5]])
    [1, 2, 3, 4, 5]
    >>> flatten_list([[1], [[2]]])
    [1, [2]]
    >>> flatten_list([1, [2]])
    Traceback (most recent call last):
    ...
    TypeError: 'int' object is not iterable
    """
    return [e for sublist in list_to_flatten for e in sublist]


def contains_sender_names(sender):
    '''Returns a functions to search sender\'s name or it\'s part.

    >>> feature = contains_sender_names("Sergey N.  Obukhov <xxx@example.com>")
    >>> feature("Sergey Obukhov")
    1
    >>> feature("BR, Sergey N.")
    1
    >>> feature("Sergey")
    1
    >>> contains_sender_names("<serobnic@mail.ru>")("Serobnic")
    1
    >>> contains_sender_names("<serobnic@mail.ru>")("serobnic")
    1
    '''
    names = '( |$)|'.join(flatten_list([[e, e.capitalize()]
                                        for e in extract_names(sender)]))
    names = names or sender
    if names != '':
        return binary_regex_search(re.compile(names))
    return lambda s: 0


def extract_names(sender):
    """Tries to extract sender's names from `From:` header.

    It could extract not only the actual names but e.g.
    the name of the company, parts of email, etc.

    >>> extract_names('Sergey N.  Obukhov <serobnic@mail.ru>')
    ['Sergey', 'Obukhov', 'serobnic']
    >>> extract_names('')
    []
    """
    sender = to_unicode(sender, precise=True)
    # Remove non-alphabetical characters
    sender = "".join([char if char.isalpha() else ' ' for char in sender])
    # Remove too short words and words from "black" list i.e.
    # words like `ru`, `gmail`, `com`, `org`, etc.
    sender = [word for word in sender.split() if len(word) > 1 and
              not word in BAD_SENDER_NAMES]
    # Remove duplicates
    names = list(set(sender))
    return names


def categories_percent(s, categories):
    '''Returns category characters percent.

    >>> categories_percent("qqq ggg hhh", ["Po"])
    0.0
    >>> categories_percent("q,w.", ["Po"])
    50.0
    >>> categories_percent("qqq ggg hhh", ["Nd"])
    0.0
    >>> categories_percent("q5", ["Nd"])
    50.0
    >>> categories_percent("s.s,5s", ["Po", "Nd"])
    50.0
    '''
    count = 0
    s = to_unicode(s, precise=True)
    for c in s:
        if unicodedata.category(c) in categories:
            count += 1
    return 100 * float(count) / len(s) if len(s) else 0


def punctuation_percent(s):
    '''Returns punctuation percent.

    >>> punctuation_percent("qqq ggg hhh")
    0.0
    >>> punctuation_percent("q,w.")
    50.0
    '''
    return categories_percent(s, ['Po'])


def capitalized_words_percent(s):
    '''Returns capitalized words percent.'''
    s = to_unicode(s, precise=True)
    words = re.split('\s', s)
    words = [w for w in words if w.strip()]
    capitalized_words_counter = 0
    valid_words_counter = 0
    for word in words:
        if not INVALID_WORD_START.match(word):
            valid_words_counter += 1
            if word[0].isupper():
                capitalized_words_counter += 1
    if valid_words_counter > 0 and len(words) > 1:
        return 100 * float(capitalized_words_counter) / valid_words_counter

    return 0


def many_capitalized_words(s):
    """Returns a function to check percentage of capitalized words.

    The function returns 1 if percentage greater then 65% and 0 otherwise.
    """
    return 1 if capitalized_words_percent(s) > 66 else 0


def has_signature(body, sender):
    '''Checks if the body has signature. Returns True or False.'''
    non_empty = [line for line in body.splitlines() if line.strip()]
    candidate = non_empty[-SIGNATURE_MAX_LINES:]
    upvotes = 0
    for line in candidate:
        # we check lines for sender's name, phone, email and url,
        # those signature lines don't take more then 27 lines
        if len(line.strip()) > 27:
            continue
        elif contains_sender_names(sender)(line):
            return True
        elif (binary_regex_search(RE_RELAX_PHONE)(line) +
              binary_regex_search(RE_EMAIL)(line) +
              binary_regex_search(RE_URL)(line) == 1):
            upvotes += 1
    if upvotes > 1:
        return True
