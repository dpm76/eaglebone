#!/bin/bash
export PYTHONPATH=../drone:../desktopRemoteControl
python -m unittest discover -p *TestCases.py
