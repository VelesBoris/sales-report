@echo off
cd /d "%~dp0"
set "INPUT=%~1"
if "%INPUT%"=="" set "INPUT=data\sales.csv"
if not exist "%INPUT%" (
    echo Input file not found: %INPUT%
    pause
    exit /b 1
)
python calc.py "%INPUT%"
pause