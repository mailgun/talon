#!/bin/bash
#    File Name: build-dock.sh
#      Created: 20201210-0744
#      Purpose: Build docker image

VERSION_FILE=talon/web/__init__.py
VERSION_NO=`git rev-parse --short HEAD`
NAME=talon-web

echo "# -*- encoding: utf-8 -*-" > $VERSION_FILE
echo >> $VERSION_FILE
echo "__version__ = \"$VERSION_NO\"" >> $VERSION_FILE

docker build -t $NAME .
