"""jogo.py
Lógica do jogo: cálculo de pontos, sincronização e reprocessamento.

Regras de pontos (schedule-aware):
  +1  horas líquidas efectivas >= objectivo do horário
  -1  tem picagens mas não atinge o objectivo
   0  sem picagens (folga, ausência não tratada) → ignorado

Regra dos 30 minutos — aplica-se a TODAS as picagens:
  • 1ª picagem (entrada): chegar tarde → +30 min por cada fracção de 30 min de atraso
  • 2ª picagem (saída pausa): sair antes da janela → −30 min por fracção
  • 3ª picagem (regresso pausa): regressar depois da janela → +30 min por fracção
  • Última picagem (saída): sair cedo → −30 min por fracção

  Entrar cedo não dá bónus (conta da hora marcada).
  Sair tarde conta normalmente.

Turnos nocturnos (entrada ≥ 20:00):
  As picagens de entrada (dia D) e saída/pausa (dia D+1) são agrupadas
  automaticamente numa única avaliação de turno.

Colaboradores sem IDPlanoTrabalho → ignorados (0 pontos).
Dias de FOLGA no ciclo → ignorados (0 pontos).
"""
import math
from datetime import datetime, timedelta, date

from base_dados import ligar_jogo
from idonics import (
    obter_colaboradores_idonics,
    obter_departamentos,
    obter_movimentos,
    obter_dados_horarios,
    obter_planos_colaboradores,
)


# ─── Utilitários de tempo ─────────────────────────────────────────────────────

def calcular_horas(picagens: list) -> float:
    """
    Horas líquidas por pares entrada/saída.
    Ignora pares negativos ou impossíveis (>16 h).
    Suporta picagens que cruzam a meia-noite (datetimes completos).
    """
    total = 0.0
    for i in range(0, len(picagens) - 1, 2):
        diff = (picagens[i + 1] - picagens[i]).total_seconds() / 3600.0
        if 0 < diff < 16:
            total += diff
    return round(total, 2)


def _hora_no_dia(picagem_ref: datetime, modelo: datetime) -> datetime:
    """
    Devolve um datetime com a data de picagem_ref mas hora/minuto de modelo.
    modelo vem da BD com base 1900-01-01; só usamos .hour e .minute.
    """
    return picagem_ref.replace(
        hour=modelo.hour, minute=modelo.minute,
        second=0, microsecond=0,
    )


