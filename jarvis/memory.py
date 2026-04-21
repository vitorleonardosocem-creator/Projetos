from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path
from config import MEMORY_FILE, OBSIDIAN_VAULT, OBSIDIAN_JARVIS_FOLDER, OBSIDIAN_MEMORY_NOTE


# ── Caminho da nota de memórias no Obsidian ─────────────────────────────────────
_OBS_DIR  = Path(OBSIDIAN_VAULT) / OBSIDIAN_JARVIS_FOLDER
_OBS_NOTE = _OBS_DIR / OBSIDIAN_MEMORY_NOTE


# ── JSON helpers ────────────────────────────────────────────────────────────────

def _load() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {"facts": [], "preferences": [], "commands": [], "history_summary": ""}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    _sync_to_obsidian(data)   # sincroniza sempre após guardar


# ── Obsidian sync ────────────────────────────────────────────────────────────────

def _sync_to_obsidian(data: dict):
    """Escreve/atualiza JARVIS/Memórias.md no vault do Obsidian."""
    try:
        _OBS_DIR.mkdir(parents=True, exist_ok=True)

        lines = [
            "# Memórias JARVIS",
            f"*Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
        ]

        if data.get("facts"):
            lines += ["## Factos", ""]
            for e in data["facts"]:
                lines.append(f"- {e['content']}")
            lines.append("")

        if data.get("preferences"):
            lines += ["## Preferências", ""]
            for e in data["preferences"]:
                lines.append(f"- {e['content']}")
            lines.append("")

        if data.get("commands"):
            lines += ["## Comandos Personalizados", ""]
            for e in data["commands"]:
                lines.append(f"- {e['content']}")
            lines.append("")

        if data.get("history_summary"):
            lines += ["## Resumo do Histórico", "", data["history_summary"], ""]

        _OBS_NOTE.write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:
        print(f"[Memory] Erro ao sincronizar com Obsidian: {e}")


def read_obsidian_extra() -> str:
    """
    Lê notas adicionais da pasta JARVIS/ no Obsidian (excluindo Memórias.md).
    Permite ao utilizador adicionar notas manualmente que o JARVIS lerá no arranque.
    """
    try:
        if not _OBS_DIR.exists():
            return ""
        extra_parts = []
        for md_file in sorted(_OBS_DIR.glob("*.md")):
            if md_file.name == OBSIDIAN_MEMORY_NOTE:
                continue   # Memórias.md é gerido automaticamente
            content = md_file.read_text(encoding="utf-8").strip()
            if content:
                extra_parts.append(f"[Nota Obsidian: {md_file.stem}]\n{content}")
        return "\n\n".join(extra_parts)
    except Exception as e:
        print(f"[Memory] Erro ao ler notas Obsidian: {e}")
        return ""


# ── API pública ──────────────────────────────────────────────────────────────────

def save_memory(category: str, content: str) -> str:
    """Guarda uma memória numa categoria (facts, preferences, commands)."""
    data = _load()
    valid = {"facts", "preferences", "commands"}
    if category not in valid:
        category = "facts"

    entry = {
        "content": content,
        "saved_at": datetime.now().isoformat(timespec="seconds")
    }
    data[category].append(entry)
    _save(data)   # _save já chama _sync_to_obsidian
    return f"Memorizado em '{category}': {content}"


def read_memory() -> str:
    """Lê todas as memórias guardadas."""
    data = _load()
    parts = []

    if data.get("facts"):
        parts.append("FACTOS GUARDADOS:")
        for e in data["facts"]:
            parts.append(f"  - {e['content']} (guardado em {e['saved_at']})")

    if data.get("preferences"):
        parts.append("PREFERÊNCIAS:")
        for e in data["preferences"]:
            parts.append(f"  - {e['content']}")

    if data.get("commands"):
        parts.append("COMANDOS PERSONALIZADOS:")
        for e in data["commands"]:
            parts.append(f"  - {e['content']}")

    if data.get("history_summary"):
        parts.append(f"RESUMO HISTÓRICO: {data['history_summary']}")

    if not parts:
        return "Nenhuma memória guardada ainda."

    return "\n".join(parts)


def delete_memory(category: str, index: int) -> str:
    """Remove uma memória pelo índice."""
    data = _load()
    if category not in data or not isinstance(data[category], list):
        return "Categoria não encontrada."
    if index < 0 or index >= len(data[category]):
        return "Índice inválido."
    removed = data[category].pop(index)
    _save(data)
    return f"Removido: {removed['content']}"


def update_history_summary(summary: str):
    """Atualiza o resumo do histórico da conversa."""
    data = _load()
    data["history_summary"] = summary
    _save(data)
