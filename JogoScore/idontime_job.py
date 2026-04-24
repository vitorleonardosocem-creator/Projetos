"""
=============================================================
  idontime_job.py  —  Job Diário IDOntime → jogo_idonics
=============================================================

  REGRAS DE PONTUAÇÃO:
  ┌─────────────────────────────────────────────────────────┐
  │  POR DIA (baseado no plano de trabalho do colaborador): │
  │    +1  horas líquidas efectivas >= objectivo do horário │
  │    -1  tem picagens mas não atinge o objectivo           │
  │     0  sem picagens (folga, ausência) → ignorado         │
  │                                                         │
  │  REGRA DOS 30 MINUTOS:                                  │
  │    Entrada tarde    → +30 min por fracção de 30 min     │
  │    Saída cedo       → −30 min por fracção de 30 min     │
  │    Regresso tarde   → +30 min por fracção de 30 min     │
  │    Entrar cedo: sem bónus (conta hora marcada)          │
  │                                                         │
  │  TURNOS NOCTURNOS (entrada ≥ 20:00):                   │
  │    Combina picagens do dia D + dia D+1                  │
  └─────────────────────────────────────────────────────────┘

  Anti-duplicação: tabela 'pontos' com UNIQUE(id_colaborador, tarefa)
  Tarefa: 'picagem_YYYY-MM-DD'

  Ligações:
    IDOnics (só leitura): 192.168.31.241 — ReadOnly / R3ad0nly2026
    jogo_idonics (escrita): 192.168.10.156 — GV / NovaSenhaForte987

  Instalar dependências:
      pip install pyodbc

=============================================================
"""

import pyodbc
import logging
import math
from datetime import datetime, timedelta, date
from collections import defaultdict
from typing import Optional

try:
    import holidays as holidays_lib
    HAS_HOLIDAYS = True
except ImportError:
    HAS_HOLIDAYS = False

# ─────────────────────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
#  LIGAÇÕES
# ─────────────────────────────────────────────────────────────

IDONICS_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.31.241;"
    "DATABASE=idonicsys_socem;"
    "UID=ReadOnly;"
    "PWD=R3ad0nly2026;"
    "TrustServerCertificate=yes;"
)

JOGO_IDONICS_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=jogo_idonics;"
    "UID=GV;"
    "PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)

# Planos de trabalho elegíveis para o jogo
PLANOS_JOGO = ('SC-NORM', 'SC-NOR-BH', 'ST-NORM', 'SC-LIMP')


# ─────────────────────────────────────────────────────────────
#  CONSULTAS AO IDONICS (só leitura)
# ─────────────────────────────────────────────────────────────

def obter_departamentos_idonics() -> list:
    """Devolve lista de departamentos do IDOnics."""
    conn = pyodbc.connect(IDONICS_CONN, timeout=10)
    c = conn.cursor()
    c.execute("SELECT ID, Nome FROM Departamentos WHERE Nome IS NOT NULL ORDER BY Nome")
    resultado = [
        {"id": r[0], "nome": r[1].strip()}
        for r in c.fetchall()
        if r[1] and r[1].strip()
    ]
    conn.close()
    return resultado


def obter_colaboradores_idonics() -> list:
    """
    Devolve colaboradores activos com planos elegíveis.
    Filtros: activo=1, nome válido, IDUser1 definido,
             picagens nos últimos 90 dias, plano em PLANOS_JOGO.
    """
    planos_str = ", ".join(f"'{p}'" for p in PLANOS_JOGO)
    conn = pyodbc.connect(IDONICS_CONN, timeout=10)
    c = conn.cursor()
    c.execute(f"""
        SELECT DISTINCT p.ID, p.Nome, p.NomeDisp, p.Numero, p.IDDepartamento
        FROM Pessoas p
        JOIN asMovimentos m ON m.IDUser = p.IDUser1
        JOIN asPlanosTrabalho pt ON pt.ID = p.IDPlanoTrabalho
        WHERE p.Activo = 1
          AND p.Nome IS NOT NULL
          AND p.Nome NOT LIKE '(%'
          AND LEN(LTRIM(RTRIM(p.Nome))) > 2
          AND p.IDUser1 IS NOT NULL
          AND p.IDPlanoTrabalho IS NOT NULL
          AND m.DateMov >= DATEADD(day, -90, GETDATE())
          AND m.Valido = 1
          AND pt.Codigo IN ({planos_str})
        ORDER BY p.Nome
    """)
    resultado = [
        {
            "id":             r[0],
            "nome":           (r[1] or "").strip(),
            "nome_disp":      (r[2] or "").strip() if r[2] and r[2].strip() else (r[1] or "").strip(),
            "numero":         str(r[3]).strip() if r[3] else "",
            "id_departamento": r[4]
        }
        for r in c.fetchall()
    ]
    conn.close()
    return resultado


