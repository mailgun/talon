# -*- coding: utf-8 -*-

"""
The module's functions operate on message bodies trying to extract
original messages (without quoted messages)
"""

import regex as re
import logging
from copy import deepcopy

from lxml import html, etree

from talon.utils import get_delimiter, html_to_text
from talon import html_quotations


log = logging.getLogger(__name__)


RE_FWD = re.compile("^[-]+[ ]*Forwarded message[ ]*[-]+$", re.I | re.M)

RE_ON_DATE_SMB_WROTE = re.compile(
    u'(-*[>]?[ ]?({0})[ ].*({1})(.*\n){{0,2}}.*({2}):?-*)'.format(
        # Beginning of the line
        u'|'.join((
            # English
            'On',
            # French
            'Le',
            # Polish
            'W dniu',
            # Dutch
            'Op',
            # German
            'Am',
            # Norwegian
            u'På',
            # Swedish, Danish
            'Den',
        )),
        # Date and sender separator
        u'|'.join((
            # most languages separate date and sender address by comma
            ',',
            # polish date and sender address separator
            u'użytkownik'
        )),
        # Ending of the line
        u'|'.join((
            # English
            'wrote', 'sent',
            # French
            u'a écrit',
            # Polish
            u'napisał',
            # Dutch
            'schreef','verzond','geschreven',
            # German
            'schrieb',
            # Norwegian, Swedish
            'skrev',
        ))
    ))
# Special case for languages where text is translated like this: 'on {date} wrote {somebody}:'
RE_ON_DATE_WROTE_SMB = re.compile(
    u'(-*[>]?[ ]?({0})[ ].*(.*\n){{0,2}}.*({1})[ ]*.*:)'.format(
        # Beginning of the line
        u'|'.join((
        	'Op',
        	#German
        	'Am'
        )),
        # Ending of the line
        u'|'.join((
            # Dutch
            'schreef','verzond','geschreven',
            # German
            'schrieb'
        ))
    )
    )

RE_QUOTATION = re.compile(
    r'''
    (
        # quotation border: splitter line or a number of quotation marker lines
        (?:
            s
            |
            (?:me*){2,}
        )

        # quotation lines could be marked as splitter or text, etc.
        .*

        # but we expect it to end with a quotation marker line
        me*
    )

    # after quotations should be text only or nothing at all
    [te]*$
    ''', re.VERBOSE)

RE_EMPTY_QUOTATION = re.compile(
    r'''
    (
        # quotation border: splitter line or a number of quotation marker lines
        (?:
            (?:se*)+
            |
            (?:me*){2,}
        )
    )
    e*
    ''', re.VERBOSE)

# ------Original Message------ or ---- Reply Message ----
# With variations in other languages.
RE_ORIGINAL_MESSAGE = re.compile(u'[\s]*[-]+[ ]*({})[ ]*[-]+'.format(
    u'|'.join((
        # English
        'Original Message', 'Reply Message',
        # German
        u'Ursprüngliche Nachricht', 'Antwort Nachricht',
        # Danish
        'Oprindelig meddelelse',
    ))), re.I)

RE_FROM_COLON_OR_DATE_COLON = re.compile(u'(_+\r?\n)?[\s]*(:?[*]?{})[\s]?:[*]? .*'.format(
    u'|'.join((
        # "From" in different languages.
        'From', 'Van', 'De', 'Von', 'Fra', u'Från',
        # "Date" in different languages.
        'Date', 'Datum', u'Envoyé', 'Skickat', 'Sendt',
    ))), re.I)

SPLITTER_PATTERNS = [
    RE_ORIGINAL_MESSAGE,
    RE_ON_DATE_SMB_WROTE,
    RE_ON_DATE_WROTE_SMB,
    RE_FROM_COLON_OR_DATE_COLON,
    # 02.04.2012 14:20 пользователь "bob@example.com" <
    # bob@xxx.mailgun.org> написал:
    re.compile("(\d+/\d+/\d+|\d+\.\d+\.\d+).*@", re.S),
    # 2014-10-17 11:28 GMT+03:00 Bob <
    # bob@example.com>:
    re.compile("\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+GMT.*@", re.S),
    # Thu, 26 Jun 2014 14:00:51 +0400 Bob <bob@example.com>:
    re.compile('\S{3,10}, \d\d? \S{3,10} 20\d\d,? \d\d?:\d\d(:\d\d)?'
               '( \S+){3,6}@\S+:'),
    # Sent from Samsung MobileName <address@example.com> wrote:
    re.compile('Sent from Samsung .*@.*> wrote')
    ]


