@echo off
title JogoScore SOCEM — Porta 8005
cd /d "%~dp0"
echo.
echo  ============================================
echo   JogoScore SOCEM — A arrancar na porta 8005
echo  ============================================
echo.
uvicorn main:app --host 0.0.0.0 --port 8005 --workers 2
pause
