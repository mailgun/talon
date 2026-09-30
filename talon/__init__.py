from __future__ import absolute_import
from talon.quotations import register_xpath_extensions


def _ml_available() -> bool:
    try:
        import joblib  # noqa: F401
        import numpy  # noqa: F401
        import sklearn  # noqa: F401
        return True
    except ImportError:
        return False


ML_ENABLED = _ml_available()


def init() -> None:
    register_xpath_extensions()
    if ML_ENABLED:
        from talon import signature
        signature.initialize()
