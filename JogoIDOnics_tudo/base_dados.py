"""base_dados.py
Ligações às bases de dados e criação de tabelas.
"""
import pyodbc

# BD do jogo (192.168.10.156)
STR_JOGO = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=jogo_idonics;"
    "UID=GV;"
    "PWD=NovaSenhaForte987;"
    "TrustServerCertificate=yes;"
)

# IDOnics — só leitura (192.168.31.241)
STR_IDONICS = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.31.241;"
    "DATABASE=idonicsys_socem;"
    "UID=ReadOnly;"
    "PWD=R3ad0nly2026;"
    "TrustServerCertificate=yes;"
)


def ligar_jogo():
    """Abre ligação à BD do jogo."""
    return pyodbc.connect(STR_JOGO, timeout=10)


def ligar_idonics():
    """Abre ligação ao IDOnics (só leitura)."""
    return pyodbc.connect(STR_IDONICS, timeout=10)


def criar_tabelas():
    """Cria as tabelas necessárias se ainda não existirem."""
    conn = ligar_jogo()
    c = conn.cursor()

    c.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='departamentos' AND xtype='U')
        CREATE TABLE departamentos (
            id   INT           PRIMARY KEY,
            nome NVARCHAR(100) NOT NULL
        )
    """)

    c.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='colaboradores' AND xtype='U')
        CREATE TABLE colaboradores (
            id              INT           PRIMARY KEY,
            nome            NVARCHAR(200),
            nome_disp       NVARCHAR(100),
            numero          NVARCHAR(20),
            id_departamento INT,
            activo          BIT           DEFAULT 1,
            pontos_total    INT           DEFAULT 0,
            data_sync       DATETIME      DEFAULT GETDATE()
        )
    """)

    c.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pontos' AND xtype='U')
        CREATE TABLE pontos (
            id             INT IDENTITY(1,1) PRIMARY KEY,
            id_colaborador INT           NOT NULL,
            tarefa         NVARCHAR(100) NOT NULL,
            pontos         INT           NOT NULL,
            data_pontos    DATETIME      DEFAULT GETDATE(),
            obs            NVARCHAR(500),
            CONSTRAINT uq_colab_tarefa UNIQUE (id_colaborador, tarefa)
        )
    """)

    c.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='processamentos' AND xtype='U')
        CREATE TABLE processamentos (
            id             INT IDENTITY(1,1) PRIMARY KEY,
            data_ini       DATE     NOT NULL,
            data_fim       DATE     NOT NULL,
            total_registos INT      DEFAULT 0,
            data_execucao  DATETIME DEFAULT GETDATE(),
            obs            NVARCHAR(500)
        )
    """)

    c.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='contas' AND xtype='U')
        CREATE TABLE contas (
            id            INT IDENTITY(1,1) PRIMARY KEY,
            username      NVARCHAR(50)  NOT NULL UNIQUE,
            password_hash NVARCHAR(200) NOT NULL,
            tipo          NVARCHAR(20)  DEFAULT 'admin'
        )
    """)

    conn.commit()
    conn.close()
    print("Tabelas criadas/verificadas com sucesso.")
