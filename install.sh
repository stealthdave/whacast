#!/bin/bash

VENV=castenv

python3 -m venv $VENV
source $VENV/bin/activate
pip install -r requirements.txt

