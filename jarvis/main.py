"""
JARVIS - Assistente de IA com Voz
Usa: python main.py           → modo voz (microfone)
     python main.py --text    → modo texto (teclado)
"""

import sys
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, SYSTEM_PROMPT, ASSISTANT_NAME, USER_NAME
from voice import speak, listen, listen_keyboard
from tools import TOOL_DEFINITIONS, execute_tool
import memory as mem

# ─── MODO DE INPUT ────────────────────────────────────────────────────────────
USE_VOICE = "--text" not in sys.argv

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Historial da conversa (mantido em memória durante a sessão)
conversation: list[dict] = []

# Máximo de mensagens no historial antes de fazer summary
MAX_HISTORY = 20


def call_claude(user_message: str) -> str:
    """Envia mensagem ao Claude com histórico e ferramentas. Retorna resposta final."""
    global conversation

    conversation.append({"role": "user", "content": user_message})

    # Loop de ferramenta (Claude pode chamar ferramentas várias vezes)
    while True:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=8096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=conversation
        )

        # Adiciona resposta do assistente ao histórico
        conversation.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Extrai texto da resposta
            text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text += block.text
            return text.strip()

        if response.stop_reason == "tool_use":
            # Executa as ferramentas pedidas
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    print(f"  [🔧 {block.name}: {result[:80]}{'...' if len(result) > 80 else ''}]")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            conversation.append({"role": "user", "content": tool_results})
            continue

        # Stop reason inesperado
        break

    return "Não consegui processar o pedido."


def trim_history():
    """Limita o tamanho do histórico para evitar contexto demasiado longo."""
    global conversation
    if len(conversation) > MAX_HISTORY:
        # Guarda resumo e mantém só as últimas N mensagens
        summary = f"Conversa anterior com {len(conversation)} mensagens trocadas."
        mem.update_history_summary(summary)
        # Mantém as últimas 10 mensagens
        conversation = conversation[-10:]


def startup():
    """Lê memórias e anuncia arranque."""
    memories = mem.read_memory()
    has_memories = "Nenhuma memória" not in memories

    if has_memories:
        # Injeta memórias como contexto inicial
        conversation.append({
            "role": "user",
            "content": f"[CONTEXTO INICIAL - memórias guardadas]\n{memories}"
        })
        conversation.append({
            "role": "assistant",
            "content": "Memórias carregadas. Pronto para assistir."
        })

    greeting = f"Sistemas online. Pronto para assistir, {USER_NAME}."
    if has_memories:
        greeting = f"Bem-vindo de volta, {USER_NAME}. Memórias carregadas. Como posso ajudar?"

    speak(greeting)


def main():
    print(f"{'='*50}")
    print(f"  {ASSISTANT_NAME} - Assistente de IA")
    print(f"  Modo: {'🎤 Voz' if USE_VOICE else '⌨️  Texto'}")
    print(f"  Diz 'sair' ou 'fechar' para terminar")
    print(f"{'='*50}\n")

    if not ANTHROPIC_API_KEY:
        print("❌ ERRO: ANTHROPIC_API_KEY não definida!")
        print("   Cria um ficheiro .env com: ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    startup()

    listen_fn = listen if USE_VOICE else listen_keyboard

    while True:
        try:
            user_input = listen_fn()

            if not user_input:
                if USE_VOICE:
                    continue  # Nada ouvido, continua a ouvir
                else:
                    continue

            # Comandos de saída
            if any(w in user_input.lower() for w in ["sair", "fechar", "desligar", "exit", "quit"]):
                speak(f"Até logo, {USER_NAME}. JARVIS a desligar.")
                break

            # Processa e responde
            response = call_claude(user_input)

            if response:
                speak(response)
                trim_history()

        except KeyboardInterrupt:
            speak(f"Interrompido. Até logo, {USER_NAME}.")
            break
        except Exception as e:
            print(f"[Erro: {e}]")
            if USE_VOICE:
                speak("Ocorreu um erro. Tente novamente.")


if __name__ == "__main__":
    main()
