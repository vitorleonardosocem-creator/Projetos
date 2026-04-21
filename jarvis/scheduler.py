"""
JARVIS Scheduler — tarefas agendadas com APScheduler.
Cada tarefa tem: id, name, cron_expression, command, active.
As tarefas são persistidas em jarvis_scheduled.json.
"""
from __future__ import annotations
import json
import os
import uuid
import re
from datetime import datetime

_SCHEDULE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_scheduled.json")


# ── Natural language → cron ────────────────────────────────────────────────────

def _nl_to_cron(text: str) -> str | None:
    """Converte linguagem natural simples para expressão cron.
    Devolve None se não conseguir interpretar."""
    t = text.lower().strip()

    # Intervalos simples
    if re.search(r"(de hora a hora|every hour|hourly|cada hora)", t):
        return "0 * * * *"
    if re.search(r"(de 30 em 30|every 30 min|cada 30)", t):
        return "*/30 * * * *"
    if re.search(r"(de 15 em 15|every 15 min|cada 15)", t):
        return "*/15 * * * *"
    if re.search(r"(de 10 em 10|every 10 min|cada 10)", t):
        return "*/10 * * * *"
    if re.search(r"(de 5 em 5|every 5 min|cada 5)", t):
        return "*/5 * * * *"
    if re.search(r"(every minute|cada minuto)", t):
        return "* * * * *"

    # Dias da semana específicos com hora
    weekday_map = {
        "segunda": 1, "monday": 1,
        "terça": 2, "tuesday": 2,
        "quarta": 3, "wednesday": 3,
        "quinta": 4, "thursday": 4,
        "sexta": 5, "friday": 5,
        "sábado": 6, "saturday": 6,
        "domingo": 0, "sunday": 0,
    }
    for day_name, day_num in weekday_map.items():
        if day_name in t:
            hour = _extract_hour(t)
            if hour is not None:
                return f"0 {hour} * * {day_num}"
            return f"0 9 * * {day_num}"  # padrão 9h

    # Todos os dias com hora
    if re.search(r"(todos os dias|every day|daily|diariamente|cada dia)", t):
        hour = _extract_hour(t)
        if hour is not None:
            return f"0 {hour} * * *"
        return "0 8 * * *"  # padrão 8h

    # Hora simples (assume todos os dias)
    hour = _extract_hour(t)
    if hour is not None:
        return f"0 {hour} * * *"

    return None


def _extract_hour(text: str) -> int | None:
    """Extrai a hora de uma string de texto."""
    # "às 8h", "at 8am", "8:00", "08h00", "8h30" (só a hora)
    m = re.search(r"(\d{1,2})[h:](\d{2})?(?:\s*h)?", text)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d{1,2})\s*am", text)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d{1,2})\s*pm", text)
    if m:
        h = int(m.group(1))
        return h + 12 if h < 12 else h
    return None


# ── Persistência ───────────────────────────────────────────────────────────────

