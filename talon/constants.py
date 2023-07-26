from __future__ import absolute_import
import regex as re
import os

PATTERNS = {
    'DELIMITER': r'\r?\n',
    'SIGNATURE': r'''(
        (?:
            ^[\s]*--*[\s]*[a-z \.]*$
            |
            ^thanks[\s,!\.]*$
            |
            ^thanks*[\s]+you[\s,!\.]*$
            |
            ^regards[\s,!\.]*$
            |
            ^cheers[\s,!\.]*$
            |
            ^best[a-z\s,!\.]*$
            |
            ^sincerely[a-z,!\.]*$
        )
        .*
    )''',
    'FOOTER_WORDS': r'''(
        (?:
            privileged
            |
            confidential
            |
            intended[\s]+recipient
            |
            all\s+rights\s+reserved
            |
            copyright
            |
            consent
            |
            registered
            |
            privacy
            |
            unsubscribe
            |
            disclose
            |
            disclosure
            |
            received[\w\s]+error
            |
            electronic\s+mail
            |
            information
            |
            emails*
            |
            policy
            |
            preferences
            |
            delivery
            |
            receive
            |
            secure
            |
            edelivery
        )
        .*
    )''',
    'PHONE_SIGNATURE': r'''(
        (?:
            ^sent[ ]{1}from[ ]{1}my[\s,!\w]*$
            |
            ^sent[ ]from[ ]Mailbox[ ]for[ ]iPhone.*$
            |
            ^sent[ ]from[ ]a[ ]phone.*$
            |
            ^sent[ ]([\S]*[ ])?from[ ]my[ ]BlackBerry.*$
            |
            ^Enviado[ ]desde[ ]mi[ ]([\S]+[ ]){0,2}BlackBerry.*$
        )
        .*
    )''',
    'EMAIL': '\S@\S',
    'RELAX_PHONE': '(\(? ?[\d]{2,3} ?\)?.{,3}?){2,}',
    'URL': r"""https?://|www\.[\S]+\.[\S]""",
    # Taken from:
    # http://www.cs.cmu.edu/~vitor/papers/sigFilePaper_finalversion.pdf
    # Line matches the regular expression "^[\s]*---*[\s]*$".
    'SEPARATOR': '^[\s]*---*[\s]*$',
    # Taken from:
    # http://www.cs.cmu.edu/~vitor/papers/sigFilePaper_finalversion.pdf
    # Line has a sequence of 10 or more special characters.
    'SPECIAL_CHARS': '^[\s]*([\*]|#|[\+]|[\^]|-|[\~]|[\&]|[\$]|_|[\!]|[\/]|[\%]|[\:]|[\=]){10,}[\s]*$',
    'SIGNATURE_WORDS': '(T|t)hank.*[,\.!]?|(B|b)est[,\.]?|(R|r)egards[,\.!]?|^(C|c)heers[,\.!]?|^sent[ ]{1}from[ ]{1}my[\s,!\w]*$|BR|^(S|s)incerely[,\.]?|(C|c)orporation|Group',
    'FOOTER_WORDS': '(P|p)rivileged|(C|c)onfidential|(I|i)ntended[\s]+recipient|(A|a)ll[ ](R|r)ights[ ](R|r)eserved|(C|c)opyright|(C|c)onsent|(R|r)egistered|(P|p)rivacy|(U|u)nsubscribe|(D|d)isclose|(D|d)isclosure|(R|r)eceived[\w\s]+error|(E|e)lectronic[\s]+mail|(I|i)nformation|(E|e)mail|(P|p)olicy|(D|d)elivery|(R|r)eceive|(E|e)delivery|(S|s)ecure|^sent[ ]{1}from[ ]{1}my[\s,!\w]*$|^sent[ ]from[ ]Mailbox[ ]for[ ]iPhone.*$|^sent[ ]from[ ]a[ ]phone.*$|^sent[ ]([\S]*[ ])?from[ ]my[ ]BlackBerry.*$|^Enviado[ ]desde[ ]mi[ ]([\S]+[ ]){0,2}BlackBerry.*$',
    # Taken from:
    # http://www.cs.cmu.edu/~vitor/papers/sigFilePaper_finalversion.pdf
    # Line contains a pattern like Vitor R. Carvalho or William W. Cohen.
    'RE_NAME': '[A-Z][a-z]+\s\s?[A-Z][\.]?\s\s?[A-Z][a-z]+',
    'INVALID_WORD_START': '\(|\+|[\d]'
}

FILTERS = {
    'TOO_LONG_SIGNATURE_LINE' : int(os.environ.get('TALON_TOO_LONG_SIGNATURE_LINE', 60)),
    'SIGNATURE_MAX_LINES': int(os.environ.get('TALON_SIGNATURE_MAX_LINES', 15)),
    'SIGNATURE_LINE_MAX_CHARS': int(os.environ.get('TALON_SIGNATURE_LINE_MAX_CHARS', 40)),
    'BAD_SENDER_NAMES': [
        # known mail domains
        'hotmail', 'gmail', 'yandex', 'mail', 'yahoo', 'mailgun', 'mailgunhq',
        'example',
        # first level domains
        'com', 'org', 'net', 'ru',
        # bad words
        'mailto'
    ],
}

def add_pattern(pattern_name):

    return

def apply_pattern(pattern_name):

    return

def get_pattern(pattern_name):

    return

def add_filter(filer_name):

    return

def apply_filter(filter_name):

    return

def get_filter(filter_name):

    return