def _construir_mapa_ids(c, ids_colaboradores: list) -> tuple:
    """
    Constrói mapeamento IDUser (asMovimentos) → Pessoas.ID (canónico).
    Resolve o caso em que IDUser = Pessoas.IDUser1 ou IDUser = Pessoas.ID.
    """
    if not ids_colaboradores:
        return {}, set()

    ids_str = ",".join(str(int(i)) for i in ids_colaboradores)
    c.execute(f"SELECT ID, IDUser1, IDUser2 FROM Pessoas WHERE ID IN ({ids_str})")

    mapa = {}
    todos_ids = set()

    for r in c.fetchall():
        id_pessoa = r[0]
        id_user1  = r[1]
        id_user2  = r[2]

        mapa[id_pessoa] = id_pessoa
        todos_ids.add(id_pessoa)

        if id_user1:
            mapa[id_user1] = id_pessoa
            todos_ids.add(id_user1)

        if id_user2:
            mapa[id_user2] = id_pessoa
            todos_ids.add(id_user2)

    return mapa, todos_ids


def obter_movimentos_idonics(data_ini: str, data_fim_exclusiva: str, ids_colaboradores: list) -> list:
    """
    Lê picagens do IDOnics para o intervalo e lista de colaboradores.
    Devolve [{id_pessoa, data (date), picagens [datetimes]}].
    """
    if not ids_colaboradores:
        return []

    conn = pyodbc.connect(IDONICS_CONN, timeout=30)
    c = conn.cursor()

    mapa, todos_ids = _construir_mapa_ids(c, ids_colaboradores)

    if not todos_ids:
        conn.close()
        return []

    ids_str = ",".join(str(int(i)) for i in todos_ids)
    c.execute(f"""
        SELECT IDUser, CAST(DateMov AS DATE) AS dia, DateMov
        FROM asMovimentos
        WHERE DateMov >= ? AND DateMov < ?
          AND IDUser IN ({ids_str})
          AND Valido = 1
        ORDER BY IDUser, DateMov
    """, (data_ini, data_fim_exclusiva))

    grupos = defaultdict(list)
    for r in c.fetchall():
        id_canonico = mapa.get(r[0], r[0])
        chave = (id_canonico, r[1])
        grupos[chave].append(r[2])

    conn.close()

    return [
        {
            "id_pessoa": id_pessoa,
            "data":      dia,
            "picagens":  sorted(picagens)
        }
        for (id_pessoa, dia), picagens in grupos.items()
    ]


