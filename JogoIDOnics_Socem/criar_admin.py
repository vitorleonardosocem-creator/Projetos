"""criar_admin.py
Cria a conta de administrador inicial.
Executar UMA vez após criar_bd.py.
"""
from base_dados import ligar_jogo
from auth import hash_senha

UTILIZADOR = "admin"
SENHA      = "Admin2026!"   # Muda antes de usar em produção


def criar_admin():
    conn = ligar_jogo()
    c = conn.cursor()

    # Verificar se já existe
    c.execute("SELECT COUNT(*) FROM contas WHERE username = ?", UTILIZADOR)
    if c.fetchone()[0] > 0:
        print(f"Conta '{UTILIZADOR}' já existe. Nenhuma alteração feita.")
        conn.close()
        return

    h = hash_senha(SENHA)
    c.execute(
        "INSERT INTO contas (username, password_hash, tipo) VALUES (?, ?, 'admin')",
        UTILIZADOR, h
    )
    conn.commit()
    conn.close()
    print(f"Conta criada com sucesso.")
    print(f"  Utilizador : {UTILIZADOR}")
    print(f"  Senha      : {SENHA}")
    print(f"\nAltera a senha após o primeiro acesso!")


if __name__ == "__main__":
    criar_admin()