RE_LINK = re.compile('<(http://[^>]*)>')
RE_NORMALIZED_LINK = re.compile('@@(http://[^>@]*)@@')

RE_PARENTHESIS_LINK = re.compile("\(https?://")

SPLITTER_MAX_LINES = 4
MAX_LINES_COUNT = 1000

QUOT_PATTERN = re.compile('^>+ ?')
NO_QUOT_LINE = re.compile('^[^>].*[\S].*')


def extract_from(msg_body, content_type='text/plain'):
    try:
        if content_type == 'text/plain':
            return extract_from_plain(msg_body)
        elif content_type == 'text/html':
            return extract_from_html(msg_body)
    except Exception:
        log.exception('ERROR extracting message')

    return msg_body


def mark_message_lines(lines):
    """Mark message lines with markers to distinguish quotation lines.

    Markers:

    * e - empty line
    * m - line that starts with quotation marker '>'
    * s - splitter line
    * t - presumably lines from the last message in the conversation

    >>> mark_message_lines(['answer', 'From: foo@bar.com', '', '> question'])
    'tsem'
    """
    markers = bytearray(len(lines))
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            markers[i] = 'e'  # empty line
        elif QUOT_PATTERN.match(lines[i]):
            markers[i] = 'm'  # line with quotation marker
        elif RE_FWD.match(lines[i]):
            markers[i] = 'f'  # ---- Forwarded message ----
        else:
            # in case splitter is spread across several lines
            splitter = is_splitter('\n'.join(lines[i:i + SPLITTER_MAX_LINES]))

            if splitter:
                # append as many splitter markers as lines in splitter
                splitter_lines = splitter.group().splitlines()
                for j in xrange(len(splitter_lines)):
                    markers[i + j] = 's'

                # skip splitter lines
                i += len(splitter_lines) - 1
            else:
                # probably the line from the last message in the conversation
                markers[i] = 't'
        i += 1

    return markers


def process_marked_lines(lines, markers, return_flags=[False, -1, -1]):
    """Run regexes against message's marked lines to strip quotations.

    Return only last message lines.
    >>> mark_message_lines(['Hello', 'From: foo@bar.com', '', '> Hi', 'tsem'])
    ['Hello']

    Also returns return_flags.
    return_flags = [were_lines_deleted, first_deleted_line,
                    last_deleted_line]
    """
    # if there are no splitter there should be no markers
    if 's' not in markers and not re.search('(me*){3}', markers):
        markers = markers.replace('m', 't')

    if re.match('[te]*f', markers):
        return_flags[:] = [False, -1, -1]
        return lines

    # inlined reply
    # use lookbehind assertions to find overlapping entries e.g. for 'mtmtm'
    # both 't' entries should be found
    for inline_reply in re.finditer('(?<=m)e*((?:t+e*)+)m', markers):
        # long links could break sequence of quotation lines but they shouldn't
        # be considered an inline reply
        links = (
            RE_PARENTHESIS_LINK.search(lines[inline_reply.start() - 1]) or
            RE_PARENTHESIS_LINK.match(lines[inline_reply.start()].strip()))
        if not links:
            return_flags[:] = [False, -1, -1]
            return lines

    # cut out text lines coming after splitter if there are no markers there
    quotation = re.search('(se*)+((t|f)+e*)+', markers)
    if quotation:
        return_flags[:] = [True, quotation.start(), len(lines)]
        return lines[:quotation.start()]

    # handle the case with markers
    quotation = (RE_QUOTATION.search(markers) or
                 RE_EMPTY_QUOTATION.search(markers))

    if quotation:
        return_flags[:] = True, quotation.start(1), quotation.end(1)
        return lines[:quotation.start(1)] + lines[quotation.end(1):]

    return_flags[:] = [False, -1, -1]
    return lines


def preprocess(msg_body, delimiter, content_type='text/plain'):
    """Prepares msg_body for being stripped.

    Replaces link brackets so that they couldn't be taken for quotation marker.
    Splits line in two if splitter pattern preceded by some text on the same
    line (done only for 'On <date> <person> wrote:' pattern).
    """
    # normalize links i.e. replace '<', '>' wrapping the link with some symbols
    # so that '>' closing the link couldn't be mistakenly taken for quotation
    # marker.
    def link_wrapper(link):
        newline_index = msg_body[:link.start()].rfind("\n")
        if msg_body[newline_index + 1] == ">":
            return link.group()
        else:
            return "@@%s@@" % link.group(1)

    msg_body = re.sub(RE_LINK, link_wrapper, msg_body)

    def splitter_wrapper(splitter):
        """Wraps splitter with new line"""
        if splitter.start() and msg_body[splitter.start() - 1] != '\n':
            return '%s%s' % (delimiter, splitter.group())
        else:
            return splitter.group()

    if content_type == 'text/plain':
        msg_body = re.sub(RE_ON_DATE_SMB_WROTE, splitter_wrapper, msg_body)

    return msg_body


