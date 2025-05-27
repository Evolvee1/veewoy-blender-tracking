@echo off
REM Build script for veewoy-blender-tracking main GUI using the correct Python 3.9 installation

REM Set the path to the correct Python 3.9 installation
set PYTHON_EXE="C:\Program Files\Python39\python.exe"

REM Clean previous build and dist directories
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Run PyInstaller with the main_gui.spec file and explicit icon argument
%PYTHON_EXE% -m PyInstaller main_gui.spec --noconfirm

echo Build complete.
pause 