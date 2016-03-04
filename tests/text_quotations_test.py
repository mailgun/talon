# -*- coding: utf-8 -*-

from . import *
from . fixtures import *

import os

import email.iterators
from talon import quotations


@patch.object(quotations, 'MAX_LINES_COUNT', 1)
def test_too_many_lines():
    msg_body = """Test reply
Hi
-----Original Message-----

Test"""
    eq_("Test reply", quotations.extract_from_plain(msg_body))


def test_pattern_on_date_somebody_wrote():
    msg_body = """Test reply

On 11-Apr-2011, at 6:54 PM, Roman Tkachenko <romant@example.com> wrote:

>
> Test
>
> Roman"""

    eq_("Test reply", quotations.extract_from_plain(msg_body))


def test_pattern_sent_from_samsung_smb_wrote():
    msg_body = """Test reply

Sent from Samsung MobileName <address@example.com> wrote:

>
> Test
>
> Roman"""

    eq_("Test reply", quotations.extract_from_plain(msg_body))


def test_pattern_on_date_wrote_somebody():
    eq_('Lorem', quotations.extract_from_plain(
    """Lorem

Op 13-02-2014 3:18 schreef Julius Caesar <pantheon@rome.com>:
    
Veniam laborum mlkshk kale chips authentic. Normcore mumblecore laboris, fanny pack readymade eu blog chia pop-up freegan enim master cleanse.
"""))


def test_pattern_on_date_somebody_wrote_date_with_slashes():
    msg_body = """Test reply

On 04/19/2011 07:10 AM, Roman Tkachenko wrote:

>
> Test.
>
> Roman"""
    eq_("Test reply", quotations.extract_from_plain(msg_body))


def test_date_time_email_splitter():
    msg_body = """Test reply

2014-10-17 11:28 GMT+03:00 Postmaster <
postmaster@sandboxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.mailgun.org>:

> First from site
>
    """
    eq_("Test reply", quotations.extract_from_plain(msg_body))


def test_pattern_on_date_somebody_wrote_allows_space_in_front():
    msg_body = """Thanks Thanmai
 On Mar 8, 2012 9:59 AM, "Example.com" <
r+7f1b094ceb90e18cca93d53d3703feae@example.com> wrote:


>**
>  Blah-blah-blah"""
    eq_("Thanks Thanmai", quotations.extract_from_plain(msg_body))


def test_pattern_on_date_somebody_sent():
    msg_body = """Test reply

On 11-Apr-2011, at 6:54 PM, Roman Tkachenko <romant@example.com> sent:

>
> Test
>
> Roman"""
    eq_("Test reply", quotations.extract_from_plain(msg_body))


def test_line_starts_with_on():
    msg_body = """Blah-blah-blah
On blah-blah-blah"""
    eq_(msg_body, quotations.extract_from_plain(msg_body))


def test_reply_and_quotation_splitter_share_line():
    # reply lines and 'On <date> <person> wrote:' splitter pattern
    # are on the same line
    msg_body = """reply On Wed, Apr 4, 2012 at 3:59 PM, bob@example.com wrote:
> Hi"""
    eq_('reply', quotations.extract_from_plain(msg_body))

    # test pattern '--- On <date> <person> wrote:' with reply text on
    # the same line
    msg_body = """reply--- On Wed, Apr 4, 2012 at 3:59 PM, me@domain.com wrote:
> Hi"""
    eq_('reply', quotations.extract_from_plain(msg_body))

    # test pattern '--- On <date> <person> wrote:' with reply text containing
    # '-' symbol
    msg_body = """reply
bla-bla - bla--- On Wed, Apr 4, 2012 at 3:59 PM, me@domain.com wrote:
> Hi"""
    reply = """reply
bla-bla - bla"""

    eq_(reply, quotations.extract_from_plain(msg_body))


def _check_pattern_original_message(original_message_indicator):
    msg_body = u"""Test reply

-----{}-----

Test"""
    eq_('Test reply', quotations.extract_from_plain(msg_body.format(unicode(original_message_indicator))))

def test_english_original_message():
    _check_pattern_original_message('Original Message')
    _check_pattern_original_message('Reply Message')

