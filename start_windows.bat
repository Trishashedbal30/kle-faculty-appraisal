@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please follow START_HERE.md to create the Python 3.12 virtual environment first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe manage.py run
pause
