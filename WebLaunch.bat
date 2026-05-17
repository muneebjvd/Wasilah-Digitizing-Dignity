@echo off
TITLE Wasilah Launcher
ECHO Starting Wasilah System...
ECHO Please wait while the application loads.

:: This command runs your Streamlit app
python -m streamlit run "d:\University\Sem5\DBMS\PROJECT\PYTHON\app.py"

:: Keeps the window open if it crashes so you can read the error
PAUSE