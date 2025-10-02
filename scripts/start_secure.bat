@echo off
echo Starting Validex in Secure Mode...
set FLASK_HOST=127.0.0.1
set FLASK_DEBUG=false
set FLASK_ENV=production
python run.py
