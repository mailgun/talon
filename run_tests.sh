#!/usr/bin/env bash
set -ex
REPORT_PATH="${REPORT_PATH:-./}"
export PYTHONPATH="$PWD/talon:$PWD/talon-core"
nosetests --with-xunit --with-coverage --cover-xml --cover-xml-file $REPORT_PATH/coverage.xml --xunit-file=$REPORT_PATH/nosetests.xml --cover-package=talon --cover-package=talon-core talon talon-core
