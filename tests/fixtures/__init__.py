import pandas as pd

STANDARD_REPLIES = "tests/fixtures/standard_replies"

COMMON_SIGNATURE_WORDS_FILENAME = "tests/fixtures/signature/signature_words/common_signature_words.csv"
COMMON_SIGNATURE_WORDS = pd.read_csv(COMMON_SIGNATURE_WORDS_FILENAME, sep="\t")

with open("tests/fixtures/reply-quotations-share-block.eml") as f:
    REPLY_QUOTATIONS_SHARE_BLOCK = f.read()

with open("tests/fixtures/OLK_SRC_BODY_SECTION.html") as f:
    OLK_SRC_BODY_SECTION = f.read()

with open("tests/fixtures/reply-separated-by-hr.html") as f:
    REPLY_SEPARATED_BY_HR = f.read()

def write_common_signature_words(df):
    df.to_csv(COMMON_SIGNATURE_WORDS_FILENAME, index=False, sep="\t")



