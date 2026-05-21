@echo off
setlocal EnableExtensions

title Prepare Offline Package Bundle

set "SETUP_DIR=%~dp0"
for %%I in ("%SETUP_DIR%..") do set "APP_DIR=%%~fI"
cd /d "%APP_DIR%"

echo.
echo ============================================================
echo   Prepare Offline Package Bundle
echo ============================================================
echo.
echo Run this once on a Windows machine with internet access.
echo It downloads dashboard Python packages into:
echo Employee_Local_Setup\offline_packages
echo.

if not exist "requirements.txt" (
    echo ERROR: requirements.txt was not found.
    echo Keep the Employee_Local_Setup folder inside the main dashboard folder.
    echo.
    pause
    exit /b 1
)

set "PYTHON_CMD="
py -3 --version >nul 2>&1
if %errorlevel%==0 set "PYTHON_CMD=py -3"

if "%PYTHON_CMD%"=="" (
    python --version >nul 2>&1
    if %errorlevel%==0 set "PYTHON_CMD=python"
)

if "%PYTHON_CMD%"=="" (
    echo ERROR: Python was not found on this preparation machine.
    echo Run START_EMPLOYEE_DASHBOARD.bat once first, or install Python 3.11+.
    echo.
    pause
    exit /b 1
)

if not exist "Employee_Local_Setup\offline_packages" mkdir "Employee_Local_Setup\offline_packages"

echo.
echo Downloading packages...
%PYTHON_CMD% -m pip download -r requirements.txt -d "Employee_Local_Setup\offline_packages"
if errorlevel 1 (
    echo.
    echo ERROR: Could not download all packages.
    echo Check internet connection, proxy settings, or Python installation.
    echo.
    pause
    exit /b 1
)

echo.
echo Offline package bundle is ready.
echo Copy the complete dashboard folder to employee laptops.
echo.
pause