def test_german_original_message():
    _check_pattern_original_message(u'Ursprüngliche Nachricht')
    _check_pattern_original_message('Antwort Nachricht')

def test_danish_original_message():
    _check_pattern_original_message('Oprindelig meddelelse')


def test_reply_after_quotations():
    msg_body = """On 04/19/2011 07:10 AM, Roman Tkachenko wrote:

>
> Test
Test reply"""
    eq_("Test reply", quotations.extract_from_plain(msg_body))


def test_reply_wraps_quotations():
    msg_body = """Test reply

On 04/19/2011 07:10 AM, Roman Tkachenko wrote:

>
> Test

Regards, Roman"""

    reply = """Test reply

Regards, Roman"""

    eq_(reply, quotations.extract_from_plain(msg_body))


def test_reply_wraps_nested_quotations():
    msg_body = """Test reply
On 04/19/2011 07:10 AM, Roman Tkachenko wrote:

>Test test
>On 04/19/2011 07:10 AM, Roman Tkachenko wrote:
>
>>
>> Test.
>>
>> Roman

Regards, Roman"""

    reply = """Test reply
Regards, Roman"""
    eq_(reply, quotations.extract_from_plain(msg_body))


def test_quotation_separator_takes_2_lines():
    msg_body = """Test reply

On Fri, May 6, 2011 at 6:03 PM, Roman Tkachenko from Hacker News
<roman@definebox.com> wrote:

> Test.
>
> Roman

Regards, Roman"""

    reply = """Test reply

Regards, Roman"""
    eq_(reply, quotations.extract_from_plain(msg_body))


def test_quotation_separator_takes_3_lines():
    msg_body = """Test reply

On Nov 30, 2011, at 12:47 PM, Somebody <
416ffd3258d4d2fa4c85cfa4c44e1721d66e3e8f4@somebody.domain.com>
wrote:

Test message
"""
    eq_("Test reply", quotations.extract_from_plain(msg_body))


def test_short_quotation():
    msg_body = """Hi

On 04/19/2011 07:10 AM, Roman Tkachenko wrote:

> Hello"""
    eq_("Hi", quotations.extract_from_plain(msg_body))

def test_with_indent():
    msg_body = """YOLO salvia cillum kogi typewriter mumblecore cardigan skateboard Austin.

------On 12/29/1987 17:32 PM, Julius Caesar wrote-----

Brunch mumblecore pug Marfa tofu, irure taxidermy hoodie readymade pariatur. 
    """
    eq_("YOLO salvia cillum kogi typewriter mumblecore cardigan skateboard Austin.", quotations.extract_from_plain(msg_body))


def test_short_quotation_with_newline():
    msg_body = """Btw blah blah...

On Tue, Jan 27, 2015 at 12:42 PM -0800, "Company" <christine.XXX@XXX.com> wrote:

Hi Mark,
Blah blah? 
Thanks,Christine 

On Jan 27, 2015, at 11:55 AM, Mark XXX <mark@XXX.com> wrote:

Lorem ipsum?
Mark

Sent from Acompli"""
    eq_("Btw blah blah...", quotations.extract_from_plain(msg_body))


def test_pattern_date_email_with_unicode():
    msg_body = """Replying ok
2011/4/7 Nathan \xd0\xb8ova <support@example.com>

>  Cool beans, scro"""
    eq_("Replying ok", quotations.extract_from_plain(msg_body))


def test_english_from_block():
    eq_('Allo! Follow up MIME!', quotations.extract_from_plain("""Allo! Follow up MIME!

From: somebody@example.com
Sent: March-19-11 5:42 PM
To: Somebody
Subject: The manager has commented on your Loop

Blah-blah-blah
"""))

def test_german_from_block():
    eq_('Allo! Follow up MIME!', quotations.extract_from_plain(
    """Allo! Follow up MIME!

Von: somebody@example.com
Gesendet: Dienstag, 25. November 2014 14:59
An: Somebody
Betreff: The manager has commented on your Loop

Blah-blah-blah
"""))

