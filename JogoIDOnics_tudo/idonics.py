"""idonics.py
Consultas à base de dados IDOnics (só leitura).

Nota sobre IDs em asMovimentos:
  O campo IDUser em asMovimentos pode referenciar:
    1. Pessoas.ID directamente (colaboradores mais antigos)
    2. Pessoas.IDUser1 (colaboradores mais recentes, ex: Vitor, Ricardo)
  A função obter_movimentos trata ambos os casos através de um mapeamento.

Nota sobre horários e planos de trabalho:
  - obter_planos_colaboradores  → IDPlanoTrabalho + DataRef + ciclo de DiaDif
  - obter_dados_horarios        → entrada/saída marcadas + objectivo de horas
  Estas funções suportam o cálculo schedule-aware em jogo.py (regra dos 30 min).
"""
from collections import defaultdict
from datetime import timedelta
from base_dados import ligar_idonics


def obter_departamentos():
    """Devolve lista de departamentos do IDOnics."""
    conn = ligar_idonics()
    c = conn.cursor()
    c.execute("SELECT ID, Nome FROM Departamentos WHERE Nome IS NOT NULL ORDER BY Nome")
    resultado = [
        {"id": r[0], "nome": r[1].strip()}
        for r in c.fetchall()
        if r[1] and r[1].strip()
    ]
    conn.close()
    return resultado


def obter_colaboradores_idonics():
    """
    Devolve colaboradores activos e reais do IDOnics.

    Filtros aplicados:
      - Activo = 1 no IDOnics
      - Nome válido (sem placeholders como '(nome)')
      - IDUser1 definido (obrigatório para leitura de picagens)
      - Teve pelo menos uma picagem nos últimos 90 dias
        → exclui automaticamente: ex-funcionários, clientes,
          fornecedores, contas de sistema e placeholders
    """
    conn = ligar_idonics()
    c = conn.cursor()
    c.execute("""
        SELECT DISTINCT p.ID, p.Nome, p.NomeDisp, p.Numero, p.IDDepartamento
        FROM Pessoas p
        JOIN asMovimentos m ON m.IDUser = p.IDUser1
        WHERE p.Activo = 1
          AND p.Nome IS NOT NULL
          AND p.Nome NOT LIKE '(%'
          AND LEN(LTRIM(RTRIM(p.Nome))) > 2
          AND p.IDUser1 IS NOT NULL
          AND m.DateMov >= DATEADD(day, -90, GETDATE())
          AND m.Valido = 1
        ORDER BY p.Nome
    """)
    resultado = [
        {
            "id": r[0],
            "nome": (r[1] or "").strip(),
            "nome_disp": (r[2] or "").strip() if r[2] and r[2].strip() else (r[1] or "").strip(),
            "numero": str(r[3]).strip() if r[3] else "",
            "id_departamento": r[4]
        }
        for r in c.fetchall()
    ]
    conn.close()
    return resultado


def _construir_mapa_ids(c, ids_colaboradores: list) -> tuple:
    """
    Constrói um mapeamento de IDUser (em asMovimentos) → Pessoas.ID (canónico).

    O asMovimentos usa IDUser = Pessoas.ID OU IDUser = Pessoas.IDUser1
    consoante o colaborador. Este mapeamento resolve ambos os casos.

    Devolve:
      mapa: dict {id_em_asMovimentos → id_canonico_Pessoas}
      todos_ids: set com todos os IDs a usar na query ao asMovimentos
    """
    if not ids_colaboradores:
        return {}, set()

    ids_str = ",".join(str(int(i)) for i in ids_colaboradores)

    # Buscar Pessoas.ID, IDUser1 e IDUser2 para todos os colaboradores
    c.execute(f"SELECT ID, IDUser1, IDUser2 FROM Pessoas WHERE ID IN ({ids_str})")

    mapa = {}
    todos_ids = set()

    for r in c.fetchall():
        id_pessoa   = r[0]
        id_user1    = r[1]
        id_user2    = r[2]

        # Sempre mapear o ID directo (pode ser usado em registos antigos)
        mapa[id_pessoa] = id_pessoa
        todos_ids.add(id_pessoa)

        # Mapear IDUser1 → mesmo Pessoas.ID canónico
        if id_user1:
            mapa[id_user1] = id_pessoa
            todos_ids.add(id_user1)

        # Mapear IDUser2 → mesmo Pessoas.ID canónico
        if id_user2:
            mapa[id_user2] = id_pessoa
            todos_ids.add(id_user2)

    return mapa, todos_ids


