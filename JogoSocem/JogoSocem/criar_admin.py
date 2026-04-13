"""
criar_admin.py
==============
Corre UMA VEZ para criar a primeira conta de admin.
Depois usa /admin/contas para criar mais contas.

Uso:
    python criar_admin.py
"""

import pyodbc
from auth import hash_password

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=jogo_socem;"
    "UID=GV;"
    "PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)

USERNAME = "admin"       # ← muda aqui se quiseres outro username
PASSWORD = "socem2026"   # ← muda aqui para a password que quiseres

def main():
    hashed = hash_password(PASSWORD)
    try:
        conn   = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()

        # Verifica se já existe
        cursor.execute("SELECT id FROM contas WHERE username = ?", (USERNAME,))
        if cursor.fetchone():
            print(f"AVISO: Conta '{USERNAME}' ja existe. Nada foi alterado.")
            conn.close()
            return

        cursor.execute(
            "INSERT INTO contas (user_id, username, password_hash, tipo) VALUES (?, ?, ?, ?)",
            (None, USERNAME, hashed, "admin")
        )
        conn.commit()
        conn.close()
        print("OK - Conta admin criada com sucesso!")
        print(f"    Username : {USERNAME}")
        print(f"    Password : {PASSWORD}")
        print("")
        print("    Podes agora entrar em http://localhost:8000/login")
        print("    Depois cria mais contas em /admin/contas")

    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    main()
