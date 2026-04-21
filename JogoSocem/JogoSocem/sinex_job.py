"""
=============================================================
  sinex_job.py  —  Job Diário SINEX → jogo_socem
=============================================================

  REGRAS DE PONTUAÇÃO:
  ┌─────────────────────────────────────────────────────────┐
  │  POR DIA (seg-sex, excluindo feriados):                 │
  │    < 7.2h               →  -1  (saiu cedo)             │
  │    >= 7.2h e <= 9.2h    →  +1  (cumpriu ✅)            │
  │    > 9.2h               →  -1  (logout esquecido)      │
  │    Finish NULL           →  -1  (não fez logout)        │
  │    sem registo           →   0  (folga, neutro)         │
  │                                                         │
  │  BÓNUS SEMANAL (calculado às segundas):                 │
  │    5 dias úteis todos com +1  →  +1 extra              │
  └─────────────────────────────────────────────────────────┘

  CORREÇÕES aplicadas:
  1. EmployeeID usado para identificar colaboradores
     → dois nomes iguais em secções diferentes = pessoas distintas
  2. Finish NULL → -1 automático (sem cálculo de horas)
  3. Soma de horas arredondada a 2 casas antes de comparar
     → evita erros de float (ex: 7.1999999 a ser tratado como 7.2)

  Anti-duplicação: tabela 'pontos' com tarefa='sinex_YYYY-MM-DD'

  Instalar dependências:
      pip install pyodbc pandas holidays

=============================================================
"""

import pyodbc
import pandas as pd
import logging
from datetime import date, timedelta
from typing import Optional

try:
    import holidays as holidays_lib
    HAS_HOLIDAYS = True
except ImportError:
    HAS_HOLIDAYS = False
    print("AVISO: biblioteca 'holidays' nao instalada. Usar: pip install holidays")


# ─────────────────────────────────────────────
#  LOGGING (stdout — capturado pelo BAT via >>)
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  LIGAÇÕES
# ─────────────────────────────────────────────

SINEX_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.120\\SQLEXPRESS;"
    "DATABASE=Sinex;"
    "UID=sa;"
    "PWD=Des@nh0!2016;"
    "TrustServerCertificate=Yes;"
    "Encrypt=no;"
)

JOGO_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=jogo_socem;"
    "UID=GV;"
    "PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)


# ─────────────────────────────────────────────
#  REGRAS
# ─────────────────────────────────────────────

HORAS_MIN = 7.2   # abaixo disto → -1
HORAS_MAX = 9.2   # acima disto  → -1


# ─────────────────────────────────────────────
#  FERIADOS — Portugal + Alcobaça (20 Ago)
# ─────────────────────────────────────────────

_feriados_cache: dict = {}


def get_feriados(ano: int) -> set:
    if ano in _feriados_cache:
        return _feriados_cache[ano]

    feriados = set()
    if HAS_HOLIDAYS:
        pt = holidays_lib.Portugal(years=ano)
        feriados.update(pt.keys())
    else:
        feriados.update([
            date(ano, 1, 1), date(ano, 4, 25), date(ano, 5, 1),
            date(ano, 6, 10), date(ano, 8, 15), date(ano, 10, 5),
            date(ano, 11, 1), date(ano, 12, 1), date(ano, 12, 8),
            date(ano, 12, 25),
        ])

    feriados.add(date(ano, 8, 20))  # Alcobaça municipal
    _feriados_cache[ano] = feriados
    return feriados


def is_dia_util(d: date) -> bool:
    if d.weekday() >= 5:
        return False
    return d not in get_feriados(d.year)


# ─────────────────────────────────────────────
#  QUERY SINEX
#  CORREÇÃO 1: inclui EmployeeID para identificar
#              cada trabalhador de forma única.
#  CORREÇÃO 2: Finish_Null = 1 quando Finish é NULL
#              → Python dá -1 automático, sem usar GETDATE().
#              Horas_Registo usa ISNULL(Finish, Start) = 0h
#              para linhas sem logout (valor ignorado pelo Python).
# ─────────────────────────────────────────────

