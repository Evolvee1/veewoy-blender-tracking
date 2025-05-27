@echo off
REM Setup script for veewoy-blender-tracking external tools

REM Set the path to the correct Python 3.9 installation
set PYTHON_EXE="C:\Program Files\Python39\python.exe"

REM Upgrade pip for reliability
%PYTHON_EXE% -m pip install --upgrade pip

REM Install dependencies for external tools
%PYTHON_EXE% -m pip install -r external_tools/requirements.txt

echo Installation complete.
pause 