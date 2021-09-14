#!/bin/bash

VENV=castenv

python3 -m venv $VENV
source $VENV/bin/activate
pip3 install -r src/requirements.txt