def get_query(data_inicio: str, data_fim: str) -> str:
    return f"""
    SELECT
        p.EmployeeID                                  AS EmployeeID,
        e.WorkName                                    AS Operador,
        CAST(p.Start AS DATE)                         AS Data,
        ISNULL(c.Name, 'Sem Seccao')                  AS Seccao,
        CASE WHEN p.Finish IS NULL THEN 1 ELSE 0 END  AS Finish_Null,
        CAST(
            (DATEDIFF(ss, p.Start, ISNULL(p.Finish, p.Start)) / 3600.0)
        AS DECIMAL(10,2))                             AS Horas_Registo

    FROM dbo.DATPRD_Production       AS p
    LEFT JOIN dbo.TABPRD_Unique      AS u ON u.UniqueID       = p.UniqueID
    LEFT JOIN dbo.TABOBJ_Workstation AS s ON s.WorkstationID  = p.WorkstationID
    LEFT JOIN dbo.TABOBJ_Workgroup   AS g ON g.WorkgroupID    = s.WorkgroupID
    LEFT JOIN dbo.TABOBJ_Section     AS c ON c.SectionID      = g.SectionID
    LEFT JOIN dbo.TABOBJ_Sector      AS r ON r.SectorID       = c.SectorID
    LEFT JOIN dbo.TABOBJ_Employee    AS e ON e.EmployeeID     = p.EmployeeID

    WHERE p.Start      >= '{data_inicio}'
      AND p.Start      <  '{data_fim}'
      AND p.EmployeeID IS NOT NULL
      AND e.WorkName   IS NOT NULL
      AND e.WorkName   <> ''
    """


# ─────────────────────────────────────────────
#  LÓGICA DE PONTOS
# ─────────────────────────────────────────────

def pontuar_dia(horas: float) -> int:
    """
    CORREÇÃO 3: horas já vêm arredondadas a 2 casas decimais
    antes desta função ser chamada, evitando erros de float
    (ex: 7.1999999 seria tratado como >= 7.2).
    """
    if horas < HORAS_MIN:
        return -1   # saiu cedo
    elif horas > HORAS_MAX:
        return -1   # logout esquecido
    else:
        return 1    # cumpriu


def calcular_pontos_diarios(df: pd.DataFrame, dia_alvo: date) -> tuple:
    """
    Devolve (pontos_dict, seccoes_dict) para o dia_alvo.

    pontos_dict  — chave: (EmployeeID, Operador)
    seccoes_dict — chave: EmployeeID

    CORREÇÃO 1: agrupa por (EmployeeID, Operador).
      → Mesmo nome em departamentos diferentes = pessoas distintas.
      → Mesmo EmployeeID em secções diferentes = mesma pessoa, horas somam-se.

    CORREÇÃO 2: se qualquer sessão do dia tiver Finish NULL → -1 automático.

    CORREÇÃO 3: soma arredondada a 2 casas antes de comparar com limiares.
    """
    if df.empty:
        return {}, {}

    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"]).dt.date
    df_dia = df[df["Data"] == dia_alvo].copy()

    if df_dia.empty:
        return {}, {}

    df_dia["Operador"] = df_dia["Operador"].str.strip()
    df_dia = df_dia[df_dia["Operador"] != ""]
    df_dia["EmployeeID"] = df_dia["EmployeeID"].astype(int)

    # CORREÇÃO 2: detectar se alguma sessão tem Finish NULL por EmployeeID
    null_por_emp = (
        df_dia.groupby("EmployeeID")["Finish_Null"]
        .max()
        .to_dict()
    )

    # CORREÇÃO 1: soma de horas por (EmployeeID, Operador)
    # → mesma pessoa em múltiplas secções soma corretamente
    # → pessoas diferentes com mesmo nome ficam separadas
    horas_por_emp = (
        df_dia.groupby(["EmployeeID", "Operador"])["Horas_Registo"]
        .sum()
        .reset_index()
        .rename(columns={"Horas_Registo": "Horas_Dia"})
    )

    # CORREÇÃO 3: arredondar a 2 casas para evitar erros de float
    # ex: 3.77 + 1.17 + 2.25 em float64 pode dar 7.1999999
    # com round(2) fica 7.19 → correto
    horas_por_emp["Horas_Dia"] = horas_por_emp["Horas_Dia"].round(2)

    # Secção mais frequente por EmployeeID (para associar ao departamento)
    seccoes = (
        df_dia.groupby("EmployeeID")["Seccao"]
        .agg(lambda x: x.value_counts().index[0])
        .to_dict()
    )

    pontos = {}
    for _, row in horas_por_emp.iterrows():
        emp_id   = int(row["EmployeeID"])
        operador = str(row["Operador"])
        key      = (emp_id, operador)

        if null_por_emp.get(emp_id, 0):
            # CORREÇÃO 2: Finish NULL → -1 (não se sabe quando saiu)
            pontos[key] = -1
            log.info(f"    -1  {operador}  [Finish NULL]")
        else:
            pontos[key] = pontuar_dia(float(row["Horas_Dia"]))

    return pontos, seccoes


