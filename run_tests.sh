#!/usr/bin/env bash
set -ex
REPORT_PATH="${REPORT_PATH:-.}"
pytest --cov=talon --cov-report=term --cov-report="xml:$REPORT_PATH/coverage.xml" --junitxml="$REPORT_PATH/nosetests.xml" .
