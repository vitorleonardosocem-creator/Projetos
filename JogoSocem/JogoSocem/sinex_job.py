"""
=============================================================
  sinex_job.py  —  Job Diário SINEX → jogo_socem
=============================================================

  Corre todos os dias via Task Scheduler.
  Vai buscar os registos do dia anterior (dias úteis apenas).

  REGRAS DE PONTUAÇÃO:
  ┌─────────────────────────────────────────────────────────┐
  │  POR DIA (seg-sex, excluindo feriados):                 │
  │    < 7.2h               →  -1  (saiu cedo)             │
  │    >= 7.2h e <= 9.2h    →  +1  (cumpriu ✅)            │
  │    > 9.2h               →  -1  (logout esquecido)      │
  │    sem registo           →   0  (folga, neutro)         │
  │                                                         │
  │  BÓNUS SEMANAL (calculado às segundas):                 │
  │    5 dias úteis todos com +1  →  +1 extra              │
  └─────────────────────────────────────────────────────────┘

  FLUXO POR DIA:
    Seg → processa Sexta passada + bónus semana passada
    Ter → processa Segunda
    Qua → processa Terça
    Qui → processa Quarta
    Sex → processa Quinta
    Sáb/Dom → não faz nada
    Feriado  → não faz nada

  Anti-duplicação: tabela 'pontos' com tarefa='sinex_YYYY-MM-DD'
  → se já existe registo, ignora sem duplicar.

  Instalar dependências:
      pip install pyodbc pandas holidays

=============================================================
"""

import pyodbc
import pandas as pd
import logging
import logging.handlers
from datetime import date, timedelta
from typing import Optional

try:
    import holidays as holidays_lib
    HAS_HOLIDAYS = True
except ImportError:
    HAS_HOLIDAYS = False
    print("AVISO: biblioteca 'holidays' não instalada. Usar: pip install holidays")
    print("       A usar lista manual de feriados como fallback.")


# ─────────────────────────────────────────────
#  LOGGING (com rotação — mantém 30 dias)
# ─────────────────────────────────────────────

_log_handler = logging.handlers.TimedRotatingFileHandler(
    "sinex_job.log",
    when="D",
    interval=1,
    backupCount=30,
    encoding="utf-8"
)
_log_handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)s  %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[_log_handler, logging.StreamHandler()]
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
    """Devolve set de dates com feriados para o ano dado."""
    if ano in _feriados_cache:
        return _feriados_cache[ano]

    feriados = set()

    if HAS_HOLIDAYS:
        pt = holidays_lib.Portugal(years=ano)
        feriados.update(pt.keys())
    else:
        # Feriados nacionais fixos (fallback sem biblioteca)
        feriados.update([
            date(ano, 1, 1),    # Ano Novo
            date(ano, 4, 25),   # Dia da Liberdade
            date(ano, 5, 1),    # Dia do Trabalhador
            date(ano, 6, 10),   # Dia de Portugal
            date(ano, 8, 15),   # Assunção
            date(ano, 10, 5),   # Implantação da República
            date(ano, 11, 1),   # Todos os Santos
            date(ano, 12, 1),   # Restauração da Independência
            date(ano, 12, 8),   # Imaculada Conceição
            date(ano, 12, 25),  # Natal
        ])

    # Feriado municipal de Alcobaça (Martingança) — 20 de agosto
    feriados.add(date(ano, 8, 20))

    _feriados_cache[ano] = feriados
    return feriados


def is_dia_util(d: date) -> bool:
    """True se o dia for dia útil (seg-sex, não feriado)."""
    if d.weekday() >= 5:
        return False
    return d not in get_feriados(d.year)


# ─────────────────────────────────────────────
#  QUERY SINEX
# ─────────────────────────────────────────────