# ─────────────────────────────────────────────
#  FUNÇÕES JOGO_SOCEM
# ─────────────────────────────────────────────

_dept_cache: dict = {}
_user_cache: dict = {}   # chave: sinex_employee_id (int) → user_id


def garantir_dept(cursor, nome_seccao: str) -> int:
    """Garante que o departamento existe na BD. Usa cache em memória."""
    nome_seccao = nome_seccao.strip() or "Sem Seccao"

    if nome_seccao in _dept_cache:
        return _dept_cache[nome_seccao]

    cursor.execute(
        "SELECT id FROM departamentos WHERE LOWER(nome) = LOWER(?)", (nome_seccao,)
    )
    row = cursor.fetchone()
    if row:
        _dept_cache[nome_seccao] = int(row[0])
        return _dept_cache[nome_seccao]

    cursor.execute(
        "INSERT INTO departamentos (nome) OUTPUT INSERTED.id VALUES (?)", (nome_seccao,)
    )
    new_id = int(cursor.fetchone()[0])
    _dept_cache[nome_seccao] = new_id
    log.info(f"  Dept criado: '{nome_seccao}' (ID {new_id})")
    return new_id


def garantir_utilizador(cursor, nome: str, dept_id: int, emp_id: int) -> int:
    """
    Garante que o utilizador existe na BD.

    USA sinex_employee_id como chave primária de identificação.
    → Dois "João Santos" em departamentos diferentes têm EmployeeIDs
      diferentes no Sinex e ficam como utilizadores separados.

    Lógica:
    1. Procura por sinex_employee_id — caso normal (rápido)
    2. Fallback de migração: procura por (nome, dept_id) sem employee_id
       → atualiza sinex_employee_id no registo existente
    3. Se não encontrar → cria novo utilizador
    """
    nome = nome.strip()

    if emp_id in _user_cache:
        return _user_cache[emp_id]

    # 1. Procura por sinex_employee_id (chave única por pessoa no Sinex)
    cursor.execute(
        "SELECT id FROM users WHERE sinex_employee_id = ?", (emp_id,)
    )
    row = cursor.fetchone()
    if row:
        _user_cache[emp_id] = int(row[0])
        return _user_cache[emp_id]

    # 2. Fallback migração: utilizadores existentes sem sinex_employee_id
    #    (dados carregados antes desta correção)
    cursor.execute(
        "SELECT id FROM users WHERE LOWER(nome) = LOWER(?) "
        "AND departamento_id = ? AND sinex_employee_id IS NULL",
        (nome, dept_id)
    )
    row = cursor.fetchone()
    if row:
        user_id = int(row[0])
        cursor.execute(
            "UPDATE users SET sinex_employee_id = ?, departamento_id = ? WHERE id = ?",
            (emp_id, dept_id, user_id)
        )
        _user_cache[emp_id] = user_id
        log.info(f"  sinex_employee_id atualizado: '{nome}' (empID {emp_id})")
        return user_id

    # 3. Criar novo utilizador
    cursor.execute(
        "INSERT INTO users (nome, departamento_id, sinex_employee_id, pontos_total, ferias_ganhas) "
        "OUTPUT INSERTED.id VALUES (?, ?, ?, 0, 0)",
        (nome, dept_id, emp_id)
    )
    new_id = int(cursor.fetchone()[0])
    _user_cache[emp_id] = new_id
    log.info(f"  Utilizador criado: '{nome}' (dept ID {dept_id}, empID {emp_id})")
    return new_id


