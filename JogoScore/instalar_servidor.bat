@echo off
title JogoScore — Instalacao no Servidor
cd /d "%~dp0"
echo.
echo  ============================================
echo   JogoScore — Instalacao de Dependencias
echo  ============================================
echo.

REM Verificar Python
python --version > nul 2>&1
if errorlevel 1 (
    echo  [ERRO] Python nao encontrado!
    echo  Instala Python 3.11+ em https://python.org
    echo  e garante que esta no PATH do sistema.
    pause
    exit /b 1
)

echo  [OK] Python encontrado:
python --version

echo.
echo  A instalar dependencias...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo  ============================================
echo   Instalacao concluida!
echo  ============================================
echo.
echo  Proximos passos:
echo   1. Corre: python criar_bd.py
echo   2. Corre: python criar_admin.py
echo   3. Abre PowerShell como Admin e corre:
echo      powershell -ExecutionPolicy Bypass -File configurar_tarefas.ps1
echo   4. Reinicia o servidor ou corre manualmente:
echo      start_JogoScore.bat
echo.
pause
