"""The package exploits machine learning for parsing message signatures.

The public interface consists of only one `extract` function:

>>> (body, signature) = extract(body, sender)

Where body is the original message `body` and `sender` corresponds to a person
who sent the message.

`extract` and classifier loading require the ``ml`` extra
(``pip install talon[ml]``). Brute-force extraction in
``talon.signature.bruteforce`` works without it.

Call ``talon.init()`` (or ``initialize()``) before ``extract`` so each process
loads classifiers into memory.

The import of the package and the call to the `extract` function are better be
enclosed in a try-catch block in case they fail.

.. warning:: When making changes to features or emails the classifier is
trained against, don't forget to regenerate:

* signature/data/train.data and
* signature/data/classifier
"""

from __future__ import absolute_import
import importlib
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from talon.signature import extraction
    from talon.signature.extraction import extract as extract

_ML_EXTRA_ERROR = (
    "talon ML extras are not installed. Install them with: pip install 'talon[ml]'"
)

_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
EXTRACTOR_FILENAME = os.path.join(_DATA_DIR, 'classifier')
EXTRACTOR_DATA = os.path.join(_DATA_DIR, 'train.data')


def initialize() -> None:
    try:
        # Any: mypy does not allow setting attributes on a ModuleType
        extraction: Any = importlib.import_module(__name__ + '.extraction')
        classifier = importlib.import_module(__name__ + '.learning.classifier')
    except ImportError as exc:
        raise ImportError(_ML_EXTRA_ERROR) from exc
    extraction.EXTRACTOR = classifier.load(EXTRACTOR_FILENAME, EXTRACTOR_DATA)


def __getattr__(name: str) -> Any:
    if name not in ('extract', 'extraction'):
        raise AttributeError(
            "module {!r} has no attribute {!r}".format(__name__, name)
        )
    try:
        extraction = importlib.import_module(__name__ + '.extraction')
        # extraction imports with numpy alone. The classifier also needs
        # sklearn and joblib; do not export extract until that import works.
        importlib.import_module(__name__ + '.learning.classifier')
    except ImportError as exc:
        raise ImportError(_ML_EXTRA_ERROR) from exc
    globals()['extraction'] = extraction
    globals()['extract'] = extraction.extract
    return globals()[name]