def ja_processado(cursor, user_id: int, tarefa: str) -> bool:
    cursor.execute(
        "SELECT COUNT(*) FROM pontos WHERE user_id = ? AND tarefa = ?",
        (user_id, tarefa)
    )
    return cursor.fetchone()[0] > 0


def aplicar_ponto(cursor, conn, user_id: int, nome: str, pontos: int,
                  tarefa: str, data_ref: date) -> bool:
    """
    Insere na tabela pontos + eventos e atualiza users.pontos_total.
    Devolve True se aplicado, False se duplicado.
    """
    if ja_processado(cursor, user_id, tarefa):
        return False

    cursor.execute(
        "INSERT INTO pontos (user_id, tarefa, pontos, data_pontos) VALUES (?, ?, ?, ?)",
        (user_id, tarefa, int(pontos), data_ref)
    )
    cursor.execute(
        "INSERT INTO eventos (user_id, tipo, pontos) VALUES (?, ?, ?)",
        (user_id, tarefa[:100], int(pontos))
    )
    cursor.execute(
        "UPDATE users SET pontos_total = pontos_total + ? WHERE id = ?",
        (int(pontos), user_id)
    )
    conn.commit()
    return True


def recalcular_pontos_total(conn):
    """
    Recalcula users.pontos_total a partir da soma real da tabela pontos.
    Usa INNER JOIN para não tocar em utilizadores sem registos Sinex
    (ex: utilizadores manuais com pontos atribuídos pelo admin).
    """
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE u
        SET u.pontos_total = p.soma
        FROM users u
        INNER JOIN (
            SELECT user_id, SUM(pontos) AS soma
            FROM pontos
            GROUP BY user_id
        ) p ON p.user_id = u.id
    """)
    conn.commit()
    log.info("  pontos_total recalculado com sucesso.")


# ─────────────────────────────────────────────
#  PROCESSAR UM DIA
# ─────────────────────────────────────────────

def processar_dia_na_bd(pontos_dict: dict, seccoes_dict: dict,
                        data_ref: date, conn) -> dict:
    """
    Aplica os pontos de um dia ao jogo_socem.

    pontos_dict  — chave: (EmployeeID, Operador) → pontos
    seccoes_dict — chave: EmployeeID → nome da secção
    """
    cursor    = conn.cursor()
    aplicados = 0
    ignorados = 0
    erros     = []
    tarefa    = f"sinex_{data_ref}"

    for (emp_id, operador), pontos in pontos_dict.items():
        if pontos == 0:
            continue
        try:
            seccao  = seccoes_dict.get(emp_id, "Sem Seccao")
            dept_id = garantir_dept(cursor, seccao)
            user_id = garantir_utilizador(cursor, operador, dept_id, emp_id)
            conn.commit()

            aplicado = aplicar_ponto(cursor, conn, user_id, operador,
                                     pontos, tarefa, data_ref)
            if aplicado:
                sinal = "+" if pontos > 0 else ""
                log.info(f"    {sinal}{pontos}  {operador}  [{seccao}]")
                aplicados += 1
            else:
                log.info(f"  skip  {operador} — ja processado ({tarefa})")
                ignorados += 1

        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            msg = f"{operador}: {e}"
            log.error(f"  ERRO ao processar {msg}")
            erros.append(msg)

    return {"aplicados": aplicados, "ignorados": ignorados, "erros": erros}


# ─────────────────────────────────────────────
#  BÓNUS SEMANAL
# ─────────────────────────────────────────────

def get_dias_uteis_semana(segunda: date, sexta: date) -> list:
    dias = []
    d = segunda
    while d <= sexta:
        if is_dia_util(d):
            dias.append(d)
        d += timedelta(days=1)
    return dias


def processar_bonus_semanal(segunda: date, sexta: date, conn) -> dict:
    """
    Atribui +1 de bónus a quem teve +1 em todos os dias úteis da semana.
    """
    dias_uteis = get_dias_uteis_semana(segunda, sexta)
    tarefa_bonus = f"bonus_semana_{segunda}_{sexta}"

    if len(dias_uteis) < 5:
        log.info(
            f"  Semana {segunda}->{sexta} tem {len(dias_uteis)} dias uteis "
            f"(feriados?) — bonus nao aplicado."
        )
        return {"aplicados": 0, "ignorados": 0}

    tarefas_dia  = [f"sinex_{d}" for d in dias_uteis]
    placeholders = ",".join(["?" for _ in tarefas_dia])
    n_dias       = len(tarefas_dia)

    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT p.user_id, u.nome, u.departamento_id
        FROM pontos p
        INNER JOIN users u ON u.id = p.user_id
        WHERE p.tarefa IN ({placeholders})
          AND p.pontos > 0
        GROUP BY p.user_id, u.nome, u.departamento_id
        HAVING COUNT(DISTINCT p.tarefa) = ?
    """, (*tarefas_dia, n_dias))

    candidatos = cursor.fetchall()
    aplicados  = 0
    ignorados  = 0

    for row in candidatos:
        user_id, nome = int(row[0]), row[1]
        try:
            aplicado = aplicar_ponto(cursor, conn, user_id, nome,
                                     1, tarefa_bonus, sexta)
            if aplicado:
                log.info(f"  Bonus semana completa +1 -> {nome}")
                aplicados += 1
            else:
                log.info(f"  Bonus {nome} ja aplicado — ignorado.")
                ignorados += 1
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            log.error(f"  ERRO bonus {nome}: {e}")

    if aplicados == 0 and ignorados == 0:
        log.info("  Nenhum operador com semana completa.")

    return {"aplicados": aplicados, "ignorados": ignorados}


