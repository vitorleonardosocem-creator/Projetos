@echo off
title Organizador de Faturas PDF
echo.
echo ==============================================
echo   Organizador de Faturas PDF
echo ==============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Instala em: https://www.python.org/downloads/
    echo Marca "Add Python to PATH" durante a instalacao.
    pause
    exit /b
)

echo A verificar/instalar dependencias...
python -m pip install --quiet --upgrade pdfplumber pypdf pytesseract pillow pdf2image 2>nul

echo Dependencias prontas!
echo.
echo A iniciar a aplicacao...
python "%~dp0organizar_faturas.py"

if errorlevel 1 (
    echo.
    echo [ERRO] Algo correu mal.
    pause
)
