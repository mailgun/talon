from __future__ import absolute_import

import pytest

import talon
from talon.signature.bruteforce import extract_signature


def test_bruteforce_works_without_ml_extra():
    text, signature = extract_signature("Wow. Awesome!\n--\nBob Smith")
    assert text == "Wow. Awesome!"
    assert signature == "--\nBob Smith"


def test_signature_package_imports_without_ml_extra():
    import talon.signature as signature

    assert signature.EXTRACTOR_FILENAME.endswith("classifier")
    assert signature.EXTRACTOR_DATA.endswith("train.data")


@pytest.mark.skipif(talon.ML_ENABLED, reason="only without talon[ml]")
def test_extract_requires_ml_extra():
    import talon.signature as signature

    with pytest.raises(ImportError, match=r"talon\[ml\]"):
        signature.extract


@pytest.mark.ml
def test_extract_is_exported_with_ml_extra():
    from talon.signature import extract

    assert callable(extract)
