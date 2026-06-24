@echo off
REM ============================================================
REM  Therapy Note Generator - double-click launcher (Windows)
REM  Activates the conda env, starts the app, opens the browser.
REM ============================================================

cd /d "%~dp0"

REM --- find the conda activate script (common install locations) ---
set "CONDA_BAT=%USERPROFILE%\miniconda3\Scripts\activate.bat"
if not exist "%CONDA_BAT%" set "CONDA_BAT=%USERPROFILE%\anaconda3\Scripts\activate.bat"
if not exist "%CONDA_BAT%" set "CONDA_BAT=%LOCALAPPDATA%\miniconda3\Scripts\activate.bat"
if not exist "%CONDA_BAT%" set "CONDA_BAT=C:\ProgramData\miniconda3\Scripts\activate.bat"

if not exist "%CONDA_BAT%" (
  echo.
  echo Could not find your conda installation automatically.
  echo Open start.bat in Notepad and set CONDA_BAT to the path of your
  echo miniconda3\Scripts\activate.bat file, then save and try again.
  echo.
  pause
  exit /b 1
)

call "%CONDA_BAT%" therapy-note-gen
if errorlevel 1 (
  echo.
  echo Could not activate the conda env "therapy-note-gen".
  echo Make sure it exists ^(conda create -n therapy-note-gen python=3.12^).
  echo.
  pause
  exit /b 1
)

python app.py

REM keep the window open if the app exits with an error
if errorlevel 1 pause
