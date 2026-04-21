"""
JARVIS - Interface Web
Corre: python app.py
Abre:  http://localhost:5000
"""
from __future__ import annotations
import asyncio
import json
import os
import tempfile
import anthropic
import edge_tts
from flask import Flask, render_template, request, jsonify, send_file, Response, stream_with_context
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, SYSTEM_PROMPT, TTS_VOICE, TTS_RATE
from tools import TOOL_DEFINITIONS, execute_tool
import memory as mem

app = Flask(__name__)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Historial da sessão web (em memória)
conversation: list[dict] = []
MAX_HISTORY = 30


# ─── MODEL ROUTING ─────────────────────────────────────────────────────────────

def choose_model(message: str) -> str:
    """Uses Haiku for simple questions, Opus for complex tasks."""
    simple_keywords = [
        'olá', 'oi', 'que horas', 'que dia', 'obrigado',
        'ok', 'sim', 'não', 'volume', 'abre', 'fecha',
        'hello', 'hi', 'thanks', 'yes', 'no'
    ]
    msg_lower = message.lower()

    # Short + simple keyword = Haiku
    if len(message) < 60 and any(k in msg_lower for k in simple_keywords):
        return "claude-haiku-4-5"

    # Complex tasks = Opus
    complex_keywords = [
        'cria', 'programa', 'projeto', 'código', 'analisa',
        'explica', 'escreve', 'desenvolve', 'implementa',
        'create', 'program', 'project', 'code', 'analyze',
        'explain', 'write', 'develop', 'implement'
    ]
    if any(k in msg_lower for k in complex_keywords) or len(message) > 200:
        return "claude-opus-4-6"

    # Default: Sonnet (balance)
    return "claude-sonnet-4-6"


def model_display_name(model_id: str) -> str:
    """Returns short display name for a model ID."""
    if "haiku" in model_id:
        return "Haiku"
    if "opus" in model_id:
        return "Opus"
    return "Sonnet"


# ─── MEMORIES ──────────────────────────────────────────────────────────────────

def load_memories_into_context():
    """Injeta as memórias + notas Obsidian no início da conversa."""
    memories = mem.read_memory()
    obsidian_extra = mem.read_obsidian_extra()

    context_parts = []
    if "Nenhuma memória" not in memories:
        context_parts.append(memories)
    if obsidian_extra:
        context_parts.append("NOTAS ADICIONAIS DO OBSIDIAN:\n" + obsidian_extra)

    if context_parts:
        conversation.append({
            "role": "user",
            "content": f"[SISTEMA - carrega este contexto antes de responder]\n" + "\n\n".join(context_parts)
        })
        conversation.append({
            "role": "assistant",
            "content": "Contexto carregado. Vou seguir todas as preferências e notas guardadas."
        })


# ─── SCREENSHOT RESULT HANDLER ─────────────────────────────────────────────────

def _build_tool_result_content(tool_result_str: str) -> list | str:
    """
    Se o resultado for um screenshot JSON, devolve content com image block.
    Caso contrário, devolve o texto simples.
    """
    try:
        data = json.loads(tool_result_str)
        if isinstance(data, dict) and data.get("type") == "screenshot":
            # Devolve content com texto + imagem para o Claude analisar
            return [
                {
                    "type": "text",
                    "text": "Screenshot tirada com sucesso. Analisa a imagem:"
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": data.get("media_type", "image/png"),
                        "data": data["base64"]
                    }
                }
            ]
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return tool_result_str


# ─── CALL CLAUDE (NON-STREAMING, usado pelo scheduler) ─────────────────────────

def call_claude(user_message: str, images: list[dict] | None = None) -> tuple[str, list[dict]]:
    """Envia ao Claude e devolve (resposta, tool_calls_log)."""
    global conversation

    # Constrói content da mensagem do utilizador
    if images:
        content: list = [{"type": "text", "text": user_message}]
        for img in images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img.get("media_type", "image/jpeg"),
                    "data": img["data"]
                }
            })
        conversation.append({"role": "user", "content": content})
    else:
        conversation.append({"role": "user", "content": user_message})

    tool_log = []
    model = choose_model(user_message)

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=8096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=conversation
        )
        conversation.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            text = "".join(b.text for b in response.content if hasattr(b, "text"))
            if len(conversation) > MAX_HISTORY:
                mem.update_history_summary(f"Conversa com {len(conversation)} mensagens.")
                conversation[:] = conversation[-10:]
            return text.strip(), tool_log

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_log.append({"tool": block.name, "result": result[:120]})
                    result_content = _build_tool_result_content(result)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_content
                    })
            conversation.append({"role": "user", "content": tool_results})
            continue
        break

    return "Não consegui processar o pedido.", tool_log