def get_query(data_inicio: str, data_fim: str) -> str:
    return f"""
    SELECT
        e.WorkName                    AS Operador,
        CAST(p.Start AS DATE)         AS Data,
        ISNULL(c.Name, 'Sem Secção')  AS Seccao,
        CAST(
            (DATEDIFF(ss, p.Start, ISNULL(p.Finish, GETDATE())) / 3600.0)
        AS DECIMAL(10,2))             AS Horas_Registo

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
    if horas < HORAS_MIN:
        return -1   # saiu cedo
    elif horas > HORAS_MAX:
        return -1   # logout esquecido
    else:
        return 1    # cumpriu ✅


def calcular_pontos_diarios(df: pd.DataFrame, dia_alvo: date) -> tuple[dict, dict]:
    """
    Devolve (pontos_dict, seccoes_dict) para o dia_alvo.

    CORREÇÃO: agrupa horas por Operador (não por Operador+Seccao).
    Se um operador trabalhou em 2 secções no mesmo dia, as horas somam-se
    corretamente antes de pontuar. A secção é a mais frequente do dia.
    """
    if df.empty:
        return {}, {}

    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"]).dt.date
    df_dia = df[df["Data"] == dia_alvo].copy()

    if df_dia.empty:
        return {}, {}

    # Normalizar nomes (trim de espaços invisíveis)
    df_dia["Operador"] = df_dia["Operador"].str.strip()
    df_dia = df_dia[df_dia["Operador"] != ""]

    # Total de horas por operador no dia (soma de todos os postos/secções)
    horas_por_op = (
        df_dia.groupby("Operador")["Horas_Registo"]
        .sum()
        .reset_index()
        .rename(columns={"Horas_Registo": "Horas_Dia"})
    )

    # Secção mais frequente por operador no dia
    seccoes = (
        df_dia.groupby("Operador")["Seccao"]
        .agg(lambda x: x.value_counts().index[0])
        .to_dict()
    )

    pontos = {}
    for _, row in horas_por_op.iterrows():
        op = row["Operador"]
        pontos[op] = pontuar_dia(float(row["Horas_Dia"]))

    return pontos, seccoes


# ─────────────────────────────────────────────
#  FUNÇÕES JOGO_SOCEM
# ─────────────────────────────────────────────

_dept_cache: dict = {}


def garantir_dept(cursor, nome_seccao: str) -> int:
    """Garante que o departamento existe na BD. Usa cache em memória."""
    nome_seccao = nome_seccao.strip() or "Sem Secção"

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
    log.info(f"  🏭  Dept criado: '{nome_seccao}' (ID {new_id})")
    return new_id


def garantir_utilizador(cursor, nome: str, dept_id: int) -> int:
    """Garante que o utilizador existe na BD. Atualiza dept se mudou."""
    nome = nome.strip()
    cursor.execute(
        "SELECT id, departamento_id FROM users WHERE LOWER(nome) = LOWER(?)", (nome,)
    )
    row = cursor.fetchone()

    if row:
        user_id    = int(row[0])
        dept_atual = row[1]
        if dept_atual is None or int(dept_atual) != dept_id:
            cursor.execute(
                "UPDATE users SET departamento_id = ? WHERE id = ?", (dept_id, user_id)
            )
        return user_id

    cursor.execute(
        "INSERT INTO users (nome, departamento_id, pontos_total, ferias_ganhas) "
        "OUTPUT INSERTED.id VALUES (?, ?, 0, 0)",
        (nome, dept_id)
    )
    new_id = int(cursor.fetchone()[0])
    log.info(f"  👤  Utilizador criado: '{nome}' → dept ID {dept_id}")
    return new_id


def ja_processado(cursor, user_id: int, tarefa: str) -> bool:
    """
    Verifica via tabela 'pontos' se esta tarefa já foi processada para este user.
    Tarefa = 'sinex_YYYY-MM-DD' ou 'bonus_semana_YYYY-MM-DD_YYYY-MM-DD'
    """
    cursor.execute(
        "SELECT COUNT(*) FROM pontos WHERE user_id = ? AND tarefa = ?",
        (user_id, tarefa)
    )
    return cursor.fetchone()[0] > 0


def aplicar_ponto(cursor, conn, user_id: int, nome: str, pontos: int,
                  tarefa: str, data_ref: date) -> bool:
    """
    Insere na tabela pontos + eventos e atualiza users.pontos_total.
    Devolve True se aplicado, False se já existia (duplicado).
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


