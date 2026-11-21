@echo off
REM ============================================================
REM  Creates a FRESH virtual environment (folder "venv") and installs everything
REM  Double-click this file or run it from the project folder.
REM ============================================================
cd /d "%~dp0"
set PYCMD=
for %%V in (3.11 3.12 3.10 3.13) do (
    if not defined PYCMD (
        py -%%V --version >nul 2>&1 && set PYCMD=py -%%V
    )
)
if not defined PYCMD (
    echo ERROR: Python 3.10-3.13 not found. Install Python 3.11 from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^) and run this file again.
    if /i not "%1"=="nopause" pause
    exit /b 1
)
echo Using: %PYCMD%
%PYCMD% --version
if exist venv (
    echo The folder "venv" already exists - delete it first if you want a completely fresh environment.
) else (
    %PYCMD% -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name prog_ai_lab --display-name "Python (Prog_for_AI_Lab)"
echo.
echo ===== Checking the installation =====
python check_env.py
echo.
echo Done. In VS Code: select the interpreter venv\Scripts\python.exe ^(see VSCODE_GUIDE.md^)
if /i not "%1"=="nopause" pause