def test_french_multiline_from_block():
    eq_('Lorem ipsum', quotations.extract_from_plain(
    u"""Lorem ipsum

De : Brendan xxx [mailto:brendan.xxx@xxx.com]
Envoyé : vendredi 23 janvier 2015 16:39
À : Camille XXX
Objet : Follow Up

Blah-blah-blah
"""))

def test_french_from_block():
    eq_('Lorem ipsum', quotations.extract_from_plain(
    u"""Lorem ipsum

Le 23 janv. 2015 à 22:03, Brendan xxx <brendan.xxx@xxx.com<mailto:brendan.xxx@xxx.com>> a écrit:

Bonjour!"""))

def test_polish_from_block():
    eq_('Lorem ipsum', quotations.extract_from_plain(
    u"""Lorem ipsum

W dniu 28 stycznia 2015 01:53 użytkownik Zoe xxx <zoe.xxx@xxx.com>
napisał:

Blah!
"""))

def test_danish_from_block():
    eq_('Allo! Follow up MIME!', quotations.extract_from_plain(
    """Allo! Follow up MIME!

Fra: somebody@example.com
Sendt: 19. march 2011 12:10
Til: Somebody
Emne: The manager has commented on your Loop

Blah-blah-blah
"""))

def test_swedish_from_block():
    eq_('Allo! Follow up MIME!', quotations.extract_from_plain(
    u"""Allo! Follow up MIME!
Från: Anno Sportel [mailto:anno.spoel@hsbcssad.com]
Skickat: den 26 augusti 2015 14:45
Till: Isacson Leiff
Ämne: RE: Week 36

Blah-blah-blah
"""))

def test_swedish_from_line():
    eq_('Lorem', quotations.extract_from_plain(
    """Lorem
Den 14 september, 2015 02:23:18, Valentino Rudy (valentino@rudy.be) skrev:

Veniam laborum mlkshk kale chips authentic. Normcore mumblecore laboris, fanny pack readymade eu blog chia pop-up freegan enim master cleanse.
"""))

def test_norwegian_from_line():
    eq_('Lorem', quotations.extract_from_plain(
    u"""Lorem
På 14 september 2015 på 02:23:18, Valentino Rudy (valentino@rudy.be) skrev:

Veniam laborum mlkshk kale chips authentic. Normcore mumblecore laboris, fanny pack readymade eu blog chia pop-up freegan enim master cleanse.
"""))

def test_dutch_from_block():
    eq_('Gluten-free culpa lo-fi et nesciunt nostrud.', quotations.extract_from_plain(
    """Gluten-free culpa lo-fi et nesciunt nostrud. 

Op 17-feb.-2015, om 13:18 heeft Julius Caesar <pantheon@rome.com> het volgende geschreven:
    
Small batch beard laboris tempor, non listicle hella Tumblr heirloom. 
"""))


def test_quotation_marker_false_positive():
    msg_body = """Visit us now for assistance...
>>> >>>  http://www.domain.com <<<
Visit our site by clicking the link above"""
    eq_(msg_body, quotations.extract_from_plain(msg_body))


def test_link_closed_with_quotation_marker_on_new_line():
    msg_body = '''8.45am-1pm

From: somebody@example.com

<http://email.example.com/c/dHJhY2tpbmdfY29kZT1mMDdjYzBmNzM1ZjYzMGIxNT
>  <bob@example.com <mailto:bob@example.com> >

Requester: '''
    eq_('8.45am-1pm', quotations.extract_from_plain(msg_body))


def test_link_breaks_quotation_markers_sequence():
    # link starts and ends on the same line
    msg_body = """Blah

On Thursday, October 25, 2012 at 3:03 PM, life is short. on Bob wrote:

>
> Post a response by replying to this email
>
 (http://example.com/c/YzOTYzMmE) >
> life is short. (http://example.com/c/YzMmE)
>
"""
    eq_("Blah", quotations.extract_from_plain(msg_body))

    # link starts after some text on one line and ends on another
    msg_body = """Blah

On Monday, 24 September, 2012 at 3:46 PM, bob wrote:

> [Ticket #50] test from bob
>
> View ticket (http://example.com/action
_nonce=3dd518)
>
"""
    eq_("Blah", quotations.extract_from_plain(msg_body))