# ─────────────────────────────────────────────
#  PROCESSAR UM DIA
# ─────────────────────────────────────────────

def processar_dia_na_bd(pontos_dict: dict, seccoes_dict: dict,
                        data_ref: date, conn) -> dict:
    """
    Aplica os pontos de um dia ao jogo_socem.
    Cada operador é processado individualmente — um erro não para os outros.

    Devolve resumo: {"aplicados": int, "ignorados": int, "erros": list}
    """
    cursor = conn.cursor()
    aplicados = 0
    ignorados = 0
    erros     = []
    tarefa    = f"sinex_{data_ref}"

    for operador, pontos in pontos_dict.items():
        if pontos == 0:
            continue
        try:
            seccao  = seccoes_dict.get(operador, "Sem Secção")
            dept_id = garantir_dept(cursor, seccao)
            user_id = garantir_utilizador(cursor, operador, dept_id)
            conn.commit()

            aplicado = aplicar_ponto(cursor, conn, user_id, operador,
                                     pontos, tarefa, data_ref)
            if aplicado:
                sinal = "+" if pontos > 0 else ""
                log.info(f"    {sinal}{pontos}  {operador}  [{seccao}]")
                aplicados += 1
            else:
                log.info(f"  ⏭️   {operador} — já processado ({tarefa}), ignorado.")
                ignorados += 1

        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            msg = f"{operador}: {e}"
            log.error(f"  ❌  Erro ao processar {msg}")
            erros.append(msg)

    return {"aplicados": aplicados, "ignorados": ignorados, "erros": erros}


# ─────────────────────────────────────────────
#  BÓNUS SEMANAL
# ─────────────────────────────────────────────

def get_dias_uteis_semana(segunda: date, sexta: date) -> list:
    """Devolve lista de dias úteis entre segunda e sexta (inclusive)."""
    dias = []
    d = segunda
    while d <= sexta:
        if is_dia_util(d):
            dias.append(d)
        d += timedelta(days=1)
    return dias


def processar_bonus_semanal(segunda: date, sexta: date, conn) -> dict:
    """
    Verifica via tabela 'pontos' quem teve +1 em todos os dias úteis da semana
    e atribui +1 de bónus.

    Devolve {"aplicados": int, "ignorados": int}
    """
    dias_uteis = get_dias_uteis_semana(segunda, sexta)
    tarefa_bonus = f"bonus_semana_{segunda}_{sexta}"

    if len(dias_uteis) < 5:
        log.info(
            f"  ℹ️   Semana {segunda}→{sexta} tem {len(dias_uteis)} dias úteis "
            f"(feriados?) — bónus não aplicado."
        )
        return {"aplicados": 0, "ignorados": 0}

    tarefas_dia = [f"sinex_{d}" for d in dias_uteis]
    placeholders = ",".join(["?" for _ in tarefas_dia])
    n_dias = len(tarefas_dia)

    cursor = conn.cursor()

    # Utilizadores com +1 em todos os dias úteis da semana
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
    aplicados = 0
    ignorados = 0

    for row in candidatos:
        user_id, nome, _ = int(row[0]), row[1], row[2]
        try:
            aplicado = aplicar_ponto(cursor, conn, user_id, nome,
                                     1, tarefa_bonus, sexta)
            if aplicado:
                log.info(f"  ⭐  Bónus semana completa +1 → {nome}")
                aplicados += 1
            else:
                log.info(f"  ⏭️   Bónus {nome} já aplicado — ignorado.")
                ignorados += 1
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            log.error(f"  ❌  Erro bónus {nome}: {e}")

    if aplicados == 0 and ignorados == 0:
        log.info("  ℹ️   Nenhum operador com semana completa.")

    return {"aplicados": aplicados, "ignorados": ignorados}