def _load_tasks() -> list[dict]:
    if os.path.exists(_SCHEDULE_FILE):
        try:
            with open(_SCHEDULE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_tasks(tasks: list[dict]) -> None:
    with open(_SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


# ── Scheduler ─────────────────────────────────────────────────────────────────

class JarvisScheduler:
    def __init__(self) -> None:
        self._scheduler = None
        self._call_claude_fn = None  # injected from app.py

    def start(self, call_claude_fn) -> None:
        """Inicia o scheduler. call_claude_fn é a função call_claude de app.py."""
        self._call_claude_fn = call_claude_fn
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger
            self._scheduler = BackgroundScheduler(daemon=True)
            self._scheduler.start()
            # Carrega tarefas guardadas
            for task in _load_tasks():
                if task.get("active", True):
                    self._add_job(task)
            print(f"[JARVIS Scheduler] Iniciado com {len(_load_tasks())} tarefa(s) carregada(s).")
        except ImportError:
            print("[JARVIS Scheduler] APScheduler não instalado. Tarefas agendadas desativadas.")
            print("  Instala com: pip install apscheduler")
        except Exception as e:
            print(f"[JARVIS Scheduler] Erro ao iniciar: {e}")

    def _add_job(self, task: dict) -> None:
        """Adiciona um job ao APScheduler."""
        if self._scheduler is None:
            return
        try:
            from apscheduler.triggers.cron import CronTrigger
            cron_parts = task["cron_expression"].split()
            if len(cron_parts) == 5:
                minute, hour, day, month, day_of_week = cron_parts
            else:
                return
            trigger = CronTrigger(
                minute=minute, hour=hour, day=day,
                month=month, day_of_week=day_of_week
            )
            self._scheduler.add_job(
                func=self._fire_task,
                trigger=trigger,
                args=[task["id"], task["command"]],
                id=task["id"],
                replace_existing=True
            )
        except Exception as e:
            print(f"[JARVIS Scheduler] Erro ao adicionar job '{task.get('name')}': {e}")

    def _remove_job(self, task_id: str) -> None:
        if self._scheduler is None:
            return
        try:
            self._scheduler.remove_job(task_id)
        except Exception:
            pass

    def _fire_task(self, task_id: str, command: str) -> None:
        """Chamado pelo APScheduler quando a tarefa dispara."""
        print(f"[JARVIS Scheduler] Tarefa '{task_id}' disparada: {command}")
        if self._call_claude_fn:
            try:
                reply, _ = self._call_claude_fn(f"[TAREFA AGENDADA] {command}")
                print(f"[JARVIS Scheduler] Resposta: {reply[:100]}...")
            except Exception as e:
                print(f"[JARVIS Scheduler] Erro ao executar tarefa: {e}")

    # ── API pública ────────────────────────────────────────────────────────────

    def create_task(self, name: str, cron_or_nl: str, command: str) -> str:
        """Cria uma nova tarefa agendada."""
        # Determina se é cron ou linguagem natural
        parts = cron_or_nl.strip().split()
        if len(parts) == 5 and all(
            re.match(r'^[\d\*\/\-,]+$', p) for p in parts
        ):
            cron_expr = cron_or_nl.strip()
        else:
            cron_expr = _nl_to_cron(cron_or_nl)
            if cron_expr is None:
                return (
                    f"Não consegui interpretar '{cron_or_nl}' como horário.\n"
                    "Exemplos: 'todos os dias às 8h', 'de hora a hora', "
                    "'às segundas às 9h', ou usa cron direto: '0 8 * * *'"
                )

        task = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "cron_expression": cron_expr,
            "command": command,
            "active": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        tasks = _load_tasks()
        tasks.append(task)
        _save_tasks(tasks)
        self._add_job(task)
        return (
            f"Tarefa agendada com sucesso!\n"
            f"ID: {task['id']} | Nome: {name}\n"
            f"Cron: {cron_expr} | Comando: {command}"
        )

    def list_tasks(self) -> str:
        tasks = _load_tasks()
        if not tasks:
            return "Nenhuma tarefa agendada. Usa schedule_task para criar uma."
        lines = [f"Tarefas agendadas ({len(tasks)}):\n"]
        for t in tasks:
            status = "✅ ativa" if t.get("active", True) else "⏸ inativa"
            lines.append(
                f"[{t['id']}] {t['name']} — {t['cron_expression']}\n"
                f"   Comando: {t['command']}\n"
                f"   Estado: {status}"
            )
        return "\n\n".join(lines)

    def delete_task(self, id_or_name: str) -> str:
        tasks = _load_tasks()
        original_len = len(tasks)
        found = None
        for t in tasks:
            if t["id"] == id_or_name or t["name"].lower() == id_or_name.lower():
                found = t
                break
        if not found:
            return f"Tarefa '{id_or_name}' não encontrada."
        tasks = [t for t in tasks if t["id"] != found["id"]]
        _save_tasks(tasks)
        self._remove_job(found["id"])
        return f"Tarefa '{found['name']}' (ID: {found['id']}) removida."

    def toggle_task(self, id_or_name: str) -> str:
        tasks = _load_tasks()
        for t in tasks:
            if t["id"] == id_or_name or t["name"].lower() == id_or_name.lower():
                t["active"] = not t.get("active", True)
                _save_tasks(tasks)
                if t["active"]:
                    self._add_job(t)
                    return f"Tarefa '{t['name']}' ativada."
                else:
                    self._remove_job(t["id"])
                    return f"Tarefa '{t['name']}' pausada."
        return f"Tarefa '{id_or_name}' não encontrada."


# Instância global
jarvis_scheduler = JarvisScheduler()
