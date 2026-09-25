from __future__ import absolute_import, annotations

import pytest

import talon
from talon.signature.bruteforce import extract_signature


def test_bruteforce_works_without_ml_extra() -> None:
    text, signature = extract_signature("Wow. Awesome!\n--\nBob Smith")
    assert text == "Wow. Awesome!"
    assert signature == "--\nBob Smith"


def test_signature_package_imports_without_ml_extra() -> None:
    import talon.signature as signature

    assert signature.EXTRACTOR_FILENAME.endswith("classifier")
    assert signature.EXTRACTOR_DATA.endswith("train.data")


@pytest.mark.skipif(talon.ML_ENABLED, reason="only without talon[ml]")
def test_extract_requires_ml_extra() -> None:
    import talon.signature as signature

    with pytest.raises(ImportError, match=r"talon\[ml\]"):
        signature.extract


def test_extract_requires_classifier_not_only_extraction(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """numpy can import extraction while sklearn and joblib are missing."""
    import importlib
    import types

    import talon.signature as signature

    real_import_module = importlib.import_module

    def import_module(name: str,
                      package: str | None = None) -> types.ModuleType:
        if name == signature.__name__ + ".learning.classifier":
            raise ImportError("No module named sklearn")
        if name == signature.__name__ + ".extraction":
            module = types.ModuleType(name)
            setattr(module, "extract", lambda body, sender: (body, None))
            return module
        return real_import_module(name, package)

    monkeypatch.setattr(importlib, "import_module", import_module)
    for attr in ("extract", "extraction"):
        monkeypatch.delitem(signature.__dict__, attr, raising=False)

    with pytest.raises(ImportError, match=r"talon\[ml\]"):
        signature.extract


@pytest.mark.ml
def test_extract_is_exported_with_ml_extra() -> None:
    from talon.signature import extract

    assert callable(extract)
