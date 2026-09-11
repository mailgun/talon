from __future__ import absolute_import
import talon_core
try:
    from talon import signature
    ML_ENABLED = True
except ImportError:
    ML_ENABLED = False


def init():
    talon_core.init()
    if ML_ENABLED:
        signature.initialize()
