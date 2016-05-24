#!/bin/bash

VENV=castenv

virtualenv $VENV
source $VENV/bin/activate
pip install -r requirements.txt

