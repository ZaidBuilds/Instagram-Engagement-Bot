@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python 3.13 virtual environment...
    py -3.13 -m venv .venv
    if errorlevel 1 (
        echo Failed to create .venv with Python 3.13.
        echo Install Python 3.13 and ensure the 'py' launcher is available.
        pause
        exit /b 1
    )
)

set "PYTHON_EXE=.venv\Scripts\python.exe"

echo Verifying dependencies...
"%PYTHON_EXE%" -c "import instagrapi, streamlit, groq, dotenv" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies from requirements.txt...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Dependency installation failed.
        pause
        exit /b 1
    )
)

if not exist ".env" (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >nul
        echo Created .env from .env.example.
    ) else (
        echo .env not found and .env.example is missing.
        pause
        exit /b 1
    )
)

echo Initializing database...
"%PYTHON_EXE%" -c "from src.database import init_db; init_db()" >nul 2>&1
if errorlevel 1 (
    echo Database initialization failed.
    pause
    exit /b 1
)

echo Starting bot...
"%PYTHON_EXE%" run_bot.py
