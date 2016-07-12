from __future__ import absolute_import
from talon.quotations import register_xpath_extensions
try:
    from talon import signature
    ML_ENABLED = True
except ImportError:
    ML_ENABLED = False


def init():
    register_xpath_extensions()
    if ML_ENABLED:
        signature.initialize()
