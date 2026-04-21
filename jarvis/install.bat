@echo off
echo Instalando dependencias do JARVIS...
echo.

python -m pip install --upgrade pip
pip install anthropic edge-tts SpeechRecognition python-dotenv

echo.
echo Tentando instalar PyAudio (necessario para microfone)...
pip install pyaudio

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo PyAudio falhou. A tentar via pipwin...
    pip install pipwin
    pipwin install pyaudio
)

echo.
echo === INSTALACAO CONCLUIDA ===
echo.
echo Proximos passos:
echo  1. Copia .env.example para .env
echo  2. Adiciona a tua ANTHROPIC_API_KEY no .env
echo  3. Corre: python main.py --text   (para testar sem microfone)
echo  4. Corre: python main.py          (modo voz completo)
echo.
pause
