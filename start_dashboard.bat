@echo off
TITLE Mahindra Training Analytics Dashboard
color 4F
echo.
echo ========================================================
echo   MAHINDRA TRAINING ANALYTICS - STARTUP SCRIPT
echo ========================================================
echo.
echo Starting the offline Streamlit dashboard...
echo.

:: Check if localtunnel is requested
set /p usetunnel="Do you want to enable global access via localtunnel? (Y/N): "
if /I "%usetunnel%"=="Y" (
    echo.
    echo Starting Streamlit in the background...
    start /B streamlit run app.py
    
    echo.
    echo Starting localtunnel...
    echo Please copy this URL to access the dashboard globally:
    echo.
    npx -y localtunnel --port 8501 --subdomain mahindra-training-dashboard
) else (
    echo.
    echo Starting local offline dashboard...
    streamlit run app.py
)

pause
