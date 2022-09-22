@echo off
:loop
CLS
%~dp0\.venv\scripts\python.exe %~dp0\main.py
TIMEOUT /t 5
GOTO loop
PAUSE