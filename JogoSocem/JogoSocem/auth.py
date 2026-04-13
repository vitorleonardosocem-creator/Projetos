"""
auth.py — Autenticação do WorkScore SOCEM
==========================================
Gestão de sessões via cookie assinado (itsdangerous).
Hash de passwords com bcrypt (passlib).

Instalar:
    pip install passlib[bcrypt] itsdangerous
"""

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from passlib.context import CryptContext
from fastapi import Request
from typing import Optional

# ─── Configuração ───────────────────────────────────────────────
SECRET_KEY      = "workscore-socem-jogo-2026-secret-xK9m"   # muda em produção!
SESSION_COOKIE  = "wssession"
SESSION_MAX_AGE = 28800   # 8 horas em segundos

# ─── Ferramentas ────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer  = URLSafeTimedSerializer(SECRET_KEY)


# ─── Passwords ──────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Gera hash bcrypt da password em texto simples."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica password em texto simples contra o hash guardado."""
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


# ─── Sessões ────────────────────────────────────────────────────

def create_session_token(data: dict) -> str:
    """Serializa e assina os dados da sessão para guardar no cookie."""
    return serializer.dumps(data)


def get_session_user(request: Request) -> Optional[dict]:
    """
    Lê e valida o cookie de sessão.
    Devolve dict com {conta_id, user_id, username, tipo} ou None.
    """
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    try:
        return serializer.loads(token, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