def test_from_block_starts_with_date():
    msg_body = """Blah

Date: Wed, 16 May 2012 00:15:02 -0600
To: klizhentas@example.com"""
    eq_('Blah', quotations.extract_from_plain(msg_body))


def test_bold_from_block():
    msg_body = """Hi

  *From:* bob@example.com [mailto:
  bob@example.com]
  *Sent:* Wednesday, June 27, 2012 3:05 PM
  *To:* travis@example.com
  *Subject:* Hello

"""
    eq_("Hi", quotations.extract_from_plain(msg_body))


def test_weird_date_format_in_date_block():
    msg_body = """Blah
Date: Fri=2C 28 Sep 2012 10:55:48 +0000
From: tickets@example.com
To: bob@example.com
Subject: [Ticket #8] Test

"""
    eq_('Blah', quotations.extract_from_plain(msg_body))


def test_dont_parse_quotations_for_forwarded_messages():
    msg_body = """FYI

---------- Forwarded message ----------
From: bob@example.com
Date: Tue, Sep 4, 2012 at 1:35 PM
Subject: Two
line subject
To: rob@example.com

Text"""
    eq_(msg_body, quotations.extract_from_plain(msg_body))


def test_forwarded_message_in_quotations():
    msg_body = """Blah

-----Original Message-----

FYI

---------- Forwarded message ----------
From: bob@example.com
Date: Tue, Sep 4, 2012 at 1:35 PM
Subject: Two
line subject
To: rob@example.com

"""
    eq_("Blah", quotations.extract_from_plain(msg_body))


def test_mark_message_lines():
    # e - empty line
    # s - splitter line
    # m - line starting with quotation marker '>'
    # t - the rest

    lines = ['Hello', '',
             # next line should be marked as splitter
             '_____________',
             'From: foo@bar.com',
             '',
             '> Hi',
             '',
             'Signature']
    eq_('tessemet', quotations.mark_message_lines(lines))

    lines = ['Just testing the email reply',
             '',
             'Robert J Samson',
             'Sent from my iPhone',
             '',
             # all 3 next lines should be marked as splitters
             'On Nov 30, 2011, at 12:47 PM, Skapture <',
             ('416ffd3258d4d2fa4c85cfa4c44e1721d66e3e8f4'
              '@skapture-staging.mailgun.org>'),
             'wrote:',
             '',
             'Tarmo Lehtpuu has posted the following message on']
    eq_('tettessset', quotations.mark_message_lines(lines))


def test_process_marked_lines():
    # quotations and last message lines are mixed
    # consider all to be a last message
    markers = 'tsemmtetm'
    lines = [str(i) for i in range(len(markers))]
    lines = [str(i) for i in range(len(markers))]

    eq_(lines, quotations.process_marked_lines(lines, markers))

    # no splitter => no markers
    markers = 'tmm'
    lines = ['1', '2', '3']
    eq_(['1', '2', '3'], quotations.process_marked_lines(lines, markers))

    # text after splitter without markers is quotation
    markers = 'tst'
    lines = ['1', '2', '3']
    eq_(['1'], quotations.process_marked_lines(lines, markers))

    # message + quotation + signature
    markers = 'tsmt'
    lines = ['1', '2', '3', '4']
    eq_(['1', '4'], quotations.process_marked_lines(lines, markers))

    # message + <quotation without markers> + nested quotation
    markers = 'tstsmt'
    lines = ['1', '2', '3', '4', '5', '6']
    eq_(['1'], quotations.process_marked_lines(lines, markers))

    # test links wrapped with paranthesis
    # link starts on the marker line
    markers = 'tsmttem'
    lines = ['text',
             'splitter',
             '>View (http://example.com',
             '/abc',
             ')',
             '',
             '> quote']
    eq_(lines[:1], quotations.process_marked_lines(lines, markers))

    # link starts on the new line
    markers = 'tmmmtm'
    lines = ['text',
             '>'
             '>',
             '>',
             '(http://example.com) >  ',
             '> life is short. (http://example.com)  '
             ]
    eq_(lines[:1], quotations.process_marked_lines(lines, markers))

    # check all "inline" replies
    markers = 'tsmtmtm'
    lines = ['text',
             'splitter',
             '>',
             '(http://example.com)',
             '>',
             'inline  reply',
             '>']
    eq_(lines, quotations.process_marked_lines(lines, markers))

    # inline reply with link not wrapped in paranthesis
    markers = 'tsmtm'
    lines = ['text',
             'splitter',
             '>',
             'inline reply with link http://example.com',
             '>']
    eq_(lines, quotations.process_marked_lines(lines, markers))

    # inline reply with link wrapped in paranthesis
    markers = 'tsmtm'
    lines = ['text',
             'splitter',
             '>',
             'inline  reply (http://example.com)',
             '>']
    eq_(lines, quotations.process_marked_lines(lines, markers))


