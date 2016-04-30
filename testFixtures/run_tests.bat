@echo off
set PYTHONPATH=..\drone;..\desktopRemoteControl;
python -m unittest discover -p *TestCases.py