def obter_dados_horarios_idonics(ids_horarios: list) -> dict:
    """
    Para cada IDHorario, devolve configuração:
    {is_folga, entrada, saida, objectivo_horas, pausa_inicio, pausa_fim}.
    """
    if not ids_horarios:
        return {}

    conn = pyodbc.connect(IDONICS_CONN, timeout=10)
    c = conn.cursor()

    ids_str = ",".join(str(int(i)) for i in ids_horarios)

    c.execute(f"SELECT ID, Objectivo FROM asHorarios WHERE ID IN ({ids_str})")
    objectivos_db = {r[0]: r[1] for r in c.fetchall()}

    c.execute(f"""
        SELECT IDHorario, Tipo, Inicio, Fim
        FROM   asHorariosPeriodos
        WHERE  IDHorario IN ({ids_str}) AND Activo = 1
        ORDER  BY IDHorario, Inicio
    """)
    periodos: dict = defaultdict(list)
    for r in c.fetchall():
        periodos[r[0]].append({"tipo": r[1], "inicio": r[2], "fim": r[3]})

    conn.close()

    resultado = {}
    for id_h in ids_horarios:
        ps = periodos.get(id_h, [])

        tipo1 = [p for p in ps if p["tipo"] == 1]
        if not tipo1:
            resultado[id_h] = {"is_folga": True}
            continue

        tipo0 = [p for p in ps if p["tipo"] == 0]
        entrada_dt = tipo0[0]["inicio"] if tipo0 else tipo1[0]["inicio"]
        saida_dt   = tipo1[-1]["fim"]

        tem_almoco = any(p["tipo"] == 3 for p in ps)
        if tem_almoco:
            objectivo_h = 8.0
        else:
            obj_dt = objectivos_db.get(id_h)
            objectivo_h = (obj_dt.hour + obj_dt.minute / 60.0) if obj_dt else 8.0

        tipo3 = [p for p in ps if p["tipo"] == 3]
        if tipo3:
            pausa_inicio = tipo3[0]["inicio"]
            pausa_fim    = tipo3[0]["fim"]
        else:
            pausa_inicio = entrada_dt + timedelta(hours=6)
            pausa_fim    = entrada_dt + timedelta(hours=6, minutes=30)

        resultado[id_h] = {
            "is_folga":        False,
            "entrada":         entrada_dt,
            "saida":           saida_dt,
            "objectivo_horas": objectivo_h,
            "pausa_inicio":    pausa_inicio,
            "pausa_fim":       pausa_fim,
        }

    return resultado


def obter_planos_colaboradores_idonics(ids_colaboradores: list) -> dict:
    """
    Para cada Pessoas.ID, devolve o plano de trabalho:
    {id_plano, data_ref, ciclo_len, ciclo: {dia_dif: id_horario}}.
    """
    if not ids_colaboradores:
        return {}

    conn = pyodbc.connect(IDONICS_CONN, timeout=10)
    c = conn.cursor()

    ids_str = ",".join(str(int(i)) for i in ids_colaboradores)

    c.execute(f"""
        SELECT p.ID, p.IDPlanoTrabalho, pt.DataRef
        FROM   Pessoas p
        JOIN   asPlanosTrabalho pt ON pt.ID = p.IDPlanoTrabalho
        WHERE  p.ID IN ({ids_str})
          AND  p.IDPlanoTrabalho IS NOT NULL
    """)

    planos: dict = {}
    plano_ids: set = set()
    for r in c.fetchall():
        id_pessoa = r[0]
        id_plano  = r[1]
        data_ref  = r[2].date() if hasattr(r[2], "date") else r[2]
        planos[id_pessoa] = {
            "id_plano": id_plano,
            "data_ref": data_ref,
        }
        plano_ids.add(id_plano)

    if plano_ids:
        plids_str = ",".join(str(i) for i in plano_ids)
        c.execute(f"""
            SELECT IDPlano, DiaDif, IDHorario
            FROM   asPlanosTrabalhoHorarios
            WHERE  IDPlano IN ({plids_str})
            ORDER  BY IDPlano, DiaDif
        """)
        ciclos: dict = defaultdict(dict)
        for r in c.fetchall():
            ciclos[r[0]][r[1]] = r[2]

        for info in planos.values():
            ciclo_dias = ciclos.get(info["id_plano"], {})
            info["ciclo"]     = ciclo_dias
            info["ciclo_len"] = max(ciclo_dias.keys()) if ciclo_dias else 7

    conn.close()
    return planos


# ─────────────────────────────────────────────────────────────
#  LÓGICA DE CÁLCULO DE PONTOS (regra dos 30 minutos)
# ─────────────────────────────────────────────────────────────

