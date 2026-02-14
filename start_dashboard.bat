@echo off
cd /d "%~dp0"
call streamlit run dashboard/app.py
pause
