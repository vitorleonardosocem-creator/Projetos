"""auth.py
Autenticação e protecção de rotas.
"""
import bcrypt
from functools import wraps
from flask import session, redirect, url_for


def hash_senha(senha: str) -> str:
    """Gera hash bcrypt da senha."""
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, hash_guardado: str) -> bool:
    """Verifica senha contra o hash guardado."""
    return bcrypt.checkpw(senha.encode(), hash_guardado.encode())


def login_obrigatorio(f):
    """Decorador: redireciona para /login se não autenticado."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "utilizador" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper
