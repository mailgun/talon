import glob

STANDARD_REPLIES = "tests/fixtures/standard_replies"

with open("tests/fixtures/reply-quotations-share-block.eml") as f:
    REPLY_QUOTATIONS_SHARE_BLOCK = f.read()

with open("tests/fixtures/OLK_SRC_BODY_SECTION.html") as f:
    OLK_SRC_BODY_SECTION = f.read()

with open("tests/fixtures/reply-separated-by-hr.html") as f:
    REPLY_SEPARATED_BY_HR = f.read()

with open("tests/fixtures/BIG_EMAIL.html") as f:
    BIG_EMAIL = f.read()

with open("tests/fixtures/missing_text.html") as f:
    MISSING_TEXT = f.read()

REAL_HTML = []

for htmlfile in glob.glob('tests/fixtures/real_data/*.html'):
    with open(htmlfile) as f:
        REAL_HTML.append(f.read())