def obter_movimentos(data_ini: str, data_fim_exclusiva: str, ids_colaboradores: list) -> list:
    """
    Lê picagens do asMovimentos para o intervalo e lista de colaboradores.
    Devolve lista de dicionários com {id_pessoa, data (date), picagens (lista de datetimes)}.

    Trata automaticamente o caso em que IDUser = Pessoas.IDUser1
    (colaboradores mais recentes como Vitor Leonardo, Ricardo Querido, etc.).

    data_ini e data_fim_exclusiva no formato 'YYYY-MM-DD'.
    data_fim_exclusiva é exclusiva (passar data_fim + 1 dia).
    Só conta picagens válidas (Valido = 1).
    """
    if not ids_colaboradores:
        return []

    conn = ligar_idonics()
    c = conn.cursor()

    # Construir mapeamento: IDUser_em_asMovimentos → Pessoas.ID_canónico
    mapa, todos_ids = _construir_mapa_ids(c, ids_colaboradores)

    if not todos_ids:
        conn.close()
        return []

    # Query ao asMovimentos com TODOS os possíveis IDUser (directos + IDUser1 + IDUser2)
    ids_str = ",".join(str(int(i)) for i in todos_ids)

    c.execute(f"""
        SELECT IDUser, CAST(DateMov AS DATE) AS dia, DateMov
        FROM asMovimentos
        WHERE DateMov >= ? AND DateMov < ?
          AND IDUser IN ({ids_str})
          AND Valido = 1
        ORDER BY IDUser, DateMov
    """, (data_ini, data_fim_exclusiva))

    # Agrupa por (id_pessoa_canónico, dia)
    grupos = defaultdict(list)
    for r in c.fetchall():
        id_canonico = mapa.get(r[0], r[0])   # resolver para Pessoas.ID
        chave = (id_canonico, r[1])           # (Pessoas.ID, date)
        grupos[chave].append(r[2])            # datetime da picagem

    conn.close()

    return [
        {
            "id_pessoa": id_pessoa,
            "data":      dia,
            "picagens":  sorted(picagens)
        }
        for (id_pessoa, dia), picagens in grupos.items()
    ]


# ─── Horários e Planos de Trabalho ───────────────────────────────────────────

def obter_dados_horarios(ids_horarios: list) -> dict:
    """
    Para cada IDHorario, devolve:
      {
        id_horario: {
          'is_folga': bool,
          'entrada':  datetime  (hora marcada de entrada — base 1900-01-01),
          'saida':    datetime  (hora marcada de saída   — base 1900-01-01),
          'objectivo_horas': float
        }
      }

    Classifica como horário normal (objectivo = 8h) se tiver período Tipo=3
    (almoço), caso contrário usa o objectivo configurado em asHorarios.
    """
    if not ids_horarios:
        return {}

    conn = ligar_idonics()
    c    = conn.cursor()

    ids_str = ",".join(str(int(i)) for i in ids_horarios)

    # Objectivo de cada IDHorario (em asHorarios)
    c.execute(f"SELECT ID, Objectivo FROM asHorarios WHERE ID IN ({ids_str})")
    objectivos_db = {r[0]: r[1] for r in c.fetchall()}

    # Períodos activos de cada IDHorario (asHorariosPeriodos)
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

        # Sem períodos de trabalho (Tipo=1) → FOLGA ou horário vazio
        tipo1 = [p for p in ps if p["tipo"] == 1]
        if not tipo1:
            resultado[id_h] = {"is_folga": True}
            continue

        # Hora de entrada marcada: primeiro período Tipo=0 (janela MANHÃ),
        # ou Início do primeiro Tipo=1 se não existir Tipo=0.
        tipo0 = [p for p in ps if p["tipo"] == 0]
        entrada_dt = tipo0[0]["inicio"] if tipo0 else tipo1[0]["inicio"]

        # Hora de saída marcada: Fim do último período Tipo=1.
        saida_dt = tipo1[-1]["fim"]

        # Objectivo: 8h se tem almoço (Tipo=3 = pausa obrigatória).
        # Caso contrário usa o valor de asHorarios.Objectivo.
        tem_almoco = any(p["tipo"] == 3 for p in ps)
        if tem_almoco:
            objectivo_h = 8.0
        else:
            obj_dt = objectivos_db.get(id_h)
            objectivo_h = (obj_dt.hour + obj_dt.minute / 60.0) if obj_dt else 8.0

        # Janela de pausa (almoço/jantar):
        #   Tipo=3 → janela definida na BD (Inicio / Fim).
        #   Sem Tipo=3 (turnos) → deriva: entrada + 6 h .. entrada + 6 h 30 min.
        #   T1 06:00 → 12:00-12:30 | T2 14:00 → 20:00-20:30 | T3 22:00 → 04:00-04:30
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
            "pausa_inicio":    pausa_inicio,   # hora mínima de saída para pausa
            "pausa_fim":       pausa_fim,      # hora máxima de regresso de pausa
        }

    return resultado


def obter_planos_colaboradores(ids_colaboradores: list) -> dict:
    """
    Para cada Pessoas.ID, devolve informação do plano de trabalho:
      {
        id_pessoa: {
          'id_plano':  int,
          'data_ref':  date,        ← data de referência do ciclo
          'ciclo_len': int,         ← número de dias no ciclo
          'ciclo':     {dia_dif: id_horario, ...}
        }
      }
    Colaboradores sem IDPlanoTrabalho não são incluídos no resultado.
    """
    if not ids_colaboradores:
        return {}

    conn = ligar_idonics()
    c    = conn.cursor()

    ids_str = ",".join(str(int(i)) for i in ids_colaboradores)

    # IDPlanoTrabalho e DataRef para cada pessoa
    c.execute(f"""
        SELECT p.ID, p.IDPlanoTrabalho, pt.DataRef
        FROM   Pessoas p
        JOIN   asPlanosTrabalho pt ON pt.ID = p.IDPlanoTrabalho
        WHERE  p.ID IN ({ids_str})
          AND  p.IDPlanoTrabalho IS NOT NULL
    """)

    planos: dict = {}
    plano_ids:  set = set()
    for r in c.fetchall():
        id_pessoa = r[0]
        id_plano  = r[1]
        data_ref  = r[2].date() if hasattr(r[2], "date") else r[2]
        planos[id_pessoa] = {
            "id_plano": id_plano,
            "data_ref": data_ref,
        }
        plano_ids.add(id_plano)

    # Ciclo de cada plano: DiaDif → IDHorario
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
