"""
The module's functions operate on message bodies trying to extract original
messages (without quoted messages) from html
"""

from __future__ import absolute_import
import regex as re

from talon.utils import cssselect 

CHECKPOINT_PREFIX = '#!%!'
CHECKPOINT_SUFFIX = '!%!#'
CHECKPOINT_PATTERN = re.compile(CHECKPOINT_PREFIX + '\d+' + CHECKPOINT_SUFFIX)

# HTML quote indicators (tag ids)
QUOTE_IDS = ['OLK_SRC_BODY_SECTION']
RE_FWD = re.compile("^[-]+[ ]*Forwarded message[ ]*[-]+$", re.I | re.M)


def add_checkpoint(html_note, counter):
    """Recursively adds checkpoints to html tree.
    """
    if html_note.text:
        html_note.text = (html_note.text + CHECKPOINT_PREFIX +
                          str(counter) + CHECKPOINT_SUFFIX)
    else:
        html_note.text = (CHECKPOINT_PREFIX + str(counter) +
                          CHECKPOINT_SUFFIX)
    counter += 1

    for child in html_note.iterchildren():
        counter = add_checkpoint(child, counter)

    if html_note.tail:
        html_note.tail = (html_note.tail + CHECKPOINT_PREFIX +
                          str(counter) + CHECKPOINT_SUFFIX)
    else:
        html_note.tail = (CHECKPOINT_PREFIX + str(counter) +
                          CHECKPOINT_SUFFIX)
    counter += 1

    return counter


def delete_quotation_tags(html_note, counter, quotation_checkpoints):
    """Deletes tags with quotation checkpoints from html tree.
    """
    tag_in_quotation = True

    if quotation_checkpoints[counter]:
        html_note.text = ''
    else:
        tag_in_quotation = False
    counter += 1

    quotation_children = []  # Children tags which are in quotation.
    for child in html_note.iterchildren():
        counter, child_tag_in_quotation = delete_quotation_tags(
            child, counter,
            quotation_checkpoints
        )
        if child_tag_in_quotation:
            quotation_children.append(child)

    if quotation_checkpoints[counter]:
        html_note.tail = ''
    else:
        tag_in_quotation = False
    counter += 1

    if tag_in_quotation:
        return counter, tag_in_quotation
    else:
        # Remove quotation children.
        for child in quotation_children:
            html_note.remove(child)
        return counter, tag_in_quotation


def cut_gmail_quote(html_message):
    ''' Cuts the outermost block element with class gmail_quote. '''
    gmail_quote = cssselect('div.gmail_quote', html_message)
    if gmail_quote and (gmail_quote[0].text is None or not RE_FWD.match(gmail_quote[0].text)):
        gmail_quote[0].getparent().remove(gmail_quote[0])
        return True


def cut_microsoft_quote(html_message):
    ''' Cuts splitter block and all following blocks. '''
    splitter = html_message.xpath(
        #outlook 2007, 2010 (international)
        "//div[@style='border:none;border-top:solid #B5C4DF 1.0pt;"
        "padding:3.0pt 0cm 0cm 0cm']|"
        #outlook 2007, 2010 (american)
        "//div[@style='border:none;border-top:solid #B5C4DF 1.0pt;"
        "padding:3.0pt 0in 0in 0in']|"
        #windows mail
        "//div[@style='padding-top: 5px; "
        "border-top-color: rgb(229, 229, 229); "
        "border-top-width: 1px; border-top-style: solid;']"
    )

    if splitter:
        splitter = splitter[0]
        #outlook 2010
        if splitter == splitter.getparent().getchildren()[0]:
            splitter = splitter.getparent()
    else:
        #outlook 2003
        splitter = html_message.xpath(
            "//div"
            "/div[@class='MsoNormal' and @align='center' "
            "and @style='text-align:center']"
            "/font"
            "/span"
            "/hr[@size='3' and @width='100%' and @align='center' "
            "and @tabindex='-1']"
        )
        if len(splitter):
            splitter = splitter[0]
            splitter = splitter.getparent().getparent()
            splitter = splitter.getparent().getparent()

    if len(splitter):
        parent = splitter.getparent()
        after_splitter = splitter.getnext()
        while after_splitter is not None:
            parent.remove(after_splitter)
            after_splitter = splitter.getnext()
        parent.remove(splitter)
        return True

    return False


def cut_by_id(html_message):
    found = False
    for quote_id in QUOTE_IDS:
        quote = cssselect('#{}'.format(quote_id), html_message)
        if quote:
            found = True
            quote[0].getparent().remove(quote[0])
    return found


def cut_blockquote(html_message):
    ''' Cuts the last non-nested blockquote with wrapping elements.'''
    quote = html_message.xpath(
        '(.//blockquote)'
        '[not(@class="gmail_quote") and not(ancestor::blockquote)]'
        '[last()]')

    if quote:
        quote = quote[0]
        quote.getparent().remove(quote)
        return True


def cut_from_block(html_message):
    """Cuts div tag which wraps block starting with "From:"."""
    # handle the case when From: block is enclosed in some tag
    block = html_message.xpath(
        ("//*[starts-with(mg:text_content(), 'From:')]|"
         "//*[starts-with(mg:text_content(), 'Date:')]"))

    if block:
        block = block[-1]
        parent_div = None
        while block.getparent() is not None:
            if block.tag == 'div':
                parent_div = block
                break
            block = block.getparent()
        if parent_div is not None:
            maybe_body = parent_div.getparent()
            # In cases where removing this enclosing div will remove all
            # content, we should assume the quote is not enclosed in a tag.
            parent_div_is_all_content = (
                maybe_body is not None and maybe_body.tag == 'body' and
                len(maybe_body.getchildren()) == 1)

            if not parent_div_is_all_content:
                parent = block.getparent()
                next_sibling = block.getnext()

                # remove all tags after found From block
                # (From block and quoted message are in separate divs)
                while next_sibling is not None:
                    parent.remove(block)
                    block = next_sibling
                    next_sibling = block.getnext()

                # remove the last sibling (or the
                # From block if no siblings)
                if block is not None:
                    parent.remove(block)

                return True
        else:
            return False

    # handle the case when From: block goes right after e.g. <hr>
    # and not enclosed in some tag
    block = html_message.xpath(
        ("//*[starts-with(mg:tail(), 'From:')]|"
         "//*[starts-with(mg:tail(), 'Date:')]"))
    if block:
        block = block[0]

        if RE_FWD.match(block.getparent().text or ''):
            return False
        
        while(block.getnext() is not None):
            block.getparent().remove(block.getnext())
        block.getparent().remove(block)
        return True

def cut_zimbra_quote(html_message):
    zDivider = html_message.xpath('//hr[@data-marker="__DIVIDER__"]')
    if zDivider:
        zDivider[0].getparent().remove(zDivider[0])
        return True
