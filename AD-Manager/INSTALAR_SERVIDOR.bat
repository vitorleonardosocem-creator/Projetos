@echo off
setlocal EnableDelayedExpansion

:: Detecta a pasta onde este script esta
set "DIR=%~dp0"
if "%DIR:~-1%"=="\" set "DIR=%DIR:~0,-1%"
set "NGINX=%DIR%\nginx"
set "SSL=%DIR%\ssl"

echo ============================================
echo  AD Manager - Instalador HTTPS (Nginx)
echo  Pasta: %DIR%
echo ============================================
echo.

:: Verifica Admin
net session >nul 2>&1
if errorlevel 1 (
    echo ERRO: Corre como Administrador!
    echo Botao direito no .bat ^> Executar como Administrador
    pause
    exit /b 1
)

:: Detecta IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "IP=%%a"
    set "IP=!IP: =!"
    goto :got_ip
)
:got_ip

echo IP detectado: %IP%
set /p CONFIRM="Confirma? (Enter aceita, ou escreve outro IP): "
if not "!CONFIRM!"=="" set "IP=!CONFIRM!"
echo A usar IP: %IP%
echo.

:: Verifica Nginx
echo [1/5] A verificar Nginx...
if not exist "%NGINX%\nginx.exe" (
    echo.
    echo ERRO: Nao encontrei nginx.exe em:
    echo %NGINX%\nginx.exe
    echo.
    echo Descarrega em: https://nginx.org/en/download.html
    echo Stable version ^> Windows ^> extrai para %NGINX%\
    pause
    exit /b 1
)
echo    OK

:: Cria pasta ssl
if not exist "%SSL%" mkdir "%SSL%"

:: Copia o PS1 para a pasta e corre-o
echo.
if not exist "%DIR%\instalar_setup.ps1" (
    echo ERRO: Ficheiro instalar_setup.ps1 nao encontrado em %DIR%\
    echo Certifica-te que o instalar_setup.ps1 esta na mesma pasta que este .bat
    pause
    exit /b 1
)

powershell -ExecutionPolicy Bypass -File "%DIR%\instalar_setup.ps1" -DIR "%DIR%" -IP "%IP%"
if errorlevel 1 (
    echo.
    echo ERRO: O script PowerShell falhou. Ver mensagens acima.
    pause
    exit /b 1
)

:: Firewall
echo.
echo A configurar firewall...
netsh advfirewall firewall delete rule name="AD-Manager-80"  >nul 2>&1
netsh advfirewall firewall delete rule name="AD-Manager-443" >nul 2>&1
netsh advfirewall firewall add rule name="AD-Manager-80"  dir=in action=allow protocol=TCP localport=80  >nul
netsh advfirewall firewall add rule name="AD-Manager-443" dir=in action=allow protocol=TCP localport=443 >nul
echo    OK - Portas 80 e 443 abertas

:: Inicia Nginx
echo.
echo A iniciar Nginx...
taskkill /f /im nginx.exe >nul 2>&1
cd /d "%NGINX%"
start /b nginx.exe
timeout /t 2 >nul
tasklist | find /i "nginx.exe" >nul 2>&1
if errorlevel 1 (
    echo AVISO: Nginx pode nao ter iniciado.
    echo Verifica: %NGINX%\logs\error.log
) else (
    echo    OK - Nginx a correr!
)

echo.
echo ============================================
echo  INSTALACAO CONCLUIDA!
echo ============================================
echo.
echo  Acesso: https://%IP%/azure-user-manager.html
echo.
echo  AZURE AD - Adicionar URI de redireccionamento:
echo    https://%IP%/azure-user-manager.html
echo.
echo  OUTROS PCs - Instalar certificado (1x por PC):
echo    Ficheiro: %SSL%\server.cer
echo    Duplo clique ^> Instalar Certificado
echo    ^> Computador Local
echo    ^> Autoridades de Raiz de Certificacao Fidedignas
echo.
pause
