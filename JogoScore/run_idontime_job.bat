@echo off
cd /d "%~dp0"
python idontime_job.py >> idontime_job.log 2>&1
