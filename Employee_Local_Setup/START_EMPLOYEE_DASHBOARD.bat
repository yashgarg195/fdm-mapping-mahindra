@echo off
setlocal EnableExtensions

title Mahindra Training Analytics Dashboard

set "SETUP_DIR=%~dp0"
for %%I in ("%SETUP_DIR%..") do set "APP_DIR=%%~fI"
cd /d "%APP_DIR%"

set "RUNTIME_DIR=%APP_DIR%\.local_runtime"
set "LOCAL_PYTHON_DIR=%RUNTIME_DIR%\python"
set "LOCAL_PYTHON=%LOCAL_PYTHON_DIR%\python.exe"
set "PYTHON_INSTALLER=%RUNTIME_DIR%\python-installer.exe"
set "PYTHON_DOWNLOAD_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"

echo.
echo ============================================================
echo   Mahindra Training Analytics ^& Manpower Intelligence
echo ============================================================
echo.
echo This launcher sets up and runs the dashboard on this laptop.
echo Company data is processed locally. Nothing is uploaded by this launcher.
echo.

if not exist "app.py" (
    echo ERROR: app.py was not found.
    echo Keep the Employee_Local_Setup folder inside the main dashboard folder.
    echo.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERROR: requirements.txt was not found.
    echo Keep all dashboard files together in the main dashboard folder.
    echo.
    pause
    exit /b 1
)

if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%" >nul 2>&1

set "PYTHON_CMD="
if exist "%LOCAL_PYTHON%" set PYTHON_CMD="%LOCAL_PYTHON%"

if "%PYTHON_CMD%"=="" if /i "%~1"=="--check" (
    py -3 --version >nul 2>&1
    if %errorlevel%==0 set "PYTHON_CMD=py -3"
    if "%PYTHON_CMD%"=="" (
        python --version >nul 2>&1
        if %errorlevel%==0 set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" if /i not "%~1"=="--check" (
    echo Private local Python was not found. Installing it inside this app folder...
    echo This first-time setup needs internet access.
    echo.

    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_DOWNLOAD_URL%' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing } catch { exit 1 }"
    if errorlevel 1 (
        echo.
        echo ERROR: Could not download Python.
        echo Checking whether this laptop already has a usable Python install...
        echo.
        py -3 --version >nul 2>&1
        if %errorlevel%==0 set "PYTHON_CMD=py -3"
        if "%PYTHON_CMD%"=="" (
            python --version >nul 2>&1
            if %errorlevel%==0 set "PYTHON_CMD=python"
        )
        if "%PYTHON_CMD%"=="" (
            echo ERROR: Python download was blocked and no existing Python was found.
            echo Check internet/proxy access or ask IT to run the setup.
            echo.
            pause
            exit /b 1
        )
        echo Existing Python found. Continuing with it for this laptop.
        echo.
    ) else (
        "%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 TargetDir="%LOCAL_PYTHON_DIR%" Include_pip=1 Include_launcher=0 PrependPath=0 Include_test=0
        if errorlevel 1 (
            echo.
            echo ERROR: Python installation failed.
            echo Ask IT/admin to check Windows security or installation permissions.
            echo.
            pause
            exit /b 1
        )

        if not exist "%LOCAL_PYTHON%" (
            echo.
            echo ERROR: Local Python was installed but python.exe was not found.
            echo Ask IT/admin to check this folder:
            echo %LOCAL_PYTHON_DIR%
            echo.
            pause
            exit /b 1
        )

        set PYTHON_CMD="%LOCAL_PYTHON%"
    )
)

echo Python ready.

if /i "%~1"=="--check" (
    echo.
    echo Launcher self-check passed.
    echo App folder: %APP_DIR%
    echo Python command: %PYTHON_CMD%
    echo.
    exit /b 0
)

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo First-time setup: creating local app environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo.
        echo ERROR: Could not create the local Python environment.
        echo Ask IT/admin to confirm Python is working correctly.
        echo.
        pause
        exit /b 1
    )
) else (
    echo Local app environment found.
)

echo.
echo Checking required dashboard packages...
if exist "Employee_Local_Setup\offline_packages\" (
    echo Offline package bundle found. Installing from local files...
    ".venv\Scripts\python.exe" -m pip install --no-index --find-links="Employee_Local_Setup\offline_packages" -r requirements.txt
) else (
    echo No offline package bundle found. Installing from Python package servers...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)
if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed.
    echo Connect to the internet or ask IT to create Employee_Local_Setup\offline_packages.
    echo.
    pause
    exit /b 1
)

echo.
echo Starting dashboard...
echo A browser window should open automatically.
echo If it does not open, use this address:
echo http://localhost:8501
echo.
echo Keep this window open while using the dashboard.
echo Press Ctrl+C in this window to stop the dashboard.
echo.

".venv\Scripts\python.exe" -m streamlit run app.py --server.address=localhost --server.port=8501

echo.
echo Dashboard stopped.
pause
