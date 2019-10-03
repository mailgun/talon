#!/usr/bin/env bash
set -ex
REPORT_PATH="${REPORT_PATH:-.}"
pytest --cov=talon/talon --cov=talon-core/talon_core --cov-report=term --cov-report="xml:$REPORT_PATH/coverage.xml" --junitxml="$REPORT_PATH/nosetests.xml" talon talon-core
