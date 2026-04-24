import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

"""
criar_bd.py — Preparação da Base de Dados JogoScore
=====================================================
Este script deve ser corrido UMA VEZ antes de arrancar o JogoScore.

O que faz:
  1. Cria a BD 'jogo_score' no servidor 192.168.10.156
     → Tabela 'contas' unificada (login para todos os utilizadores)

  2. Estende a tabela 'resgates' na BD 'jogo_socem'
     → Adiciona colunas para suportar utilizadores IDOntime e desconto proporcional

Ligar como: GV / NovaSenhaForte987

Executar:
    python criar_bd.py
"""

import pyodbc

# ─── Ligação ao servidor (sem BD — para criar a jogo_score) ───────────────────
CONN_SERVIDOR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "UID=GV;"
    "PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)

# ─── Ligação à BD jogo_socem (para extender a tabela resgates) ────────────────
CONN_JOGO_SOCEM = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=jogo_socem;"
    "UID=GV;"
    "PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)

# ─── Ligação à BD jogo_score (criada neste script) ───────────────────────────
CONN_JOGO_SCORE = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=jogo_score;"
    "UID=GV;"
    "PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)


def criar_bd_jogo_score():
    """
    Cria a base de dados 'jogo_score' se ainda não existir.
    É necessário ligar sem BD especificada para poder criar a BD.
    """
    print("─── Passo 1: Criar BD jogo_score ───────────────────────────────────────────")
    # autocommit=True é necessário para CREATE DATABASE (não pode estar dentro de transação)
    conn = pyodbc.connect(CONN_SERVIDOR, autocommit=True)
    cursor = conn.cursor()

    cursor.execute("""
        IF NOT EXISTS (
            SELECT name FROM sys.databases WHERE name = 'jogo_score'
        )
        CREATE DATABASE jogo_score
    """)
    print("  ✅ BD 'jogo_score' criada (ou já existia).")
    conn.close()


def criar_tabela_contas():
    """
    Cria a tabela 'contas' unificada na BD jogo_score.

    Colunas:
      sinex_user_id         → FK para jogo_socem.users.id  (NULL se só IDOntime)
      idontime_colaborador_id → FK para jogo_idonics.colaboradores.id (NULL se só SINEX)

    Um utilizador pode ter ambos preenchidos → login combinado com pontos somados.
    """
    print("─── Passo 2: Criar tabela contas ────────────────────────────────────────────")
    conn = pyodbc.connect(CONN_JOGO_SCORE)
    cursor = conn.cursor()

    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sysobjects WHERE name = 'contas' AND xtype = 'U'
        )
        CREATE TABLE contas (
            id                      INT IDENTITY(1,1) PRIMARY KEY,
            username                NVARCHAR(50)  NOT NULL UNIQUE,
            password_hash           NVARCHAR(200) NOT NULL,
            tipo                    NVARCHAR(20)  DEFAULT 'admin',
            sinex_user_id           INT           NULL,
            idontime_colaborador_id INT           NULL
        )
    """)
    conn.commit()
    print("  ✅ Tabela 'contas' criada (ou já existia).")
    conn.close()


def extender_resgates():
    """
    Adiciona colunas à tabela 'resgates' na BD jogo_socem para suportar:
      - Utilizadores IDOntime (user_id pode ser NULL, usa idontime_colaborador_id)
      - Desconto proporcional (pontos_gastos_idontime para a parte IDOntime)

    Não altera dados existentes — colunas nullable, valor NULL = registo antigo SINEX.
    """
    print("─── Passo 3: Estender tabela resgates em jogo_socem ─────────────────────────")
    conn = pyodbc.connect(CONN_JOGO_SOCEM)
    cursor = conn.cursor()

    # Coluna para ID do colaborador IDOntime (NULL para utilizadores SINEX puros)
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.columns
            WHERE object_id = OBJECT_ID('resgates')
              AND name = 'idontime_colaborador_id'
        )
        ALTER TABLE resgates ADD idontime_colaborador_id INT NULL
    """)
    print("  ✅ Coluna 'idontime_colaborador_id' adicionada a resgates (ou já existia).")

    # Coluna para pontos descontados do lado IDOntime (para utilizadores combinados)
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sys.columns
            WHERE object_id = OBJECT_ID('resgates')
              AND name = 'pontos_gastos_idontime'
        )
        ALTER TABLE resgates ADD pontos_gastos_idontime INT NULL DEFAULT 0
    """)
    print("  ✅ Coluna 'pontos_gastos_idontime' adicionada a resgates (ou já existia).")

    # Permite user_id NULL (para utilizadores IDOntime puros)
    # Nota: só executa se ainda não for nullable (verificação via sys.columns)
    cursor.execute("""
        SELECT is_nullable FROM sys.columns
        WHERE object_id = OBJECT_ID('resgates') AND name = 'user_id'
    """)
    row = cursor.fetchone()
    if row and not row[0]:
        # user_id ainda é NOT NULL — torna nullable
        cursor.execute("ALTER TABLE resgates ALTER COLUMN user_id INT NULL")
        print("  ✅ Coluna 'user_id' de resgates tornada nullable.")
    else:
        print("  ✅ Coluna 'user_id' já é nullable (ou não existe).")

    conn.commit()
    conn.close()


def verificar_resultado():
    """Mostra um resumo do que foi criado para confirmar."""
    print("─── Verificação Final ────────────────────────────────────────────────────────")
    conn = pyodbc.connect(CONN_JOGO_SCORE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM contas")
    total_contas = cursor.fetchone()[0]
    conn.close()

    conn2 = pyodbc.connect(CONN_JOGO_SOCEM)
    cursor2 = conn2.cursor()
    cursor2.execute("""
        SELECT name FROM sys.columns
        WHERE object_id = OBJECT_ID('resgates')
          AND name IN ('idontime_colaborador_id', 'pontos_gastos_idontime')
    """)
    colunas = [r[0] for r in cursor2.fetchall()]
    conn2.close()

    print(f"  jogo_score.contas: {total_contas} conta(s) registada(s).")
    print(f"  jogo_socem.resgates: colunas extras → {', '.join(colunas) or 'nenhuma encontrada'}")
    print()
    print("  ✅ Tudo pronto! Corre agora: python criar_admin.py")


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  JogoScore — Preparação da Base de Dados")
    print("=" * 60)
    print()

    try:
        criar_bd_jogo_score()
        criar_tabela_contas()
        extender_resgates()
        verificar_resultado()
    except Exception as e:
        print(f"\n  ❌ ERRO: {e}")
        raise
