"""criar_bd.py
Cria a base de dados 'jogo_idonics' no servidor 192.168.10.156
e todas as tabelas necessárias.
Executar UMA vez antes de arrancar a aplicação.
"""
import pyodbc

# Ligação ao master para criar a BD
STR_MASTER = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=master;"
    "UID=GV;"
    "PWD=NovaSenhaForte987;"
    "TrustServerCertificate=yes;"
)


def criar_base_dados():
    """Cria a base de dados jogo_idonics se não existir."""
    # autocommit=True é obrigatório para CREATE DATABASE fora de transacção
    conn = pyodbc.connect(STR_MASTER, timeout=10, autocommit=True)
    c = conn.cursor()
    c.execute("""
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'jogo_idonics')
            CREATE DATABASE jogo_idonics
    """)
    conn.close()
    print("Base de dados 'jogo_idonics' criada/verificada.")


if __name__ == "__main__":
    print("=== Configuração inicial — JogoIDOnics ===\n")

    criar_base_dados()

    # Importar e criar tabelas (já liga à jogo_idonics)
    from base_dados import criar_tabelas
    criar_tabelas()

    print("\nPronto. Executa agora: python criar_admin.py")
