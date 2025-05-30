STANDARD_REPLIES = "tests/fixtures/standard_replies"

with open("tests/fixtures/reply-quotations-share-block.eml", encoding="utf-8") as f:
    REPLY_QUOTATIONS_SHARE_BLOCK = f.read()

with open("tests/fixtures/OLK_SRC_BODY_SECTION.html", encoding="utf-8") as f:
    OLK_SRC_BODY_SECTION = f.read()

with open("tests/fixtures/reply-separated-by-hr.html", encoding="utf-8") as f:
    REPLY_SEPARATED_BY_HR = f.read()
