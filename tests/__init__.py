from __future__ import absolute_import
from nose.tools import *
from mock import *

import talon


EML_MSG_FILENAME = "tests/fixtures/standard_replies/yahoo.eml"
MSG_FILENAME_WITH_BODY_SUFFIX = ("tests/fixtures/signature/emails/P/"
                                 "johndoeexamplecom_body")
EMAILS_DIR = "tests/fixtures/signature/emails"
TMP_DIR = "tests/fixtures/signature/tmp"

STRIPPED = "tests/fixtures/signature/emails/stripped/"
UNICODE_MSG = ("tests/fixtures/signature/emails/P/"
               "unicode_msg")


talon.init()
