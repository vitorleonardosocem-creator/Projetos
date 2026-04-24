import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

"""
criar_admin.py — Criar conta de administrador inicial
======================================================
Corre UMA VEZ após criar_bd.py.

Cria uma conta admin na BD jogo_score.contas.
Esta conta dá acesso ao painel de administração do JogoScore.

Executar:
    python criar_admin.py
"""

import pyodbc
from auth import hash_password

# ─── Credenciais da conta admin inicial ──────────────────────────────────────
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "socem2026"

# ─── Ligação à BD jogo_score ─────────────────────────────────────────────────
CONN_JOGO_SCORE = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=jogo_score;"
    "UID=GV;"
    "PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)


def criar_conta_admin():
    conn = pyodbc.connect(CONN_JOGO_SCORE)
    cursor = conn.cursor()

    # Verificar se já existe
    cursor.execute(
        "SELECT id FROM contas WHERE username = ?",
        (ADMIN_USERNAME,)
    )
    if cursor.fetchone():
        print(f"  ⚠️  Conta '{ADMIN_USERNAME}' já existe — nada a fazer.")
        conn.close()
        return

    # Criar conta admin (sem user SINEX nem IDOntime associado)
    hashed = hash_password(ADMIN_PASSWORD)
    cursor.execute(
        """
        INSERT INTO contas (username, password_hash, tipo, sinex_user_id, idontime_colaborador_id)
        VALUES (?, ?, 'admin', NULL, NULL)
        """,
        (ADMIN_USERNAME, hashed)
    )
    conn.commit()
    conn.close()

    print(f"  ✅ Conta admin criada com sucesso!")
    print(f"     Username: {ADMIN_USERNAME}")
    print(f"     Password: {ADMIN_PASSWORD}")
    print()
    print("  ⚠️  Muda a password após o primeiro login!")


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  JogoScore — Criar Admin Inicial")
    print("=" * 60)
    print()
    try:
        criar_conta_admin()
    except Exception as e:
        print(f"  ❌ ERRO: {e}")
        raise
