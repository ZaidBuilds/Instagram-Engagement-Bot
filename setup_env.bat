@echo off
cd /d "%~dp0"
if not exist ".env" (
    copy .env.example .env
    echo Created .env file. Please edit it with your API keys!
    notepad .env
) else (
    echo .env file already exists.
)
pause
