"""main.py
Aplicação Flask — JogoIDOnics (versão de teste).
Rotas: login, dashboard, utilizadores, pontos, reprocessar, relatório, sincronização.
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, date, timedelta
from base_dados import ligar_jogo
from auth import hash_senha, verificar_senha, login_obrigatorio
from jogo import sincronizar_colaboradores, reprocessar

app = Flask(__name__)
app.secret_key = "jogo_idonics_chave_secreta_2026"


# ─── Autenticação ────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        senha    = request.form.get("senha", "")

        conn = ligar_jogo()
        c = conn.cursor()
        c.execute("SELECT password_hash, tipo FROM contas WHERE username = ?", username)
        conta = c.fetchone()
        conn.close()

        if conta and verificar_senha(senha, conta[0]):
            session["utilizador"] = username
            session["tipo"]       = conta[1]
            return redirect(url_for("dashboard"))

        flash("Utilizador ou senha incorrectos.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ─── Dashboard ───────────────────────────────────────────────────────────────

@app.route("/")
@app.route("/dashboard")
@login_obrigatorio
def dashboard():
    conn = ligar_jogo()
    c = conn.cursor()

    # Top 15 por pontos
    c.execute("""
        SELECT c.id, c.nome_disp, c.pontos_total, d.nome AS departamento
        FROM colaboradores c
        LEFT JOIN departamentos d ON d.id = c.id_departamento
        WHERE c.activo = 1
        ORDER BY c.pontos_total DESC
        OFFSET 0 ROWS FETCH NEXT 15 ROWS ONLY
    """)
    top15 = [
        {"id": r[0], "nome": r[1] or "—", "pontos": r[2], "departamento": r[3] or "—"}
        for r in c.fetchall()
    ]

    # Estatísticas gerais
    c.execute("SELECT COUNT(*) FROM colaboradores WHERE activo = 1")
    total_colaboradores = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM colaboradores WHERE activo = 1 AND pontos_total > 0")
    com_pontos_positivos = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM colaboradores WHERE activo = 1 AND pontos_total < 0")
    com_pontos_negativos = c.fetchone()[0]

    # Último processamento
    c.execute("""
        SELECT TOP 1 data_ini, data_fim, total_registos, data_execucao, obs
        FROM processamentos ORDER BY data_execucao DESC
    """)
    ultimo_proc = c.fetchone()
    if ultimo_proc:
        ultimo_proc = {
            "data_ini":    ultimo_proc[0],
            "data_fim":    ultimo_proc[1],
            "total":       ultimo_proc[2],
            "executado_em": ultimo_proc[3],
            "obs":         ultimo_proc[4]
        }

    conn.close()

    return render_template("dashboard.html",
        top15=top15,
        total_colaboradores=total_colaboradores,
        com_pontos_positivos=com_pontos_positivos,
        com_pontos_negativos=com_pontos_negativos,
        ultimo_proc=ultimo_proc
    )


# ─── Utilizadores ────────────────────────────────────────────────────────────

@app.route("/utilizadores")
@login_obrigatorio
def utilizadores():
    conn = ligar_jogo()
    c = conn.cursor()

    # Filtro por departamento
    id_dept = request.args.get("departamento", "")
    pesquisa = request.args.get("pesquisa", "").strip()

    query = """
        SELECT c.id, c.nome, c.nome_disp, c.numero, c.pontos_total,
               d.nome AS departamento, c.id_departamento
        FROM colaboradores c
        LEFT JOIN departamentos d ON d.id = c.id_departamento
        WHERE c.activo = 1
    """
    params = []

    if id_dept:
        query += " AND c.id_departamento = ?"
        params.append(int(id_dept))

    if pesquisa:
        query += " AND (c.nome LIKE ? OR c.nome_disp LIKE ? OR c.numero LIKE ?)"
        params += [f"%{pesquisa}%", f"%{pesquisa}%", f"%{pesquisa}%"]

    query += " ORDER BY c.nome_disp"

    c.execute(query, params)
    colaboradores = [
        {
            "id":            r[0],
            "nome":          r[1] or "—",
            "nome_disp":     r[2] or "—",
            "numero":        r[3] or "—",
            "pontos":        r[4],
            "departamento":  r[5] or "—",
            "id_departamento": r[6]
        }
        for r in c.fetchall()
    ]

    # Lista de departamentos para o filtro
    c.execute("SELECT id, nome FROM departamentos ORDER BY nome")
    departamentos = [{"id": r[0], "nome": r[1]} for r in c.fetchall()]

    conn.close()

    return render_template("utilizadores.html",
        colaboradores=colaboradores,
        departamentos=departamentos,
        id_dept_sel=id_dept,
        pesquisa=pesquisa
    )


@app.route("/utilizador/<int:id_colab>")
@login_obrigatorio
def utilizador_detalhe(id_colab):
    conn = ligar_jogo()
    c = conn.cursor()

    # Dados do colaborador
    c.execute("""
        SELECT c.id, c.nome, c.nome_disp, c.numero, c.pontos_total,
               d.nome AS departamento, c.data_sync
        FROM colaboradores c
        LEFT JOIN departamentos d ON d.id = c.id_departamento
        WHERE c.id = ?
    """, id_colab)
    r = c.fetchone()
    if not r:
        conn.close()
        flash("Colaborador não encontrado.", "warning")
        return redirect(url_for("utilizadores"))

    colaborador = {
        "id":          r[0],
        "nome":        r[1] or "—",
        "nome_disp":   r[2] or "—",
        "numero":      r[3] or "—",
        "pontos":      r[4],
        "departamento": r[5] or "—",
        "data_sync":   r[6]
    }

    # Últimos 30 registos de pontos
    c.execute("""
        SELECT TOP 30 tarefa, pontos, obs, data_pontos
        FROM pontos
        WHERE id_colaborador = ?
        ORDER BY data_pontos DESC
    """, id_colab)
    historico = [
        {"tarefa": r[0], "pontos": r[1], "obs": r[2], "data": r[3]}
        for r in c.fetchall()
    ]

    # Resumo: positivos e negativos
    c.execute("""
        SELECT
            SUM(CASE WHEN pontos > 0 THEN pontos ELSE 0 END),
            SUM(CASE WHEN pontos < 0 THEN pontos ELSE 0 END),
            COUNT(*)
        FROM pontos WHERE id_colaborador = ?
    """, id_colab)
    r = c.fetchone()
    resumo = {
        "positivos": r[0] or 0,
        "negativos": r[1] or 0,
        "total_registos": r[2] or 0
    }

    conn.close()
    return render_template("utilizador_detalhe.html",
        colaborador=colaborador,
        historico=historico,
        resumo=resumo
    )


# ─── Pontos (histórico global) ────────────────────────────────────────────────

@app.route("/pontos")
@login_obrigatorio
def pontos():
    conn = ligar_jogo()
    c = conn.cursor()

    data_ini = request.args.get("data_ini", "")
    data_fim = request.args.get("data_fim", "")
    id_dept  = request.args.get("departamento", "")

    query = """
        SELECT TOP 200
            p.tarefa, p.pontos, p.obs, p.data_pontos,
            c.nome_disp, c.id, d.nome AS departamento
        FROM pontos p
        JOIN colaboradores c ON c.id = p.id_colaborador
        LEFT JOIN departamentos d ON d.id = c.id_departamento
        WHERE 1=1
    """
    params = []

    if data_ini:
        query += " AND p.data_pontos >= ?"
        params.append(data_ini)
    if data_fim:
        query += " AND p.data_pontos < DATEADD(day, 1, CAST(? AS DATE))"
        params.append(data_fim)
    if id_dept:
        query += " AND c.id_departamento = ?"
        params.append(int(id_dept))

    query += " ORDER BY p.data_pontos DESC"

    c.execute(query, params)
    registos = [
        {
            "tarefa":       r[0],
            "pontos":       r[1],
            "obs":          r[2],
            "data":         r[3],
            "colaborador":  r[4] or "—",
            "id_colab":     r[5],
            "departamento": r[6] or "—"
        }
        for r in c.fetchall()
    ]

    c.execute("SELECT id, nome FROM departamentos ORDER BY nome")
    departamentos = [{"id": r[0], "nome": r[1]} for r in c.fetchall()]

    conn.close()
    return render_template("pontos.html",
        registos=registos,
        departamentos=departamentos,
        data_ini=data_ini,
        data_fim=data_fim,
        id_dept_sel=id_dept
    )


# ─── Reprocessar ─────────────────────────────────────────────────────────────

@app.route("/reprocessar", methods=["GET", "POST"])
@login_obrigatorio
def reprocessar_view():
    conn = ligar_jogo()
    c = conn.cursor()

    # Histórico de processamentos
    c.execute("""
        SELECT TOP 10 data_ini, data_fim, total_registos, data_execucao, obs
        FROM processamentos ORDER BY data_execucao DESC
    """)
    historico = [
        {
            "data_ini":    r[0],
            "data_fim":    r[1],
            "total":       r[2],
            "executado_em": r[3],
            "obs":         r[4]
        }
        for r in c.fetchall()
    ]
    conn.close()

    resultado = None

    if request.method == "POST":
        data_ini = request.form.get("data_ini", "").strip()
        data_fim = request.form.get("data_fim", "").strip()

        if not data_ini or not data_fim:
            flash("Preenche as datas de início e fim.", "warning")
        elif data_ini > data_fim:
            flash("A data de início não pode ser posterior à data de fim.", "warning")
        else:
            resultado = reprocessar(data_ini, data_fim)
            if "erro" in resultado:
                flash(resultado["erro"], "danger")
            else:
                flash(
                    f"Concluído: {resultado['inseridos']} registos processados, "
                    f"{resultado['ignorados']} ignorados (folga), "
                    f"{resultado['colaboradores_afectados']} colaboradores afectados.",
                    "success"
                )
            return redirect(url_for("reprocessar_view"))

    # Sugerir datas: primeiro e último dia do mês actual
    hoje = date.today()
    data_ini_sugerida = hoje.replace(day=1).strftime("%Y-%m-%d")
    data_fim_sugerida = hoje.strftime("%Y-%m-%d")

    return render_template("reprocessar.html",
        historico=historico,
        data_ini_sugerida=data_ini_sugerida,
        data_fim_sugerida=data_fim_sugerida
    )


# ─── Relatório por departamento ───────────────────────────────────────────────

@app.route("/relatorio")
@login_obrigatorio
def relatorio():
    conn = ligar_jogo()
    c = conn.cursor()

    # Período: mês actual por defeito
    hoje = date.today()
    data_ini = request.args.get("data_ini", hoje.replace(day=1).strftime("%Y-%m-%d"))
    data_fim = request.args.get("data_fim", hoje.strftime("%Y-%m-%d"))

    # Resumo por departamento
    c.execute("""
        SELECT
            d.nome AS departamento,
            COUNT(DISTINCT c.id) AS total_colaboradores,
            SUM(CASE WHEN p.pontos > 0 THEN p.pontos ELSE 0 END) AS total_positivos,
            SUM(CASE WHEN p.pontos < 0 THEN p.pontos ELSE 0 END) AS total_negativos,
            SUM(p.pontos) AS saldo
        FROM colaboradores c
        LEFT JOIN departamentos d ON d.id = c.id_departamento
        LEFT JOIN pontos p ON p.id_colaborador = c.id
            AND p.data_pontos >= ?
            AND p.data_pontos < DATEADD(day, 1, CAST(? AS DATE))
        WHERE c.activo = 1
        GROUP BY d.nome
        ORDER BY saldo DESC
    """, data_ini, data_fim)

    por_departamento = [
        {
            "departamento":        r[0] or "Sem departamento",
            "total_colaboradores": r[1],
            "positivos":           r[2] or 0,
            "negativos":           r[3] or 0,
            "saldo":               r[4] or 0
        }
        for r in c.fetchall()
    ]

    # Top 10 e Bottom 10 do período
    c.execute("""
        SELECT TOP 10
            c.nome_disp, c.id,
            SUM(p.pontos) AS saldo,
            d.nome AS departamento
        FROM colaboradores c
        LEFT JOIN departamentos d ON d.id = c.id_departamento
        LEFT JOIN pontos p ON p.id_colaborador = c.id
            AND p.data_pontos >= ?
            AND p.data_pontos < DATEADD(day, 1, CAST(? AS DATE))
        WHERE c.activo = 1
        GROUP BY c.nome_disp, c.id, d.nome
        HAVING SUM(p.pontos) IS NOT NULL
        ORDER BY saldo DESC
    """, data_ini, data_fim)
    top10 = [
        {"nome": r[0] or "—", "id": r[1], "saldo": r[2], "departamento": r[3] or "—"}
        for r in c.fetchall()
    ]

    c.execute("""
        SELECT TOP 10
            c.nome_disp, c.id,
            SUM(p.pontos) AS saldo,
            d.nome AS departamento
        FROM colaboradores c
        LEFT JOIN departamentos d ON d.id = c.id_departamento
        LEFT JOIN pontos p ON p.id_colaborador = c.id
            AND p.data_pontos >= ?
            AND p.data_pontos < DATEADD(day, 1, CAST(? AS DATE))
        WHERE c.activo = 1
        GROUP BY c.nome_disp, c.id, d.nome
        HAVING SUM(p.pontos) IS NOT NULL
        ORDER BY saldo ASC
    """, data_ini, data_fim)
    bottom10 = [
        {"nome": r[0] or "—", "id": r[1], "saldo": r[2], "departamento": r[3] or "—"}
        for r in c.fetchall()
    ]

    conn.close()
    return render_template("relatorio.html",
        por_departamento=por_departamento,
        top10=top10,
        bottom10=bottom10,
        data_ini=data_ini,
        data_fim=data_fim
    )


# ─── Sincronizar colaboradores (chamada AJAX/form) ────────────────────────────

@app.route("/admin/sincronizar", methods=["POST"])
@login_obrigatorio
def sincronizar():
    resultado = sincronizar_colaboradores()
    flash(
        f"Sincronização concluída: {resultado['colaboradores']} colaboradores activos, "
        f"{resultado['departamentos']} departamentos, "
        f"{resultado['inactivados']} marcados como inactivos (ex-funcionários/externos).",
        "success"
    )
    return redirect(request.referrer or url_for("utilizadores"))


# ─── Arranque ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)