# ─────────────────────────────────────────────
#  SEMANAS COMPLETAS NUM INTERVALO
# ─────────────────────────────────────────────

def get_semanas_completas(data_inicio: date, data_fim: date) -> list:
    semanas = []
    d = data_inicio
    while d.weekday() != 0:
        d += timedelta(days=1)
    while True:
        segunda = d
        sexta   = d + timedelta(days=4)
        if sexta > data_fim:
            break
        semanas.append((segunda, sexta))
        d += timedelta(days=7)
    return semanas


# ─────────────────────────────────────────────
#  PROCESSAR INTERVALO  (usado pelo job e pela UI)
# ─────────────────────────────────────────────

def processar_intervalo(data_inicio_str: str, data_fim_str: str) -> dict:
    """
    Processa pontos Sinex para todos os dias úteis no intervalo.
    Inclui bónus semanal para semanas completas dentro do intervalo.
    Anti-duplicação via tabela 'pontos'.
    """
    try:
        data_inicio = date.fromisoformat(data_inicio_str)
        data_fim    = date.fromisoformat(data_fim_str)
    except ValueError as e:
        return {"erro_fatal": f"Data invalida: {e}"}

    if data_inicio > data_fim:
        return {"erro_fatal": "Data inicio e posterior a data fim."}

    resultado = {
        "data_inicio": data_inicio_str,
        "data_fim":    data_fim_str,
        "dias":            [],
        "bonus":           [],
        "total_aplicados": 0,
        "total_ignorados": 0,
        "total_erros":     0,
        "erro_fatal":      None,
    }

    dias_uteis = []
    d = data_inicio
    while d <= data_fim:
        if is_dia_util(d):
            dias_uteis.append(d)
        d += timedelta(days=1)

    if not dias_uteis:
        resultado["erro_fatal"] = "Sem dias uteis no intervalo selecionado."
        return resultado

    log.info("=" * 60)
    log.info(f"  REPROCESSAMENTO {data_inicio} -> {data_fim}  ({len(dias_uteis)} dias uteis)")
    log.info("=" * 60)

    # Ler Sinex para todo o intervalo de uma vez
    data_fim_query = str(data_fim + timedelta(days=1))
    try:
        sinex_conn = pyodbc.connect(SINEX_CONN, timeout=30)
        df = pd.read_sql(get_query(data_inicio_str, data_fim_query), sinex_conn)
        sinex_conn.close()
        log.info(f"  {len(df):,} registos lidos do Sinex.")
    except Exception as e:
        log.error(f"  ERRO a ler Sinex: {e}")
        resultado["erro_fatal"] = f"Erro ao ler Sinex: {e}"
        return resultado

    try:
        conn_jogo = pyodbc.connect(JOGO_CONN)
    except Exception as e:
        log.error(f"  ERRO a ligar jogo_socem: {e}")
        resultado["erro_fatal"] = f"Erro ao ligar jogo_socem: {e}"
        return resultado

    try:
        for dia in dias_uteis:
            log.info(f"  {dia} ...")
            pontos_dia, seccoes = calcular_pontos_diarios(df, dia)

            if not pontos_dia:
                log.info(f"  Sem registos Sinex para {dia}.")
                resultado["dias"].append({
                    "data": str(dia), "aplicados": 0,
                    "ignorados": 0, "erros": 0, "sem_dados": True,
                })
                continue

            resumo = processar_dia_na_bd(pontos_dia, seccoes, dia, conn_jogo)
            resultado["dias"].append({
                "data":      str(dia),
                "aplicados": resumo["aplicados"],
                "ignorados": resumo["ignorados"],
                "erros":     len(resumo["erros"]),
                "sem_dados": False,
            })
            resultado["total_aplicados"] += resumo["aplicados"]
            resultado["total_ignorados"] += resumo["ignorados"]
            resultado["total_erros"]     += len(resumo["erros"])

        # Bónus semanal para semanas completas dentro do intervalo
        for segunda, sexta in get_semanas_completas(data_inicio, data_fim):
            log.info(f"  Bonus semana {segunda} -> {sexta} ...")
            res_bonus = processar_bonus_semanal(segunda, sexta, conn_jogo)
            resultado["bonus"].append({
                "semana":    f"{segunda} -> {sexta}",
                "aplicados": res_bonus["aplicados"],
                "ignorados": res_bonus["ignorados"],
            })

        # Recalcular pontos_total (salvaguarda de consistência)
        recalcular_pontos_total(conn_jogo)

    except Exception as e:
        log.error(f"  ERRO inesperado: {e}")
        resultado["erro_fatal"] = str(e)
    finally:
        try:
            conn_jogo.close()
        except Exception:
            pass

    log.info(
        f"  Concluido: {resultado['total_aplicados']} aplicados, "
        f"{resultado['total_ignorados']} ignorados, "
        f"{resultado['total_erros']} erros."
    )
    return resultado


