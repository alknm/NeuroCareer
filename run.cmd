@echo off
REM ============================================================
REM NeuroCareer - one-click launcher for Windows reviewers.
REM
REM Steps performed (idempotent):
REM   1. Verify Python 3.10+ is available.
REM   2. Create a virtual environment in .\.venv (if missing).
REM   3. Install requirements.txt into .venv (skipped if marker exists).
REM   4. Launch the Streamlit app, opening the browser automatically.
REM
REM First run: ~3-5 minutes (downloads ~200 MB of dependencies).
REM Subsequent runs: ~3 seconds.
REM ============================================================

setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo === NeuroCareer launcher ===
echo.

REM --- 1. Find Python ---------------------------------------------------
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python is not installed or not on PATH.
    echo Install Python 3.10 or newer from https://www.python.org/downloads/
    echo and tick "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo Found Python !PYVER!

REM Quick check that we are on >= 3.10
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python 3.10 or newer is required ^(found !PYVER!^).
    pause
    exit /b 1
)

REM --- 2. Create venv if missing ---------------------------------------
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment in .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv.
        pause
        exit /b 1
    )
)

set "PY=.venv\Scripts\python.exe"
set "PIP=.venv\Scripts\pip.exe"

REM --- 3. Install requirements (idempotent) ----------------------------
if not exist ".venv\.installed" (
    echo Upgrading pip ...
    "%PY%" -m pip install --upgrade pip --quiet --disable-pip-version-check
    echo Installing dependencies ^(this can take 3-5 minutes the first time^) ...
    "%PIP%" install --quiet --disable-pip-version-check -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] pip install failed.
        pause
        exit /b 1
    )
    echo. > ".venv\.installed"
    echo Dependencies installed.
)

REM --- 4. Launch the app -----------------------------------------------
echo.
echo Starting Streamlit on http://localhost:8501 ...
echo Press Ctrl+C in this window to stop the app.
echo.
"%PY%" -m streamlit run app.py --server.port 8501

endlocal
