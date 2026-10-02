@echo off
title MSBTE Student Saver
color 0B

echo ======================================================================
echo    MSBTE Student Saver - Academic Performance & Early Warning System
echo    3rd-Year Diploma Computer Engineering Project
echo ======================================================================
echo.

:: 1. Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not found on your system PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    echo and ensure "Add python.exe to PATH" is checked.
    echo.
    pause
    exit /b 1
)

:: 2. Check and train ML model if model.pkl is missing
if not exist "ml\model.pkl" (
    echo [*] Training Machine Learning Decision Tree model...
    python ml\train_model.py
    echo.
)

:: 3. Check and initialize database if database.db is missing
if not exist "database.db" (
    echo [*] Initializing SQLite database with 120 demo MSBTE student records...
    python seed_data.py
    echo.
)

echo [*] Starting Flask Web Application on http://127.0.0.1:5000 ...
echo [*] Opening default web browser in 3 seconds...
echo.
echo ----------------------------------------------------------------------
echo  Demo Login Credentials:
echo   - Admin Role:    admin / admin123
echo   - Student Role:  2300520001 / stud@0001
echo ----------------------------------------------------------------------
echo.
echo Press CTRL+C in this terminal window to stop the server.
echo ======================================================================
echo.

:: Launch browser in background after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

:: Start Flask server
python app.py

pause
