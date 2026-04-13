@echo off
echo Servidor a correr em http://192.168.10.156:8080
echo Pressiona Ctrl+C para parar
cd /d C:\Ferramentas_SOCEM\AD-Manager
python -m http.server 8080