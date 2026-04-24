"""
auth.py — Autenticação do JogoScore
=====================================
Gestão de sessões via cookie assinado (itsdangerous).
Hash de passwords com bcrypt directo (sem passlib — incompatível com bcrypt 4.x).

A sessão guarda:
  conta_id               → ID na tabela jogo_score.contas
  username               → nome de utilizador
  tipo                   → 'admin' ou 'user'
  sinex_user_id          → ID em jogo_socem.users (None se não tiver)
  idontime_colaborador_id → ID em jogo_idonics.colaboradores (None se não tiver)

Instalar:
    pip install bcrypt itsdangerous
"""

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import bcrypt
from fastapi import Request
from typing import Optional

# ─── Configuração ────────────────────────────────────────────────────────────
SECRET_KEY      = "jogoscore-socem-2026-secret-xK9m"  # Mudar em produção!
SESSION_COOKIE  = "jssession"
SESSION_MAX_AGE = 28800   # 8 horas em segundos

# ─── Serializer de sessões ────────────────────────────────────────────────────
serializer = URLSafeTimedSerializer(SECRET_KEY)


# ─── Passwords (bcrypt directo — compatível com bcrypt 4.x) ──────────────────

def hash_password(plain: str) -> str:
    """Gera hash bcrypt da password em texto simples."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica password em texto simples contra o hash guardado."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ─── Sessões ─────────────────────────────────────────────────────────────────

def create_session_token(data: dict) -> str:
    """Serializa e assina os dados da sessão para guardar no cookie."""
    return serializer.dumps(data)


def get_session_user(request: Request) -> Optional[dict]:
    """
    Lê e valida o cookie de sessão.

    Devolve dict com:
      {
        conta_id, username, tipo,
        sinex_user_id,           ← None se não tiver SINEX
        idontime_colaborador_id  ← None se não tiver IDOntime
      }
    Devolve None se cookie inválido ou expirado.
    """
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    try:
        return serializer.loads(token, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
