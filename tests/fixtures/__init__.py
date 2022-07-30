import os

FIXTURES_DIR = os.path.dirname(__file__)
STANDARD_REPLIES = FIXTURES_DIR + "/standard_replies"

with open(FIXTURES_DIR + "/reply-quotations-share-block.eml") as f:
    REPLY_QUOTATIONS_SHARE_BLOCK = f.read()

with open(FIXTURES_DIR + "/OLK_SRC_BODY_SECTION.html") as f:
    OLK_SRC_BODY_SECTION = f.read()

with open(FIXTURES_DIR + "/reply-separated-by-hr.html") as f:
    REPLY_SEPARATED_BY_HR = f.read()
