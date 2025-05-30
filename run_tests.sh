#!/bin/bash

# nosetests -s --with-coverage --cover-package=talon --cover-erase --logging-level=INFO
pytest --cov=talon --cov-report=term-missing tests/