def calcular_horas(picagens: list) -> float:
    """Horas líquidas por pares entrada/saída. Ignora pares > 16h."""
    total = 0.0
    for i in range(0, len(picagens) - 1, 2):
        diff = (picagens[i + 1] - picagens[i]).total_seconds() / 3600.0
        if 0 < diff < 16:
            total += diff
    return round(total, 2)


def _hora_no_dia(picagem_ref: datetime, modelo: datetime) -> datetime:
    """Aplica a hora/minuto do modelo à data da picagem real."""
    return picagem_ref.replace(
        hour=modelo.hour, minute=modelo.minute,
        second=0, microsecond=0,
    )


def _minutos_inteiros(delta) -> int:
    """Converte timedelta em minutos inteiros (trunca segundos)."""
    return int(delta.total_seconds() // 60)


def ajustar_entrada(picagem: datetime, ref: datetime) -> datetime:
    """Entrada: pontual/cedo → conta hora marcada. Tarde → +30 min por fracção."""
    marcada = _hora_no_dia(picagem, ref)
    if picagem <= marcada:
        return marcada
    atraso_min = _minutos_inteiros(picagem - marcada)
    return marcada + timedelta(minutes=math.ceil(atraso_min / 30) * 30)


def ajustar_saida(picagem: datetime, ref: datetime) -> datetime:
    """Saída: pontual/tarde → conta tempo real. Cedo → −30 min por fracção."""
    marcada = _hora_no_dia(picagem, ref)
    if picagem >= marcada:
        return picagem
    antec_min = _minutos_inteiros(marcada - picagem)
    return marcada - timedelta(minutes=math.ceil(antec_min / 30) * 30)


def ajustar_regresso_pausa(picagem: datetime, ref: datetime) -> datetime:
    """Regresso de pausa: a tempo → tempo real. Tarde → +30 min por fracção."""
    marcada = _hora_no_dia(picagem, ref)
    if picagem <= marcada:
        return picagem
    tarde_min = _minutos_inteiros(picagem - marcada)
    return marcada + timedelta(minutes=math.ceil(tarde_min / 30) * 30)


def calcular_pontos(picagens: list, entrada_m: datetime, saida_m: datetime,
                    obj_horas: float, pausa_ini: datetime = None,
                    pausa_fim: datetime = None) -> tuple:
    """
    Calcula pontos para um colaborador num dia.
    Devolve (pontos: int, descrição: str).
      +1 → cumpriu objectivo
      -1 → insuficiente ou picagem incompleta
       0 → sem picagens (folga/ausência — ignorado)
    """
    n = len(picagens)
    pics_str = ", ".join(p.strftime("%H:%M:%S") for p in picagens)

    if n == 0:
        return 0, "Sem picagens (folga/ausência — ignorado)"

    if n == 1:
        return -1, f"Picagem incompleta [pics: {pics_str}]"

    adj = list(picagens)

    # Ajustar entrada
    adj[0] = ajustar_entrada(picagens[0], entrada_m)

    # Ajustar picagens de pausa (2ª e 3ª) se existirem e janela definida
    if n >= 4 and pausa_ini and pausa_fim:
        pausa_ini_dia = _hora_no_dia(picagens[1], pausa_ini)
        if picagens[1] >= pausa_ini_dia:
            adj[1] = ajustar_saida(picagens[1], pausa_ini)
        adj[2] = ajustar_regresso_pausa(picagens[2], pausa_fim)

    # Ajustar saída final
    adj[-1] = ajustar_saida(picagens[-1], saida_m)

    if adj[-1] <= adj[0]:
        return -1, f"Saída antes da entrada [pics: {pics_str}]"

    horas = calcular_horas(adj)
    obj_str = f"{obj_horas:g}h"

    if horas >= obj_horas:
        return 1, f"Cumpriu {horas:.1f}h (obj {obj_str}, {n} picagens) [pics: {pics_str}]"

    return -1, f"Insuficiente {horas:.1f}h de {obj_str} ({n} picagens) [pics: {pics_str}]"


# ─────────────────────────────────────────────────────────────
#  SINCRONIZAÇÃO: IDOnics → jogo_idonics
# ─────────────────────────────────────────────────────────────

def sincronizar_colaboradores() -> dict:
    """
    Copia colaboradores e departamentos do IDOnics para jogo_idonics.
    Faz upsert — não apaga nem altera pontos_total.
    Colaboradores que já não passam o filtro são marcados activo=0.
    """
    colaboradores = obter_colaboradores_idonics()
    departamentos  = obter_departamentos_idonics()

    conn = pyodbc.connect(JOGO_IDONICS_CONN)
    c    = conn.cursor()

    for d in departamentos:
        c.execute("""
            IF EXISTS (SELECT 1 FROM departamentos WHERE id = ?)
                UPDATE departamentos SET nome = ? WHERE id = ?
            ELSE
                INSERT INTO departamentos (id, nome) VALUES (?, ?)
        """, d["id"], d["nome"], d["id"], d["id"], d["nome"])

    for p in colaboradores:
        c.execute("""
            IF EXISTS (SELECT 1 FROM colaboradores WHERE id = ?)
                UPDATE colaboradores
                SET nome = ?, nome_disp = ?, numero = ?,
                    id_departamento = ?, activo = 1, data_sync = GETDATE()
                WHERE id = ?
            ELSE
                INSERT INTO colaboradores
                    (id, nome, nome_disp, numero, id_departamento, activo, pontos_total)
                VALUES (?, ?, ?, ?, ?, 1, 0)
        """,
            p["id"],
            p["nome"], p["nome_disp"], p["numero"], p["id_departamento"], p["id"],
            p["id"], p["nome"], p["nome_disp"], p["numero"], p["id_departamento"]
        )

    inactivados = 0
    if colaboradores:
        ids_validos = ",".join(str(p["id"]) for p in colaboradores)
        c.execute(f"""
            UPDATE colaboradores SET activo = 0
            WHERE activo = 1 AND id NOT IN ({ids_validos})
        """)
        inactivados = c.rowcount

    conn.commit()
    conn.close()

    return {
        "colaboradores": len(colaboradores),
        "departamentos": len(departamentos),
        "inactivados":   inactivados,
    }


# ─────────────────────────────────────────────────────────────
#  FERIADOS — Portugal + Alcobaça (20 Ago)
# ─────────────────────────────────────────────────────────────

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


def get_dias_uteis_semana(segunda: date, sexta: date) -> list:
    dias = []
    d = segunda
    while d <= sexta:
        if is_dia_util(d):
            dias.append(d)
        d += timedelta(days=1)
    return dias


def get_semanas_completas(data_inicio: date, data_fim: date) -> list:
    """Devolve lista de (segunda, sexta) de semanas completas dentro do intervalo."""
    semanas = []
    d = data_inicio
    while d.weekday() != 0:   # avançar até segunda-feira
        d += timedelta(days=1)
    while True:
        segunda = d
        sexta   = d + timedelta(days=4)
        if sexta > data_fim:
            break
        semanas.append((segunda, sexta))
        d += timedelta(days=7)
    return semanas


# ─────────────────────────────────────────────────────────────
#  BÓNUS SEMANAL IDONTIME
# ─────────────────────────────────────────────────────────────

def processar_bonus_semanal_idontime(segunda: date, sexta: date, conn) -> dict:
    """
    Atribui +1 de bónus a colaboradores IDOntime que tiveram
    pontos > 0 em todos os dias úteis da semana (segunda → sexta).
    Tarefa: bonus_semana_{segunda}_{sexta}  (mesmo formato do SINEX)
    """
    dias_uteis    = get_dias_uteis_semana(segunda, sexta)
    tarefa_bonus  = f"bonus_semana_{segunda}_{sexta}"

    if len(dias_uteis) < 5:
        log.info(
            f"  Semana {segunda}→{sexta} tem {len(dias_uteis)} dias úteis "
            f"(feriado?) — bónus IDOntime não aplicado."
        )
        return {"aplicados": 0, "ignorados": 0}

    tarefas_dia  = [f"picagem_{d}" for d in dias_uteis]
    n_dias       = len(tarefas_dia)
    placeholders = ",".join(["?" for _ in tarefas_dia])

    cursor = conn.cursor()

    # Colaboradores com +1 em todos os dias úteis da semana
    cursor.execute(f"""
        SELECT p.id_colaborador, c.nome
        FROM   pontos p
        INNER JOIN colaboradores c ON c.id = p.id_colaborador
        WHERE  p.tarefa IN ({placeholders})
          AND  p.pontos > 0
        GROUP BY p.id_colaborador, c.nome
        HAVING COUNT(DISTINCT p.tarefa) = ?
    """, (*tarefas_dia, n_dias))

    candidatos = cursor.fetchall()
    aplicados  = 0
    ignorados  = 0

    for row in candidatos:
        id_colab, nome = int(row[0]), row[1]
        try:
            # Verificar se já foi aplicado (anti-duplicação)
            cursor.execute(
                "SELECT COUNT(1) FROM pontos WHERE id_colaborador = ? AND tarefa = ?",
                id_colab, tarefa_bonus
            )
            if cursor.fetchone()[0] > 0:
                log.info(f"  Bónus {nome} já aplicado — ignorado.")
                ignorados += 1
                continue

            # Inserir bónus
            cursor.execute("""
                INSERT INTO pontos (id_colaborador, tarefa, pontos, obs)
                VALUES (?, ?, 1, ?)
            """, id_colab, tarefa_bonus, f"Bónus semana completa {segunda} a {sexta}")

            # Recalcular pontos_total
            cursor.execute("""
                UPDATE colaboradores
                SET pontos_total = (
                    SELECT ISNULL(SUM(pontos), 0) FROM pontos WHERE id_colaborador = ?
                )
                WHERE id = ?
            """, id_colab, id_colab)

            conn.commit()
            log.info(f"  Bónus semana completa +1 → {nome}")
            aplicados += 1

        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            log.error(f"  ERRO bónus {nome}: {e}")

    if aplicados == 0 and ignorados == 0:
        log.info("  Nenhum colaborador IDOntime com semana completa.")

    return {"aplicados": aplicados, "ignorados": ignorados}


# ─────────────────────────────────────────────────────────────
#  REPROCESSAMENTO
# ─────────────────────────────────────────────────────────────

def reprocessar_intervalo(data_ini: str, data_fim: str) -> dict:
    """
    Processa picagens IDOntime para o intervalo de datas.
    Lê do IDOnics, escreve em jogo_idonics.
    Anti-duplicação: UNIQUE(id_colaborador, tarefa) na tabela pontos.

    Retorna dict com resultado para mostrar no painel admin.
    """
    try:
        datetime.strptime(data_ini, "%Y-%m-%d")
        datetime.strptime(data_fim, "%Y-%m-%d")
    except ValueError as e:
        return {"erro_fatal": f"Data inválida: {e}"}

    resultado = {
        "data_inicio":         data_ini,
        "data_fim":            data_fim,
        "inseridos":           0,
        "ignorados":           0,
        "colaboradores":       0,
        "erro_fatal":          None,
        "log_linhas":          [],
    }

    log.info("=" * 60)
    log.info(f"  REPROCESSAMENTO IDOntime {data_ini} → {data_fim}")
    log.info("=" * 60)

    # 1. Colaboradores activos em jogo_idonics
    conn_jogo = pyodbc.connect(JOGO_IDONICS_CONN)
    c_jogo    = conn_jogo.cursor()
    c_jogo.execute("SELECT id FROM colaboradores WHERE activo = 1")
    ids_colab = [r[0] for r in c_jogo.fetchall()]
    conn_jogo.close()

    if not ids_colab:
        resultado["erro_fatal"] = "Sem colaboradores activos. Execute a sincronização primeiro (/admin/sincronizar-idontime)."
        return resultado

    # 2. Picagens do IDOnics (dia extra para turnos nocturnos)
    dt_fim_excl_extra = (
        datetime.strptime(data_fim, "%Y-%m-%d") + timedelta(days=2)
    ).strftime("%Y-%m-%d")

    try:
        movimentos = obter_movimentos_idonics(data_ini, dt_fim_excl_extra, ids_colab)
    except Exception as e:
        resultado["erro_fatal"] = f"Erro ao ler IDOnics: {e}"
        return resultado

    if not movimentos:
        resultado["erro_fatal"] = f"Sem picagens entre {data_ini} e {data_fim}. Verifica o intervalo."
        return resultado

    # 3. Planos e horários
    try:
        planos_info   = obter_planos_colaboradores_idonics(ids_colab)
        ids_horarios: set = set()
        for info in planos_info.values():
            for id_h in info.get("ciclo", {}).values():
                if id_h:
                    ids_horarios.add(id_h)
        horarios_info = obter_dados_horarios_idonics(list(ids_horarios))
    except Exception as e:
        resultado["erro_fatal"] = f"Erro ao obter planos/horários: {e}"
        return resultado

    # 4. Índice de picagens por (id_colab, date)
    pic_por_chave: dict = {}
    for reg in movimentos:
        d = reg["data"] if isinstance(reg["data"], date) else reg["data"].date()
        pic_por_chave[(reg["id_pessoa"], d)] = reg["picagens"]

    data_ini_dt = datetime.strptime(data_ini, "%Y-%m-%d").date()
    data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d").date()

    # 5. Processar
    processados    = 0
    ignorados      = 0
    ids_afectados: set = set()
    dias_consumidos: set = set()

    conn_jogo = pyodbc.connect(JOGO_IDONICS_CONN)
    c_jogo    = conn_jogo.cursor()

    for reg in movimentos:
        id_colab = reg["id_pessoa"]
        data_mov = reg["data"]
        data_date = data_mov if isinstance(data_mov, date) else data_mov.date()

        if data_date > data_fim_dt:
            continue

        chave = (id_colab, data_date)
        if chave in dias_consumidos:
            continue

        data_str = data_date.strftime("%Y-%m-%d")
        tarefa   = f"picagem_{data_str}"

        if id_colab not in planos_info:
            ignorados += 1
            continue

        info_plano = planos_info[id_colab]
        days_diff  = (data_date - info_plano["data_ref"]).days
        dia_dif    = (days_diff % info_plano["ciclo_len"]) + 1
        id_horario = info_plano.get("ciclo", {}).get(dia_dif)

        if not id_horario:
            ignorados += 1
            continue

        horario = horarios_info.get(id_horario, {})
        if horario.get("is_folga", True):
            ignorados += 1
            continue

        # Turno nocturno: combinar com dia seguinte
        entrada_h  = horario.get("entrada")
        is_noturno = (entrada_h is not None and entrada_h.hour >= 20)

        if is_noturno:
            chave_d1 = (id_colab, data_date + timedelta(days=1))
            pic_d    = pic_por_chave.get(chave, [])
            pic_d1   = pic_por_chave.get(chave_d1, [])
            picagens = sorted(pic_d + pic_d1)
            if chave_d1 in pic_por_chave:
                dias_consumidos.add(chave_d1)
        else:
            picagens = reg["picagens"]

        pts, obs = calcular_pontos(
            picagens,
            horario["entrada"],
            horario["saida"],
            horario["objectivo_horas"],
            pausa_ini=horario.get("pausa_inicio"),
            pausa_fim=horario.get("pausa_fim"),
        )

        if pts == 0:
            ignorados += 1
            continue

        ids_afectados.add(id_colab)

        # Upsert com anti-duplicação
        c_jogo.execute("""
            IF EXISTS (SELECT 1 FROM pontos WHERE id_colaborador = ? AND tarefa = ?)
                UPDATE pontos
                SET pontos = ?, obs = ?, data_pontos = GETDATE()
                WHERE id_colaborador = ? AND tarefa = ?
            ELSE
                INSERT INTO pontos (id_colaborador, tarefa, pontos, obs)
                VALUES (?, ?, ?, ?)
        """,
            id_colab, tarefa,
            pts, obs, id_colab, tarefa,
            id_colab, tarefa, pts, obs,
        )
        processados += 1

        sinal = "+" if pts > 0 else ""
        log.info(f"    {sinal}{pts}  colaborador {id_colab}  [{data_str}]")

    # 6. Recalcular pontos_total para afectados
    for id_colab in ids_afectados:
        c_jogo.execute("""
            UPDATE colaboradores
            SET pontos_total = (
                SELECT ISNULL(SUM(pontos), 0)
                FROM   pontos
                WHERE  id_colaborador = ?
            )
            WHERE id = ?
        """, id_colab, id_colab)

    # 7. Registo do processamento
    c_jogo.execute("""
        INSERT INTO processamentos (data_ini, data_fim, total_registos, obs)
        VALUES (?, ?, ?, ?)
    """, data_ini, data_fim, processados,
        (f"Processados: {processados} | "
         f"Ignorados: {ignorados} | "
         f"Colaboradores: {len(ids_afectados)}"))

    conn_jogo.commit()
    conn_jogo.close()

    resultado["inseridos"]     = processados
    resultado["ignorados"]     = ignorados
    resultado["colaboradores"] = len(ids_afectados)

    log.info(
        f"  Concluído IDOntime: {processados} inseridos, "
        f"{ignorados} ignorados, "
        f"{len(ids_afectados)} colaboradores."
    )

    # Bónus semanal — aplicar para cada semana completa dentro do intervalo
    data_ini_dt = datetime.strptime(data_ini, "%Y-%m-%d").date()
    data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d").date()
    semanas = get_semanas_completas(data_ini_dt, data_fim_dt)

    if semanas:
        conn_bonus = pyodbc.connect(JOGO_IDONICS_CONN)
        try:
            for segunda, sexta in semanas:
                log.info(f"  Bónus semanal IDOntime: {segunda} → {sexta}")
                processar_bonus_semanal_idontime(segunda, sexta, conn_bonus)
        finally:
            conn_bonus.close()

    return resultado


# ─────────────────────────────────────────────────────────────
#  JOB PRINCIPAL (Task Scheduler)
# ─────────────────────────────────────────────────────────────

def run_job():
    """
    Corre todos os dias via Task Scheduler.
    Processa o dia anterior (ou sexta-feira se for segunda).
    Na segunda-feira aplica também o bónus semanal da semana passada.
    """
    hoje = date.today()

    if hoje.weekday() >= 5:
        log.info("  Fim de semana — job IDOntime ignorado.")
        return

    if hoje.weekday() == 0:
        # Segunda → processa sexta passada
        dia_a_processar = hoje - timedelta(days=3)
        segunda_passada = hoje - timedelta(days=7)
        sexta_passada   = hoje - timedelta(days=3)
    else:
        dia_a_processar = hoje - timedelta(days=1)
        segunda_passada = None
        sexta_passada   = None

    log.info("=" * 60)
    log.info(f"  JOB IDOntime — a processar {dia_a_processar}")
    log.info("=" * 60)

    reprocessar_intervalo(str(dia_a_processar), str(dia_a_processar))

    # Bónus semanal — só na segunda-feira
    if hoje.weekday() == 0 and segunda_passada and sexta_passada:
        log.info(f"  Segunda → bónus IDOntime {segunda_passada} a {sexta_passada} ...")
        try:
            conn_bonus = pyodbc.connect(JOGO_IDONICS_CONN)
            try:
                processar_bonus_semanal_idontime(segunda_passada, sexta_passada, conn_bonus)
            finally:
                conn_bonus.close()
        except Exception as e:
            log.error(f"  ERRO no bónus semanal IDOntime: {e}")

    log.info("  Job IDOntime concluído.\n")


# ─────────────────────────────────────────────────────────────
#  ARRANQUE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("A correr job IDOntime...")
    run_job()
    log.info("Job terminado.")
