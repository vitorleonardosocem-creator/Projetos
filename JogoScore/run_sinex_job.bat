@echo off
cd /d "%~dp0"
python sinex_job.py >> sinex_job.log 2>&1
