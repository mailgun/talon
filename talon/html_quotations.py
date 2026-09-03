"""
The module's functions operate on message bodies trying to extract original
messages (without quoted messages) from html
"""

from __future__ import absolute_import
import regex as re

from talon.utils import cssselect

CHECKPOINT_PREFIX = '#!%!'
CHECKPOINT_SUFFIX = '!%!#'
CHECKPOINT_PATTERN = re.compile(CHECKPOINT_PREFIX + r'\d+' + CHECKPOINT_SUFFIX)

# HTML quote indicators (tag ids)
QUOTE_IDS = ['OLK_SRC_BODY_SECTION']
RE_FWD = re.compile(r"^[-]+[ ]*Forwarded message[ ]*[-]+$", re.I | re.M)
# Leading "On ... wrote:" header inside a quote wrapper (Gmail, Yahoo, etc.).
RE_QUOTE_HEADER = re.compile(r"On\s.{0,500}wrote\s*:", re.I | re.S)
# Leftover greeting/name after removing a quote wrapper that actually wraps the body.
QUOTE_STUB_MAX_CHARS = 40


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


def _tree_text(element):
    """Return concatenated descendant text without mutating the tree."""
    return (element.xpath('string()') or '').strip()


def _gmail_quote_looks_like_quotation(quote):
    """True if the node looks like quoted history rather than the current body."""
    if cssselect('.gmail_attr', quote) or cssselect('blockquote.gmail_quote', quote):
        return True
    return bool(RE_QUOTE_HEADER.search(_tree_text(quote)))


def _yahoo_quote_looks_like_quotation(quote):
    """True if the node looks like quoted history rather than the current body."""
    return bool(RE_QUOTE_HEADER.search(_tree_text(quote)))


def _quote_is_forward(quote):
    """True if the quote starts with a forwarded-message header.

    Gmail puts the header in the wrapper's direct text. Yahoo puts it in a
    child, so also check the first non-empty descendant text node.
    """
    if quote.text is not None and RE_FWD.match(quote.text):
        return True
    for child in quote.iterdescendants():
        text = (child.text or '').strip()
        if text:
            return bool(RE_FWD.match(text))
    return False


def _should_preserve_quote(remaining_text, original_text, looks_like_quotation):
    """True if cutting the quote wrapper would leave almost no readable text.

    Mirrors cut_from_block's parent_div_is_all_content / _readable_text_empty:
    do not strip when the quote wrapper holds the message. Completely empty
    leftover is always preserved. A short leftover (greeting) is preserved
    only when the node does not look like a real quotation, so short replies
    to quoted threads are still stripped.
    """
    if not remaining_text:
        return True
    if looks_like_quotation or not original_text:
        return False
    return (
        len(remaining_text) <= QUOTE_STUB_MAX_CHARS
        and len(remaining_text) < 0.05 * len(original_text)
    )


def _cut_quote_node(html_message, quote, looks_like_quotation):
    """Remove quote unless it is a forward or cutting would empty the message."""
    if _quote_is_forward(quote):
        return False

    parent = quote.getparent()
    if parent is None:
        return False

    original_text = _tree_text(html_message)
    idx = parent.index(quote)
    parent.remove(quote)
    remaining_text = _tree_text(html_message)

    if _should_preserve_quote(remaining_text, original_text, looks_like_quotation):
        parent.insert(idx, quote)
        return False
    return True


def cut_gmail_quote(html_message):
    ''' Cuts the outermost block element with class gmail_quote.

    Does not cut if that would leave the message with almost no readable text.
    '''
    gmail_quote = cssselect('div.gmail_quote', html_message)
    if not gmail_quote:
        return False
    quote = gmail_quote[0]
    return _cut_quote_node(
        html_message, quote, _gmail_quote_looks_like_quotation(quote))


def cut_yahoo_quote(html_message):
    ''' Cuts the outermost block element with class yahoo_quoted.

    Does not cut if that would leave the message with almost no readable text.
    '''
    yahoo_quote = cssselect('div.yahoo_quoted', html_message)
    if not yahoo_quote:
        return False
    quote = yahoo_quote[0]
    return _cut_quote_node(
        html_message, quote, _yahoo_quote_looks_like_quotation(quote))


def cut_microsoft_quote(html_message):
    ''' Cuts splitter block and all following blocks. '''
    #use EXSLT extensions to have a regex match() function with lxml
    ns = {"re": "http://exslt.org/regular-expressions"}

    #general pattern: @style='border:none;border-top:solid <color> 1.0pt;padding:3.0pt 0<unit> 0<unit> 0<unit>'
    #outlook 2007, 2010 (international) <color=#B5C4DF> <unit=cm>
    #outlook 2007, 2010 (american)      <color=#B5C4DF> <unit=pt>
    #outlook 2013       (international) <color=#E1E1E1> <unit=cm>
    #outlook 2013       (american)      <color=#E1E1E1> <unit=pt>
    #also handles a variant with a space after the semicolon
    splitter = html_message.xpath(
        #outlook 2007, 2010, 2013 (international, american)
        "//div[@style[re:match(., 'border:none; ?border-top:solid #(E1E1E1|B5C4DF) 1.0pt; ?"
        "padding:3.0pt 0(in|cm) 0(in|cm) 0(in|cm)')]]|"
        #windows mail
        "//div[@style='padding-top: 5px; "
        "border-top-color: rgb(229, 229, 229); "
        "border-top-width: 1px; border-top-style: solid;']"
        , namespaces=ns
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