def postprocess(msg_body):
    """Make up for changes done at preprocessing message.

    Replace link brackets back to '<' and '>'.
    """
    return re.sub(RE_NORMALIZED_LINK, r'<\1>', msg_body).strip()


def extract_from_plain(msg_body):
    """Extracts a non quoted message from provided plain text."""
    stripped_text = msg_body

    delimiter = get_delimiter(msg_body)
    msg_body = preprocess(msg_body, delimiter)
    # don't process too long messages
    lines = msg_body.splitlines()[:MAX_LINES_COUNT]
    markers = mark_message_lines(lines)
    lines = process_marked_lines(lines, markers)

    # concatenate lines, change links back, strip and return
    msg_body = delimiter.join(lines)
    msg_body = postprocess(msg_body)
    return msg_body


def extract_from_html(msg_body):
    """
    Extract not quoted message from provided html message body
    using tags and plain text algorithm.

    Cut out the 'blockquote', 'gmail_quote' tags.
    Cut Microsoft quotations.

    Then use plain text algorithm to cut out splitter or
    leftover quotation.
    This works by adding checkpoint text to all html tags,
    then converting html to text,
    then extracting quotations from text,
    then checking deleted checkpoints,
    then deleting necessary tags.
    """
    if msg_body.strip() == '':
        return msg_body

    msg_body = msg_body.replace('\r\n', '').replace('\n', '')
    html_tree = html.document_fromstring(
        msg_body,
        parser=html.HTMLParser(encoding="utf-8")
    )
    cut_quotations = (html_quotations.cut_gmail_quote(html_tree) or
                      html_quotations.cut_zimbra_quote(html_tree) or
                      html_quotations.cut_blockquote(html_tree) or
                      html_quotations.cut_microsoft_quote(html_tree) or
                      html_quotations.cut_by_id(html_tree) or
                      html_quotations.cut_from_block(html_tree)
                      )
    html_tree_copy = deepcopy(html_tree)

    number_of_checkpoints = html_quotations.add_checkpoint(html_tree, 0)
    quotation_checkpoints = [False] * number_of_checkpoints
    msg_with_checkpoints = html.tostring(html_tree)
    plain_text = html_to_text(msg_with_checkpoints)
    plain_text = preprocess(plain_text, '\n', content_type='text/html')
    lines = plain_text.splitlines()

    # Don't process too long messages
    if len(lines) > MAX_LINES_COUNT:
        return msg_body

    # Collect checkpoints on each line
    line_checkpoints = [
        [int(i[4:-4])  # Only checkpoint number
         for i in re.findall(html_quotations.CHECKPOINT_PATTERN, line)]
        for line in lines]

    # Remove checkpoints
    lines = [re.sub(html_quotations.CHECKPOINT_PATTERN, '', line)
             for line in lines]

    # Use plain text quotation extracting algorithm
    markers = mark_message_lines(lines)
    return_flags = []
    process_marked_lines(lines, markers, return_flags)
    lines_were_deleted, first_deleted, last_deleted = return_flags
    if lines_were_deleted:
        #collect checkpoints from deleted lines
        for i in xrange(first_deleted, last_deleted):
            for checkpoint in line_checkpoints[i]:
                quotation_checkpoints[checkpoint] = True
    else:
        if cut_quotations:
            return html.tostring(html_tree_copy)
        else:
            return msg_body

    # Remove tags with quotation checkpoints
    html_quotations.delete_quotation_tags(
        html_tree_copy, 0, quotation_checkpoints
    )

    return html.tostring(html_tree_copy)


def is_splitter(line):
    '''
    Returns Matcher object if provided string is a splitter and
    None otherwise.
    '''
    for pattern in SPLITTER_PATTERNS:
        matcher = re.match(pattern, line)
        if matcher:
            return matcher


def text_content(context):
    '''XPath Extension function to return a node text content.'''
    return context.context_node.text_content().strip()


def tail(context):
    '''XPath Extension function to return a node tail text.'''
    return context.context_node.tail or ''


def register_xpath_extensions():
    ns = etree.FunctionNamespace("http://mailgun.net")
    ns.prefix = 'mg'
    ns['text_content'] = text_content
    ns['tail'] = tail