def test_preprocess():
    msg = ('Hello\n'
           'See <http://google.com\n'
           '> for more\n'
           'information On Nov 30, 2011, at 12:47 PM, Somebody <\n'
           '416ffd3258d4d2fa4c85cfa4c44e1721d66e3e8f4\n'
           '@example.com>'
           'wrote:\n'
           '\n'
           '> Hi')

    # test the link is rewritten
    # 'On <date> <person> wrote:' pattern starts from a new line
    prepared_msg = ('Hello\n'
                    'See @@http://google.com\n'
                    '@@ for more\n'
                    'information\n'
                    ' On Nov 30, 2011, at 12:47 PM, Somebody <\n'
                    '416ffd3258d4d2fa4c85cfa4c44e1721d66e3e8f4\n'
                    '@example.com>'
                    'wrote:\n'
                    '\n'
                    '> Hi')
    eq_(prepared_msg, quotations.preprocess(msg, '\n'))

    msg = """
> <http://teemcl.mailgun.org/u/**aD1mZmZiNGU5ODQwMDNkZWZlMTExNm**

> MxNjQ4Y2RmOTNlMCZyPXNlcmdleS5v**YnlraG92JTQwbWFpbGd1bmhxLmNvbS**

> Z0PSUyQSZkPWUwY2U<http://example.org/u/aD1mZmZiNGU5ODQwMDNkZWZlMTExNmMxNjQ4Y>
    """
    eq_(msg, quotations.preprocess(msg, '\n'))

    # 'On <date> <person> wrote' shouldn't be spread across too many lines
    msg = ('Hello\n'
           'How are you? On Nov 30, 2011, at 12:47 PM,\n '
           'Example <\n'
           '416ffd3258d4d2fa4c85cfa4c44e1721d66e3e8f4\n'
           '@example.org>'
           'wrote:\n'
           '\n'
           '> Hi')
    eq_(msg, quotations.preprocess(msg, '\n'))

    msg = ('Hello On Nov 30, smb wrote:\n'
           'Hi\n'
           'On Nov 29, smb wrote:\n'
           'hi')

    prepared_msg = ('Hello\n'
                    ' On Nov 30, smb wrote:\n'
                    'Hi\n'
                    'On Nov 29, smb wrote:\n'
                    'hi')

    eq_(prepared_msg, quotations.preprocess(msg, '\n'))


def test_preprocess_postprocess_2_links():
    msg_body = "<http://link1> <http://link2>"
    eq_(msg_body, quotations.extract_from_plain(msg_body))


def test_standard_replies():
    for filename in os.listdir(STANDARD_REPLIES):
        filename = os.path.join(STANDARD_REPLIES, filename)
        if not filename.endswith('.eml') or os.path.isdir(filename):
            continue
        with open(filename) as f:
            message = email.message_from_file(f)
            body = email.iterators.typed_subpart_iterator(message, subtype='plain').next()
            text = ''.join(email.iterators.body_line_iterator(body, True))

            stripped_text = quotations.extract_from_plain(text)
            reply_text_fn = filename[:-4] + '_reply_text'
            if os.path.isfile(reply_text_fn):
                with open(reply_text_fn) as f:
                    reply_text = f.read().strip()
            else:
                reply_text = 'Hello'
            yield eq_, reply_text, stripped_text, \
                "'%(reply)s' != %(stripped)s for %(fn)s" % \
                {'reply': reply_text, 'stripped': stripped_text,
                 'fn': filename}
