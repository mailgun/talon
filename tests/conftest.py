import pytest


def _ml_available():
    try:
        import joblib  # noqa: F401
        import numpy  # noqa: F401
        import sklearn  # noqa: F401
        return True
    except ImportError:
        return False


ML_AVAILABLE = _ml_available()


def pytest_collection_modifyitems(config, items):
    if ML_AVAILABLE:
        return
    skip_ml = pytest.mark.skip(reason="requires talon[ml] extra")
    for item in items:
        if item.get_closest_marker("ml"):
            item.add_marker(skip_ml)