# ─────────────────────────────────────────────
#  JOB PRINCIPAL (Task Scheduler)
# ─────────────────────────────────────────────

def run_job():
    """
    Corre todos os dias via Task Scheduler:
      Seg → processa Sexta passada + bónus semana passada
      Ter → processa Segunda
      Qua → processa Terça
      Qui → processa Quarta
      Sex → processa Quinta
      Sáb/Dom/Feriado → não faz nada
    """
    hoje = date.today()

    if hoje.weekday() >= 5:
        log.info("  Fim de semana — job ignorado.")
        return

    if not is_dia_util(hoje):
        log.info(f"  {hoje} e feriado — job ignorado.")
        return

    if hoje.weekday() == 0:
        dia_a_processar = hoje - timedelta(days=3)
        segunda_passada = hoje - timedelta(days=7)
        sexta_passada   = hoje - timedelta(days=3)
    else:
        dia_a_processar = hoje - timedelta(days=1)
        segunda_passada = None
        sexta_passada   = None

    log.info("=" * 60)
    log.info(f"  JOB SINEX — a processar {dia_a_processar}")
    log.info("=" * 60)

    processar_intervalo(str(dia_a_processar), str(dia_a_processar))

    if hoje.weekday() == 0 and segunda_passada and sexta_passada:
        log.info(f"  Segunda -> bonus {segunda_passada} a {sexta_passada} ...")
        try:
            conn_jogo = pyodbc.connect(JOGO_CONN)
            try:
                processar_bonus_semanal(segunda_passada, sexta_passada, conn_jogo)
                recalcular_pontos_total(conn_jogo)
            finally:
                conn_jogo.close()
        except Exception as e:
            log.error(f"  ERRO no bonus semanal: {e}")

    log.info("  Job concluido.\n")


# ─────────────────────────────────────────────
#  ARRANQUE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    log.info("A correr job...")
    run_job()
    log.info("Job terminado.")
