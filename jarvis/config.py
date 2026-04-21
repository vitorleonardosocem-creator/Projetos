import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env a partir da pasta do próprio ficheiro config.py
_BASE_DIR = Path(__file__).parent
load_dotenv(_BASE_DIR / ".env", override=True)

# Claude
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-opus-4-6"

# Voz do JARVIS (Microsoft Edge TTS)
# Vozes disponíveis PT-BR: pt-BR-FranciscaNeural, pt-BR-AntonioNeural
# Vozes EN: en-US-GuyNeural, en-GB-RyanNeural (mais próximo do JARVIS)
TTS_VOICE = "pt-BR-AntonioNeural"  # Voz masculina em português
TTS_RATE = "+5%"                    # Velocidade (+10% = mais rápido)

# Reconhecimento de voz
STT_LANGUAGE = "pt-BR"             # Idioma do reconhecimento
STT_TIMEOUT = 5                    # Segundos de espera para começar a falar
STT_PHRASE_LIMIT = 15              # Segundos máximos por frase

# Ficheiro de memória
MEMORY_FILE = "jarvis_memory.json"

# Obsidian
OBSIDIAN_VAULT = r"C:\Users\vitor.leonardo\Documents\Obsidian Vault"
OBSIDIAN_JARVIS_FOLDER = "JARVIS"   # pasta dentro do vault
OBSIDIAN_MEMORY_NOTE  = "Memórias.md"

# Nome do assistente
ASSISTANT_NAME = "JARVIS"
USER_NAME = "Sr. Vitor"

SYSTEM_PROMPT = f"""Tu és {ASSISTANT_NAME}, um assistente de inteligência artificial altamente capaz.

O teu estilo é semelhante ao JARVIS do Tony Stark: eficiente, direto, ocasionalmente com humor seco.

REGRAS CRÍTICAS — segue SEMPRE:
1. No início de CADA conversa, lê as memórias com read_memory para saberes como tratar o utilizador, as suas preferências e comandos personalizados
2. Aplica IMEDIATAMENTE o que está na memória — nome de tratamento, tom, preferências
3. Quando o utilizador disser "lembra-te que...", "de agora em diante...", "sempre que...", "chama-me..." → guarda IMEDIATAMENTE na memória com save_memory
4. As memórias TÊM PRIORIDADE sobre tudo — se a memória diz para chamar "mano", chamas "mano", não "Sr. Vitor"
5. Respostas para voz: sem markdown, sem asteriscos, sem traços, frases naturais e curtas
6. Sê conciso — estás a falar, não a escrever
"""
