from __future__ import annotations
import asyncio
import tempfile
import os
import speech_recognition as sr
import edge_tts
from config import TTS_VOICE, TTS_RATE, STT_LANGUAGE, STT_TIMEOUT, STT_PHRASE_LIMIT


# ─── TEXT TO SPEECH ────────────────────────────────────────────────────────────

async def _speak_async(text: str):
    """Converte texto em fala e reproduz."""
    communicate = edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    try:
        await communicate.save(tmp_path)
        # Reproduz com o player padrão do sistema
        if os.name == "nt":  # Windows
            os.system(f'start /wait wmplayer "{tmp_path}" /play /close 2>nul || '
                      f'powershell -c "(New-Object Media.SoundPlayer).PlaySync()" 2>nul || '
                      f'ffplay -nodisp -autoexit "{tmp_path}" -loglevel quiet 2>nul')
        else:
            os.system(f'mpg123 -q "{tmp_path}" 2>/dev/null || '
                      f'ffplay -nodisp -autoexit "{tmp_path}" -loglevel quiet 2>/dev/null')
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def speak(text: str):
    """Interface síncrona para TTS."""
    # Remove markdown que não soa bem em voz
    clean = text.replace("**", "").replace("*", "").replace("#", "").replace("`", "")
    print(f"\n🤖 JARVIS: {clean}\n")
    asyncio.run(_speak_async(clean))


# ─── SPEECH TO TEXT ────────────────────────────────────────────────────────────

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 1.0


def listen() -> str | None:
    """Ouve o microfone e retorna o texto reconhecido, ou None."""
    with sr.Microphone() as source:
        print("🎤 A ouvir... (fala agora)")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source,
                timeout=STT_TIMEOUT,
                phrase_time_limit=STT_PHRASE_LIMIT
            )
        except sr.WaitTimeoutError:
            return None

    try:
        text = recognizer.recognize_google(audio, language=STT_LANGUAGE)
        print(f"👤 Tu: {text}")
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"[Erro STT: {e}]")
        return None


def listen_keyboard() -> str | None:
    """Modo teclado: recebe input por texto (para testar sem microfone)."""
    try:
        text = input("👤 Tu: ").strip()
        return text if text else None
    except (EOFError, KeyboardInterrupt):
        return None