def _fmt(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def _fmt_seg(dt: datetime) -> str:
    """Formato HH:MM:SS para mostrar segundos reais das picagens."""
    return dt.strftime("%H:%M:%S")


# ─── Ajustes dos 30 min ───────────────────────────────────────────────────────

def _minutos_inteiros(delta) -> int:
    """
    Converte timedelta em minutos inteiros (trunca segundos).
    Garante que 08:30:15 não é tratado como "30 min e 15 s" mas sim "30 min".
    """
    return int(delta.total_seconds() // 60)


def ajustar_entrada(picagem: datetime, ref: datetime) -> datetime:
    """
    Entrada de manhã: chegar cedo/pontual → conta da hora marcada (sem bónus).
    Chegar tarde → sobe em múltiplos de 30 min (comparação truncada ao minuto).
    """
    marcada = _hora_no_dia(picagem, ref)
    if picagem <= marcada:
        return marcada                          # pontual ou cedo → sem bónus
    atraso_min = _minutos_inteiros(picagem - marcada)
    return marcada + timedelta(minutes=math.ceil(atraso_min / 30) * 30)


def ajustar_saida(picagem: datetime, ref: datetime) -> datetime:
    """
    Saída final OU saída para pausa: sair pontual/tarde → conta tempo real.
    Sair cedo → desce em múltiplos de 30 min (comparação truncada ao minuto).
    """
    marcada = _hora_no_dia(picagem, ref)
    if picagem >= marcada:
        return picagem                          # pontual ou tarde → tempo real
    antec_min = _minutos_inteiros(marcada - picagem)
    return marcada - timedelta(minutes=math.ceil(antec_min / 30) * 30)


def ajustar_regresso_pausa(picagem: datetime, ref: datetime) -> datetime:
    """
    Regresso de pausa: chegar cedo/pontual → conta tempo real.
    Chegar tarde → sobe em múltiplos de 30 min a partir do fim da janela.
    """
    marcada = _hora_no_dia(picagem, ref)
    if picagem <= marcada:
        return picagem                          # regressou a tempo → tempo real
    tarde_min = _minutos_inteiros(picagem - marcada)
    return marcada + timedelta(minutes=math.ceil(tarde_min / 30) * 30)


# ─── Cálculo de pontos ────────────────────────────────────────────────────────

def calcular_pontos(picagens: list,
                    entrada_m: datetime,
                    saida_m:   datetime,
                    obj_horas: float,
                    pausa_ini: datetime = None,
                    pausa_fim: datetime = None) -> tuple:
    """
    Calcula pontos para um colaborador num dia/turno.

    Regras dos 30 min:
      • Entrada tarde       → +30 min por cada fracção de 30 min de atraso
      • Saída para pausa cedo (antes de pausa_ini) → picagem ignorada (provável erro);
        só se aplica o ajuste se a saída for APÓS o início da janela de pausa
      • Regresso de pausa tarde → +30 min por cada fracção de 30 min de atraso
      • Saída final cedo    → −30 min por cada fracção de 30 min de antecipação

      Entrar cedo não dá bónus (conta da hora marcada).
      Sair tarde conta normalmente.

    Parâmetros:
      picagens  – lista de datetimes ordenados.
      entrada_m – hora marcada de entrada  (datetime base 1900-01-01).
      saida_m   – hora marcada de saída    (datetime base 1900-01-01).
      obj_horas – horas líquidas exigidas (ex: 8.0, 7.5).
      pausa_ini – início permitido da pausa (datetime base 1900-01-01).
      pausa_fim – fim máximo da pausa      (datetime base 1900-01-01).

    Devolve (pontos: int, descrição: str).
    """
    n = len(picagens)

    # Lista de picagens reais com segundos (para perceber entradas/saídas)
    pics_str = ", ".join(_fmt_seg(p) for p in picagens)

    if n == 0:
        return 0, "Sem picagens (folga/ausência — ignorado)"

    if n == 1:
        return -1, f"Picagem incompleta [pics: {pics_str}]"

    adj = list(picagens)

    # ── 1ª picagem: entrada ────────────────────────────────────────────────
    adj[0] = ajustar_entrada(picagens[0], entrada_m)

    # ── Picagens de pausa (2ª e 3ª), se existirem e janela definida ────────
    if n >= 4 and pausa_ini and pausa_fim:
        pausa_ini_dia = _hora_no_dia(picagens[1], pausa_ini)

        # Saída para pausa: só ajusta se saiu APÓS o início da janela de pausa.
        # Picagem antes de pausa_ini é provavelmente um erro → não penaliza.
        if picagens[1] >= pausa_ini_dia:
            adj[1] = ajustar_saida(picagens[1], pausa_ini)

        # Regresso de pausa: aplica sempre — penaliza regresso tardio.
        adj[2] = ajustar_regresso_pausa(picagens[2], pausa_fim)

    # ── Última picagem: saída final ────────────────────────────────────────
    adj[-1] = ajustar_saida(picagens[-1], saida_m)

    # Saída efectiva antes da entrada → dia inválido
    if adj[-1] <= adj[0]:
        return -1, f"Saída efectiva antes da entrada [pics: {pics_str}]"

    horas = calcular_horas(adj)

    obj_str = f"{obj_horas:g}h"   # 8.0→"8h", 7.5→"7.5h"

    if horas >= obj_horas:
        return 1, f"Cumpriu {horas:.1f}h (obj {obj_str}, {n} picagens) [pics: {pics_str}]"

    return -1, f"Insuficiente {horas:.1f}h de {obj_str} ({n} picagens) [pics: {pics_str}]"


# ─── Sincronização ────────────────────────────────────────────────────────────

def sincronizar_colaboradores() -> dict:
    """
    Copia colaboradores e departamentos do IDOnics para a BD do jogo.
    Faz upsert — não apaga registos nem altera pontos_total.
    Colaboradores que já não passam o filtro são marcados activo=0.
    """
    colaboradores = obter_colaboradores_idonics()
    departamentos  = obter_departamentos()

    conn = ligar_jogo()
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


# ─── Reprocessamento ─────────────────────────────────────────────────────────

def reprocessar(data_ini: str, data_fim: str) -> dict:
    """
    Lê picagens do asMovimentos e actualiza pontos na BD do jogo.
    data_ini e data_fim formato 'YYYY-MM-DD' (ambas inclusivas).

    Funcionalidades:
      • Regra dos 30 min em TODAS as picagens (entrada, pausa, saída).
      • Janela de pausa por horário (Tipo=3 da BD ou entry+6h para turnos).
      • Turnos nocturnos (entrada ≥ 20:00): combina picagens do dia D com
        as do dia D+1 numa única avaliação de turno.
    """
    dt_fim_excl = (
        datetime.strptime(data_fim, "%Y-%m-%d") + timedelta(days=1)
    ).strftime("%Y-%m-%d")

    # ── 1. Colaboradores activos ────────────────────────────────────────────
    conn = ligar_jogo()
    c    = conn.cursor()
    c.execute("SELECT id FROM colaboradores WHERE activo = 1")
    ids_colab = [r[0] for r in c.fetchall()]
    conn.close()

    if not ids_colab:
        return {"erro": "Sem colaboradores activos. Execute a sincronização primeiro."}

    # ── 2. Picagens do IDOnics ──────────────────────────────────────────────
    # Para turnos nocturnos que terminam no dia seguinte ao data_fim,
    # pedimos um dia extra ao IDOnics.
    dt_fim_excl_extra = (
        datetime.strptime(data_fim, "%Y-%m-%d") + timedelta(days=2)
    ).strftime("%Y-%m-%d")

    movimentos = obter_movimentos(data_ini, dt_fim_excl_extra, ids_colab)

    if not movimentos:
        return {
            "erro": (f"Sem picagens encontradas entre {data_ini} e {data_fim}. "
                     "Verifica o intervalo de datas.")
        }

    # ── 3. Planos de trabalho ───────────────────────────────────────────────
    planos_info = obter_planos_colaboradores(ids_colab)

    # ── 4. Carregar info de todos os IDHorarios dos planos ─────────────────
    ids_horarios: set = set()
    for info in planos_info.values():
        for id_h in info["ciclo"].values():
            if id_h:
                ids_horarios.add(id_h)

    horarios_info = obter_dados_horarios(list(ids_horarios))

    # ── 5. Índice de picagens por (id_colab, date) ──────────────────────────
    # Necessário para combinar turnos nocturnos (dia D + dia D+1).
    pic_por_chave: dict = {}
    for reg in movimentos:
        d = reg["data"] if isinstance(reg["data"], date) else reg["data"].date()
        pic_por_chave[(reg["id_pessoa"], d)] = reg["picagens"]

    data_ini_dt = datetime.strptime(data_ini, "%Y-%m-%d").date()
    data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d").date()

    # ── 6. Processar cada dia ───────────────────────────────────────────────
    processados    = 0
    ignorados      = 0
    sem_plano      = 0
    folgas         = 0
    ids_afectados: set = set()
    dias_consumidos: set = set()   # (id_colab, date) já contabilizados

    conn = ligar_jogo()
    c    = conn.cursor()

    for reg in movimentos:
        id_colab = reg["id_pessoa"]
        data_mov = reg["data"]
        data_date = data_mov if isinstance(data_mov, date) else data_mov.date()

        # Ignorar dias fora do intervalo pedido (só o dia extra para turnos nocturnos)
        if data_date > data_fim_dt:
            continue

        chave = (id_colab, data_date)
        if chave in dias_consumidos:
            continue   # já processado como parte de um turno nocturno

        data_str = data_date.strftime("%Y-%m-%d")
        tarefa   = f"picagem_{data_str}"

        # Sem plano de trabalho → ignorar
        if id_colab not in planos_info:
            sem_plano += 1
            ignorados += 1
            continue

        # Determinar IDHorario para este dia
        info_plano = planos_info[id_colab]
        days_diff  = (data_date - info_plano["data_ref"]).days
        dia_dif    = (days_diff % info_plano["ciclo_len"]) + 1
        id_horario = info_plano["ciclo"].get(dia_dif)

        if not id_horario:
            ignorados += 1
            continue

        horario = horarios_info.get(id_horario, {})

        if horario.get("is_folga", True):
            folgas += 1
            ignorados += 1
            continue

        # ── Turno nocturno: combinar com o dia seguinte ──────────────────
        entrada_h  = horario.get("entrada")
        is_noturno = (entrada_h is not None and entrada_h.hour >= 20)

        if is_noturno:
            chave_d1    = (id_colab, data_date + timedelta(days=1))
            pic_d       = pic_por_chave.get(chave,    [])
            pic_d1      = pic_por_chave.get(chave_d1, [])
            picagens    = sorted(pic_d + pic_d1)
            # Marcar o dia seguinte como consumido (não será reprocessado)
            if chave_d1 in pic_por_chave:
                dias_consumidos.add(chave_d1)
        else:
            picagens = reg["picagens"]

        # ── Calcular pontos com a regra dos 30 min ────────────────────────
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

        # Upsert
        c.execute("""
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

    # ── 7. Recalcular pontos_total ──────────────────────────────────────────
    for id_colab in ids_afectados:
        c.execute("""
            UPDATE colaboradores
            SET pontos_total = (
                SELECT ISNULL(SUM(pontos), 0)
                FROM   pontos
                WHERE  id_colaborador = ?
            )
            WHERE id = ?
        """, id_colab, id_colab)

    # ── 8. Log ─────────────────────────────────────────────────────────────
    c.execute("""
        INSERT INTO processamentos (data_ini, data_fim, total_registos, obs)
        VALUES (?, ?, ?, ?)
    """, data_ini, data_fim, processados,
        (f"Processados: {processados} | "
         f"Ignorados: {ignorados} (sem plano: {sem_plano}, folgas: {folgas}) | "
         f"Colaboradores: {len(ids_afectados)}"))

    conn.commit()
    conn.close()

    return {
        "inseridos":               processados,
        "ignorados":               ignorados,
        "colaboradores_afectados": len(ids_afectados),
    }
