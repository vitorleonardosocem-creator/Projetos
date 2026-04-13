@echo off
:: ============================================================
::  run_sinex_job.bat
::  Adicionar ao Windows Task Scheduler para correr ao arranque
::  ou diariamente.
::
::  Como configurar o Task Scheduler:
::  1. Abre "Task Scheduler" (Gestor de Tarefas Agendadas)
::  2. "Create Basic Task" → nome: "Sinex Job"
::  3. Trigger: "Daily" às 05:55
::  4. Action: "Start a program"
::       Program: C:\caminho\para\run_sinex_job.bat
::  5. Finish
:: ============================================================

cd /d "%~dp0"
python sinex_job.py >> sinex_job_startup.log 2>&1
