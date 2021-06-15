#!/usr/bin/env bash
set -ex
REPORT_PATH="${REPORT_PATH:-./}"
nosetests --with-xunit --with-coverage --cover-xml --cover-xml-file $REPORT_PATH/coverage.xml --xunit-file=$REPORT_PATH/nosetests.xml --cover-package=talon .
