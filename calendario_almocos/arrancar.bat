@echo off
echo ============================================
echo   Calendario de Almocos - a iniciar...
echo ============================================
echo.
cd /d "%~dp0"
pip install -r requirements.txt --quiet
echo.
echo Acesso: http://192.168.10.156:5002
echo Para parar: fechar esta janela ou Ctrl+C
echo.
python app.py
pause