# ─── STREAMING GENERATOR ───────────────────────────────────────────────────────

def generate_stream(user_message: str, images: list[dict] | None = None):
    """Generator que produz SSE events para streaming da resposta do Claude."""
    global conversation

    # Escolhe modelo com base na mensagem
    model = choose_model(user_message)
    model_name = model_display_name(model)

    # Envia badge de modelo imediatamente
    yield f"data: {json.dumps({'type': 'model', 'model': model_name})}\n\n"

    # Constrói content da mensagem do utilizador
    if images:
        content: list = [{"type": "text", "text": user_message}]
        for img in images:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img.get("media_type", "image/jpeg"),
                    "data": img["data"]
                }
            })
        conversation.append({"role": "user", "content": content})
    else:
        conversation.append({"role": "user", "content": user_message})

    full_text = ""
    loop_count = 0
    max_loops = 10  # Segurança contra loops infinitos

    while loop_count < max_loops:
        loop_count += 1

        try:
            with client.messages.stream(
                model=model,
                max_tokens=8096,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=conversation
            ) as stream:
                # Stream de tokens de texto
                for text in stream.text_stream:
                    full_text += text
                    yield f"data: {json.dumps({'type': 'token', 'text': text})}\n\n"

                # Obtém mensagem final
                final = stream.get_final_message()

        except anthropic.BadRequestError as e:
            msg = str(e)
            err_msg = (
                "Saldo de créditos insuficiente. Vai a console.anthropic.com → Plans & Billing."
                if "credit balance" in msg or "too low" in msg
                else f"Erro na API: {msg}"
            )
            yield f"data: {json.dumps({'type': 'error', 'text': err_msg})}\n\n"
            return
        except anthropic.AuthenticationError:
            yield f"data: {json.dumps({'type': 'error', 'text': 'Chave de API inválida. Verifica o ficheiro .env.'})}\n\n"
            return
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'text': f'Erro: {str(e)}'})}\n\n"
            return

        # Guarda resposta no historial
        conversation.append({"role": "assistant", "content": final.content})

        # Se terminou normalmente, sai
        if final.stop_reason == "end_turn":
            break

        # Se usou ferramentas
        if final.stop_reason == "tool_use":
            tool_results = []
            for block in final.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    short_result = result[:200] if len(result) > 200 else result

                    # Notifica frontend
                    yield f"data: {json.dumps({'type': 'tool', 'name': block.name, 'result': short_result})}\n\n"

                    # Verifica se é screenshot para enviar como imagem
                    result_content = _build_tool_result_content(result)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_content
                    })

            conversation.append({"role": "user", "content": tool_results})
            # Continua o loop para obter a resposta final
            continue

        # Qualquer outro stop_reason: termina
        break

    # Limita historial
    if len(conversation) > MAX_HISTORY:
        mem.update_history_summary(f"Conversa com {len(conversation)} mensagens.")
        conversation[:] = conversation[-10:]

    # Sinal de conclusão com texto completo
    yield f"data: {json.dumps({'type': 'done', 'full_text': full_text.strip(), 'model': model_name})}\n\n"


# ─── AUDIO ─────────────────────────────────────────────────────────────────────

async def generate_audio(text: str) -> str:
    """Gera áudio TTS e devolve o caminho do ficheiro temporário."""
    clean = text.replace("**","").replace("*","").replace("#","").replace("`","")
    communicate = edge_tts.Communicate(clean, TTS_VOICE, rate=TTS_RATE)
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    await communicate.save(tmp.name)
    return tmp.name


# ─── ROTAS ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "Mensagem vazia"}), 400

    # Imagens opcionais (array de {data: base64, media_type: "image/jpeg"})
    images = data.get("images", None)
    if images and not isinstance(images, list):
        images = None

    return Response(
        stream_with_context(generate_stream(user_msg, images)),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Texto vazio"}), 400
    try:
        audio_path = asyncio.run(generate_audio(text))
        return send_file(audio_path, mimetype="audio/mpeg", as_attachment=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/memories", methods=["GET"])
def get_memories():
    return jsonify({"memories": mem.read_memory()})


@app.route("/reset", methods=["POST"])
def reset():
    global conversation
    conversation = []
    load_memories_into_context()
    return jsonify({"status": "ok"})


# ─── ARRANQUE ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  JARVIS Interface Web")
    print("  Abre: http://localhost:5000")
    print("="*50 + "\n")

    load_memories_into_context()

    # Inicia scheduler (não bloqueia — BackgroundScheduler)
    try:
        from scheduler import jarvis_scheduler
        jarvis_scheduler.start(call_claude)
    except Exception as e:
        print(f"[Scheduler] Não iniciado: {e}")

    app.run(debug=False, port=5000)