# ─────────────────────────────────────────────
#  SEMANAS COMPLETAS NUM INTERVALO
# ─────────────────────────────────────────────

def get_semanas_completas(data_inicio: date, data_fim: date) -> list:
    """
    Devolve lista de (segunda, sexta) para cada semana Mon-Fri
    completamente contida no intervalo [data_inicio, data_fim].
    """
    semanas = []
    # Primeira segunda-feira >= data_inicio
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
    Processa pontos Sinex para todos os dias úteis no intervalo [data_inicio, data_fim].
    Inclui bónus semanal para semanas completas dentro do intervalo.
    Anti-duplicação via tabela 'pontos': dias já processados são ignorados.

    Devolve dict com resumo do processamento (para a UI de reprocessamento).
    """
    try:
        data_inicio = date.fromisoformat(data_inicio_str)
        data_fim    = date.fromisoformat(data_fim_str)
    except ValueError as e:
        return {"erro_fatal": f"Data inválida: {e}"}

    if data_inicio > data_fim:
        return {"erro_fatal": "Data início é posterior à data fim."}

    resultado = {
        "data_inicio": data_inicio_str,
        "data_fim":    data_fim_str,
        "dias": [],
        "bonus": [],
        "total_aplicados": 0,
        "total_ignorados": 0,
        "total_erros":    0,
        "erro_fatal":     None,
    }

    # Dias úteis no intervalo
    dias_uteis = []
    d = data_inicio
    while d <= data_fim:
        if is_dia_util(d):
            dias_uteis.append(d)
        d += timedelta(days=1)

    if not dias_uteis:
        resultado["erro_fatal"] = "Sem dias úteis no intervalo selecionado."
        return resultado

    log.info("=" * 60)
    log.info(f"  🔄  REPROCESSAMENTO {data_inicio} → {data_fim}  ({len(dias_uteis)} dias úteis)")
    log.info("=" * 60)

    # Ler Sinex para todo o intervalo de uma vez
    data_fim_query = str(data_fim + timedelta(days=1))  # exclusive
    try:
        sinex_conn = pyodbc.connect(SINEX_CONN, timeout=30)
        df = pd.read_sql(get_query(data_inicio_str, data_fim_query), sinex_conn)
        sinex_conn.close()
        log.info(f"  📥  {len(df):,} registos lidos do Sinex.")
    except Exception as e:
        log.error(f"  ❌  Erro a ler Sinex: {e}")
        resultado["erro_fatal"] = f"Erro ao ler Sinex: {e}"
        return resultado

    # Ligar ao jogo_socem
    try:
        conn_jogo = pyodbc.connect(JOGO_CONN)
    except Exception as e:
        log.error(f"  ❌  Erro a ligar jogo_socem: {e}")
        resultado["erro_fatal"] = f"Erro ao ligar jogo_socem: {e}"
        return resultado

    try:
        # Processar cada dia útil
        for dia in dias_uteis:
            log.info(f"  📊  {dia} ...")
            pontos_dia, seccoes = calcular_pontos_diarios(df, dia)

            if not pontos_dia:
                log.info(f"  ℹ️   Sem registos Sinex para {dia}.")
                resultado["dias"].append({
                    "data":      str(dia),
                    "aplicados": 0,
                    "ignorados": 0,
                    "erros":     0,
                    "sem_dados": True,
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
        semanas = get_semanas_completas(data_inicio, data_fim)
        for segunda, sexta in semanas:
            log.info(f"  ⭐  Bónus semana {segunda} → {sexta} ...")
            res_bonus = processar_bonus_semanal(segunda, sexta, conn_jogo)
            resultado["bonus"].append({
                "semana":    f"{segunda} → {sexta}",
                "aplicados": res_bonus["aplicados"],
                "ignorados": res_bonus["ignorados"],
            })

        # ── RECALCULAR pontos_total a partir da tabela pontos ──────────
        # Garante que users.pontos_total está sempre em sincronismo com a
        # soma real da tabela pontos (evita desvios por triggers, double-updates, etc.)
        log.info("  🔄  A recalcular pontos_total de todos os utilizadores...")
        try:
            cursor_fix = conn_jogo.cursor()
            cursor_fix.execute("""
                UPDATE u
                SET u.pontos_total = ISNULL(p.soma, 0)
                FROM users u
                LEFT JOIN (
                    SELECT user_id, SUM(pontos) AS soma
                    FROM pontos
                    GROUP BY user_id
                ) p ON p.user_id = u.id
            """)
            conn_jogo.commit()
            log.info("  ✅  pontos_total recalculado com sucesso.")
        except Exception as e_fix:
            log.error(f"  ⚠️   Erro ao recalcular pontos_total: {e_fix}")
        # ───────────────────────────────────────────────────────────────

    except Exception as e:
        log.error(f"  ❌  Erro inesperado: {e}")
        resultado["erro_fatal"] = str(e)
    finally:
        try:
            conn_jogo.close()
        except Exception:
            pass

    log.info(
        f"  🏁  Concluído: {resultado['total_aplicados']} aplicados, "
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

    # Fim de semana
    if hoje.weekday() >= 5:
        log.info("  ℹ️   Fim de semana — job ignorado.")
        return

    # Feriado (hoje é feriado, o job não corre)
    if not is_dia_util(hoje):
        log.info(f"  ℹ️   {hoje} é feriado — job ignorado.")
        return

    # Segunda-feira: processa sexta passada + bónus
    if hoje.weekday() == 0:
        dia_a_processar = hoje - timedelta(days=3)
        segunda_passada = hoje - timedelta(days=7)
        sexta_passada   = hoje - timedelta(days=3)
    else:
        dia_a_processar = hoje - timedelta(days=1)
        segunda_passada = None
        sexta_passada   = None

    log.info("=" * 60)
    log.info(f"  🚀  JOB SINEX — a processar {dia_a_processar}")
    log.info("=" * 60)

    # Processar o dia
    processar_intervalo(str(dia_a_processar), str(dia_a_processar))

    # Bónus semanal só às segundas
    if hoje.weekday() == 0 and segunda_passada and sexta_passada:
        log.info(f"  ⭐  Segunda → bónus {segunda_passada} a {sexta_passada} ...")
        try:
            conn_jogo = pyodbc.connect(JOGO_CONN)
            try:
                processar_bonus_semanal(segunda_passada, sexta_passada, conn_jogo)
            finally:
                conn_jogo.close()
        except Exception as e:
            log.error(f"  ❌  Erro no bónus semanal: {e}")

    # Recalcular pontos_total (salvaguarda final)
    try:
        conn_jogo = pyodbc.connect(JOGO_CONN)
        cursor_fix = conn_jogo.cursor()
        cursor_fix.execute("""
            UPDATE u
            SET u.pontos_total = ISNULL(p.soma, 0)
            FROM users u
            LEFT JOIN (
                SELECT user_id, SUM(pontos) AS soma
                FROM pontos
                GROUP BY user_id
            ) p ON p.user_id = u.id
        """)
        conn_jogo.commit()
        conn_jogo.close()
        log.info("  🔄  pontos_total recalculado.")
    except Exception as e:
        log.error(f"  ⚠️   Erro ao recalcular pontos_total: {e}")

    log.info("  🏁  Job concluído.\n")


# ─────────────────────────────────────────────
#  ARRANQUE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    log.info("▶️   A correr job...")
    run_job()
    log.info("✅  Job terminado.")
