from __future__ import absolute_import
import os
from nose.tools import *
from mock import *

import talon


FIXTURES_DIR = os.path.dirname(__file__) + "/fixtures"
EML_MSG_FILENAME = FIXTURES_DIR + "/standard_replies/yahoo.eml"
MSG_FILENAME_WITH_BODY_SUFFIX = (FIXTURES_DIR + "/signature/emails/P/"
                                 "johndoeexamplecom_body")
EMAILS_DIR = FIXTURES_DIR + "/signature/emails"
TMP_DIR = FIXTURES_DIR + "/signature/tmp"

STRIPPED = FIXTURES_DIR + "/signature/emails/stripped/"
UNICODE_MSG = (FIXTURES_DIR + "/signature/emails/P/"
               "unicode_msg")


talon.init()
