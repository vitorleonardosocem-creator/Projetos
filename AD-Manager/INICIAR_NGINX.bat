@echo off
:: Remove a variavel NGINX do ambiente que causa conflito
reg delete "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v NGINX /f >nul 2>&1
reg delete "HKCU\Environment" /v NGINX /f >nul 2>&1

:: Para qualquer instancia anterior
taskkill /f /im nginx.exe >nul 2>&1
timeout /t 1 >nul

:: Inicia o nginx sem a variavel de ambiente
set "NGINX="
cd /d "%~dp0nginx"
start "" nginx.exe

timeout /t 2 >nul
tasklist | find /i "nginx.exe" >nul 2>&1
if errorlevel 1 (
    echo ERRO: Nginx nao iniciou! Ver logs\error.log
) else (
    echo OK - Nginx a correr em https://192.168.10.156/azure-user-manager.html
)
pause
