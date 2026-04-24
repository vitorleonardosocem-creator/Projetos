"""
=============================================================
  main.py  —  JogoScore (FastAPI)
=============================================================
  Aplicação unificada que combina:
    - JogoSocem (pontos via SINEX → jogo_socem)
    - JogoIDOnics (pontos via IDOntime → jogo_idonics)

  Porta: 8005
  Login: jogo_score.contas (BD unificada)

  Leaderboard: combina utilizadores dos dois sistemas.
    → Utilizadores duplicados (sinex_employee_id == numero)
      aparecem UMA VEZ com pontos somados.

  Minha área: mostra pontos SINEX + pontos IDOntime + total.

  Loja: qualquer utilizador pode resgatar.
    → Desconto proporcional para utilizadores combinados.
=============================================================
"""

import uuid
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text
import urllib.parse
import pandas as pd
import pyodbc
import io
import os
from datetime import date, datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse as StarletteRedirect
from fastapi.responses import JSONResponse

from sinex_job import processar_intervalo as sinex_processar_intervalo
from idontime_job import (
    reprocessar_intervalo as idontime_processar_intervalo,
    sincronizar_colaboradores,
)
from auth import (
    get_session_user, create_session_token,
    hash_password, verify_password,
    SESSION_COOKIE, SESSION_MAX_AGE,
)


# ─────────────────────────────────────────────────────────────
#  APP
# ─────────────────────────────────────────────────────────────

app = FastAPI(title="JogoScore SOCEM")
templates = Jinja2Templates(directory="templates")


# ─────────────────────────────────────────────────────────────
#  STRINGS DE LIGAÇÃO
# ─────────────────────────────────────────────────────────────

CONN_SOCEM = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=jogo_socem;"
    "UID=GV;PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)

CONN_IDONICS = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=jogo_idonics;"
    "UID=GV;PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)

CONN_SCORE = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=jogo_score;"
    "UID=GV;PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)

# SQLAlchemy engines (para pandas)
engine_socem   = create_engine(f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(CONN_SOCEM)}")
engine_idonics = create_engine(f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(CONN_IDONICS)}")
engine_score   = create_engine(f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(CONN_SCORE)}")


# ─────────────────────────────────────────────────────────────
#  LEADERBOARD UNIFICADO (helper)
# ─────────────────────────────────────────────────────────────

def obter_leaderboard_unificado() -> list:
    """
    Combina utilizadores dos dois sistemas.
    Quando sinex_employee_id == colaboradores.numero → mesma pessoa,
    aparece UMA VEZ com pontos somados.

    Devolve lista de dicts ordenada por pontos_total DESC.
    """
    # Utilizadores SINEX
    with engine_socem.connect() as conn:
        df_sinex = pd.read_sql(text("""
            SELECT u.id, u.nome,
                   ISNULL(u.sinex_employee_id, '') as sinex_employee_id,
                   ISNULL(u.pontos_total, 0)        as pontos_sinex,
                   ISNULL(d.nome, 'Sem Dept')        as departamento,
                   ISNULL(e.nome, 'Sem Equipa')      as equipa
            FROM users u
            LEFT JOIN departamentos d ON d.id = u.departamento_id
            LEFT JOIN equipas e ON e.id = u.equipa_id
        """), conn)

    # Colaboradores IDOntime
    with engine_idonics.connect() as conn:
        df_idonics = pd.read_sql(text("""
            SELECT c.id, c.nome,
                   ISNULL(c.numero, '')              as numero,
                   ISNULL(c.pontos_total, 0)          as pontos_idonics,
                   ISNULL(d.nome, 'Sem Dept')         as departamento
            FROM colaboradores c
            LEFT JOIN departamentos d ON d.id = c.id_departamento
            WHERE c.activo = 1
        """), conn)

    # Mapa: numero_idonics → pontos + nome
    mapa_idonics = {}
    for _, row in df_idonics.iterrows():
        num = str(row["numero"]).strip()
        if num:
            mapa_idonics[num] = {
                "id_idonics":    int(row["id"]),
                "nome_idonics":  str(row["nome"]),
                "pontos_idonics": int(row["pontos_idonics"]),
                "dept_idonics":  str(row["departamento"]),
            }

    usados_idonics = set()  # números IDOntime já somados a um user SINEX
    resultado = []

    for _, row in df_sinex.iterrows():
        emp_id = str(row["sinex_employee_id"]).strip()
        pontos_sinex   = int(row["pontos_sinex"])
        pontos_idonics = 0
        id_idonics     = None

        if emp_id and emp_id in mapa_idonics:
            # Utilizador duplicado → somar pontos
            info_id = mapa_idonics[emp_id]
            pontos_idonics = info_id["pontos_idonics"]
            id_idonics     = info_id["id_idonics"]
            usados_idonics.add(emp_id)

        resultado.append({
            "id":            int(row["id"]),
            "id_idonics":    id_idonics,
            "nome":          str(row["nome"]),
            "departamento":  str(row["departamento"]),
            "equipa":        str(row["equipa"]),
            "pontos_sinex":  pontos_sinex,
            "pontos_idonics": pontos_idonics,
            "pontos_total":  pontos_sinex + pontos_idonics,
            "fonte":         "sinex",
        })

    # Colaboradores IDOntime que NÃO estão no SINEX
    for _, row in df_idonics.iterrows():
        num = str(row["numero"]).strip()
        if num in usados_idonics:
            continue  # já foi somado ao utilizador SINEX
        resultado.append({
            "id":            None,
            "id_idonics":    int(row["id"]),
            "nome":          str(row["nome"]),
            "departamento":  str(row["departamento"]),
            "equipa":        "—",
            "pontos_sinex":  0,
            "pontos_idonics": int(row["pontos_idonics"]),
            "pontos_total":  int(row["pontos_idonics"]),
            "fonte":         "idontime",
        })

    # Ordenar por pontos_total DESC
    resultado.sort(key=lambda x: x["pontos_total"], reverse=True)

    # Atribuir posição
    for i, item in enumerate(resultado, start=1):
        item["posicao"] = i

    return resultado


# ─────────────────────────────────────────────────────────────
#  MIDDLEWARE DE AUTENTICAÇÃO
# ─────────────────────────────────────────────────────────────

PUBLIC_PATHS  = {"/login", "/logout", "/tv", "/leaderboard-json"}
USER_PATHS    = {"/minha-area", "/loja"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path.startswith("/static") or path in PUBLIC_PATHS:
            request.state.user = get_session_user(request)
            return await call_next(request)

        user = get_session_user(request)
        request.state.user = user

        if not user:
            return StarletteRedirect(f"/login?next={path}")

        if user.get("tipo") == "user":
            permitido = (
                path in USER_PATHS
                or path.startswith("/loja")
                or path.startswith("/minha-area")
                or path.startswith("/colaborador")
                or path.startswith("/departamentos")
                or path.startswith("/departamento")
                or path == "/historico"
                or path == "/tv"
            )
            if not permitido:
                return StarletteRedirect("/minha-area")

        return await call_next(request)


app.add_middleware(AuthMiddleware)


# ─────────────────────────────────────────────────────────────
#  LOGIN / LOGOUT
# ─────────────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request, next: str = "/"):
    user = get_session_user(request)
    if user:
        return RedirectResponse("/minha-area" if user.get("tipo") == "user" else "/")
    return templates.TemplateResponse("login.html", {
        "request": request, "next": next, "erro": ""
    })


@app.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
):
    try:
        conn = pyodbc.connect(CONN_SCORE)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, username, password_hash, tipo,
                      sinex_user_id, idontime_colaborador_id
               FROM contas WHERE username = ?""",
            (username.strip(),)
        )
        row = cursor.fetchone()
        conn.close()
    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request, "next": next,
            "erro": f"Erro de ligação: {e}"
        })

    if not row or not verify_password(password, row.password_hash):
        return templates.TemplateResponse("login.html", {
            "request": request, "next": next,
            "erro": "Utilizador ou password incorretos."
        })

    session_data = {
        "conta_id":               int(row.id),
        "username":               row.username,
        "tipo":                   row.tipo,
        "sinex_user_id":          int(row.sinex_user_id) if row.sinex_user_id else None,
        "idontime_colaborador_id": int(row.idontime_colaborador_id) if row.idontime_colaborador_id else None,
    }
    token = create_session_token(session_data)

    destino = next if next and next != "/" else (
        "/minha-area" if row.tipo == "user" else "/"
    )
    response = RedirectResponse(destino, status_code=303)
    response.set_cookie(
        SESSION_COOKIE, token,
        max_age=SESSION_MAX_AGE, httponly=True, samesite="lax"
    )
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


# ─────────────────────────────────────────────────────────────
#  DASHBOARD (leaderboard unificado)
# ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        leaderboard = obter_leaderboard_unificado()

        total_users = len(leaderboard)
        top1 = leaderboard[0] if leaderboard else None

        # Contagens totais
        total_sinex   = sum(1 for u in leaderboard if u["fonte"] == "sinex" or u["pontos_sinex"] > 0)
        total_idonics = sum(1 for u in leaderboard if u["fonte"] == "idontime" or u["pontos_idonics"] > 0)

    except Exception as e:
        return f"Erro Dashboard: {e}<br><a href='/'>Tentar novamente</a>"

    return templates.TemplateResponse("demo.html", {
        "request":      request,
        "leaderboard":  leaderboard,
        "total_users":  total_users,
        "top1":         top1,
        "total_sinex":  total_sinex,
        "total_idonics": total_idonics,
    })


@app.get("/leaderboard-json")
async def leaderboard_json():
    try:
        return obter_leaderboard_unificado()
    except Exception:
        return []


# ─────────────────────────────────────────────────────────────
#  TV DASHBOARD
# ─────────────────────────────────────────────────────────────

@app.get("/tv", response_class=HTMLResponse)
async def tv_dashboard(request: Request):
    try:
        leaderboard = obter_leaderboard_unificado()
        top5 = leaderboard[:5]

        # Departamentos — agrega pontos de ambos os sistemas
        with engine_socem.connect() as conn:
            depts_sinex = pd.read_sql(text("""
                SELECT ISNULL(d.nome, 'Sem Dept') as departamento,
                       COUNT(u.id) as total_users,
                       ISNULL(SUM(u.pontos_total), 0) as total_pontos
                FROM departamentos d
                LEFT JOIN users u ON u.departamento_id = d.id
                GROUP BY d.nome
            """), conn).to_dict("records")

    except Exception as e:
        return f"<h1>Erro TV: {e}</h1>"

    return templates.TemplateResponse("tv.html", {
        "request": request,
        "top5":    top5,
        "depts":   depts_sinex,
    })


# ─────────────────────────────────────────────────────────────
#  MINHA ÁREA (utilizador normal)
# ─────────────────────────────────────────────────────────────

@app.get("/minha-area", response_class=HTMLResponse)
async def minha_area(request: Request, msg: str = ""):
    session = request.state.user
    if not session:
        return RedirectResponse("/login")

    sinex_uid  = session.get("sinex_user_id")
    idon_uid   = session.get("idontime_colaborador_id")

    # Conta sem utilizador associado (ex: admin puro)
    if not sinex_uid and not idon_uid:
        return templates.TemplateResponse("minha_area.html", {
            "request": request, "colaborador": None,
            "eventos_sinex": [], "eventos_idonics": [],
            "pos_geral": "-", "total_users": "-",
            "recompensas": [], "msg": msg,
        })

    colaborador  = {}
    eventos_sinex   = []
    eventos_idonics = []
    pontos_sinex    = 0
    pontos_idonics  = 0

    try:
        # Dados SINEX
        if sinex_uid:
            with engine_socem.connect() as conn:
                df = pd.read_sql(text("""
                    SELECT u.id, u.nome,
                           ISNULL(u.pontos_total, 0) as pontos_total,
                           ISNULL(u.ferias_ganhas, 0) as ferias_ganhas,
                           ISNULL(d.nome, 'Sem Dept') as departamento,
                           ISNULL(e.nome, 'Sem Equipa') as equipa
                    FROM users u
                    LEFT JOIN departamentos d ON d.id = u.departamento_id
                    LEFT JOIN equipas e ON e.id = u.equipa_id
                    WHERE u.id = :uid
                """), conn, params={"uid": sinex_uid})

                if not df.empty:
                    colaborador = df.iloc[0].to_dict()
                    pontos_sinex = int(colaborador.get("pontos_total", 0))

                eventos_sinex = pd.read_sql(text("""
                    SELECT TOP 15 tarefa, pontos,
                           FORMAT(data_pontos, 'dd/MM/yyyy') as data_fmt
                    FROM pontos
                    WHERE user_id = :uid
                    ORDER BY data_pontos DESC, id DESC
                """), conn, params={"uid": sinex_uid}).to_dict("records")

        # Dados IDOntime
        if idon_uid:
            with engine_idonics.connect() as conn:
                df_id = pd.read_sql(text("""
                    SELECT c.id, c.nome,
                           ISNULL(c.pontos_total, 0) as pontos_total,
                           ISNULL(d.nome, 'Sem Dept') as departamento
                    FROM colaboradores c
                    LEFT JOIN departamentos d ON d.id = c.id_departamento
                    WHERE c.id = :uid
                """), conn, params={"uid": idon_uid})

                if not df_id.empty:
                    pontos_idonics = int(df_id.iloc[0]["pontos_total"])
                    # Se não tem dados SINEX, usa os do IDOntime
                    if not colaborador:
                        colaborador = df_id.iloc[0].to_dict()
                        colaborador["equipa"] = "—"
                        colaborador["ferias_ganhas"] = 0

                eventos_idonics = pd.read_sql(text("""
                    SELECT TOP 15 tarefa, pontos,
                           FORMAT(data_pontos, 'dd/MM/yyyy HH:mm') as data_fmt
                    FROM pontos
                    WHERE id_colaborador = :uid
                    ORDER BY data_pontos DESC, id DESC
                """), conn, params={"uid": idon_uid}).to_dict("records")

        # Total combinado
        pontos_total_combinado = pontos_sinex + pontos_idonics
        colaborador["pontos_sinex"]   = pontos_sinex
        colaborador["pontos_idonics"] = pontos_idonics
        colaborador["pontos_total"]   = pontos_total_combinado
        colaborador["tem_ambos"]      = bool(sinex_uid and idon_uid)

        # Ranking (baseado no leaderboard unificado)
        leaderboard = obter_leaderboard_unificado()
        total_users = len(leaderboard)
        pos_geral   = next(
            (i + 1 for i, u in enumerate(leaderboard)
             if (sinex_uid and u.get("id") == sinex_uid)
             or (idon_uid and u.get("id_idonics") == idon_uid)),
            "-"
        )

        # Recompensas disponíveis
        with engine_socem.connect() as conn:
            recompensas = pd.read_sql(text(
                "SELECT id, nome, descricao, custo_pontos FROM recompensas WHERE ativo = 1 ORDER BY custo_pontos"
            ), conn).to_dict("records")

    except Exception as e:
        return f"<h1>Erro minha-area: {e}</h1>"

    return templates.TemplateResponse("minha_area.html", {
        "request":        request,
        "colaborador":    colaborador,
        "eventos_sinex":  eventos_sinex,
        "eventos_idonics": eventos_idonics,
        "pos_geral":      pos_geral,
        "total_users":    total_users,
        "recompensas":    recompensas,
        "msg":            msg,
    })


# ─────────────────────────────────────────────────────────────
#  COLABORADOR (perfil público)
# ─────────────────────────────────────────────────────────────

@app.get("/colaborador/{user_id}", response_class=HTMLResponse)
async def pagina_colaborador(request: Request, user_id: int):
    try:
        with engine_socem.connect() as conn:
            df = pd.read_sql(text("""
                SELECT u.id, u.nome, u.pontos_total, u.ferias_ganhas,
                       ISNULL(d.nome, 'Sem Dept') as departamento,
                       ISNULL(e.nome, 'Sem Equipa') as equipa
                FROM users u
                LEFT JOIN departamentos d ON d.id = u.departamento_id
                LEFT JOIN equipas e ON e.id = u.equipa_id
                WHERE u.id = :uid
            """), conn, params={"uid": user_id})

            if df.empty:
                return f"<h1>❌ Colaborador não encontrado</h1><a href='/'>← Dashboard</a>"

            user = df.iloc[0].to_dict()
            dept_nome = user["departamento"]

            eventos = pd.read_sql(text("""
                SELECT TOP 20 tarefa as tipo, pontos,
                       FORMAT(data_pontos, 'dd/MM/yyyy') as data_evento
                FROM pontos
                WHERE user_id = :u
                ORDER BY data_pontos DESC, id DESC
            """), conn, params={"u": user_id}).to_dict("records")

            ranking_dept = pd.read_sql(text("""
                SELECT u.id, RANK() OVER (ORDER BY u.pontos_total DESC) as pos
                FROM users u
                INNER JOIN departamentos d ON u.departamento_id = d.id
                WHERE d.nome = :d
            """), conn, params={"d": dept_nome})
            pos_arr = ranking_dept[ranking_dept["id"] == user_id]["pos"].values
            pos_dept = int(pos_arr[0]) if len(pos_arr) > 0 else "-"

            ranking_geral = pd.read_sql(text("""
                SELECT id, RANK() OVER (ORDER BY pontos_total DESC) as pos FROM users
            """), conn)
            pos_g_arr = ranking_geral[ranking_geral["id"] == user_id]["pos"].values
            pos_geral = int(pos_g_arr[0]) if len(pos_g_arr) > 0 else "-"

    except Exception as e:
        return f"<h1>Erro colaborador: {e}</h1><a href='/'>← Dashboard</a>"

    return templates.TemplateResponse("Colaborador.html", {
        "request": request,
        "user":     user,
        "eventos":  eventos,
        "pos_dept": pos_dept,
        "pos_geral": pos_geral,
    })


# ─────────────────────────────────────────────────────────────
#  DEPARTAMENTOS
# ─────────────────────────────────────────────────────────────

@app.get("/departamentos", response_class=HTMLResponse)
async def lista_departamentos(request: Request):
    """
    Lista unificada de departamentos — combina SINEX + IDOntime.
    Usa o leaderboard unificado para garantir que utilizadores duplicados
    não são contados duas vezes e ficam no departamento SINEX.
    """
    try:
        leaderboard = obter_leaderboard_unificado()

        # Agrupar por departamento a partir do leaderboard
        depts: dict = {}
        for user in leaderboard:
            dept = user["departamento"] or "Sem Dept"
            if dept not in depts:
                depts[dept] = {
                    "nome":         dept,
                    "total_users":  0,
                    "total_pontos": 0.0,
                    "media_pontos": 0.0,
                }
            depts[dept]["total_users"]  += 1
            depts[dept]["total_pontos"] += float(user["pontos_total"])

        # Calcular médias
        for d in depts.values():
            d["media_pontos"] = d["total_pontos"] / d["total_users"] if d["total_users"] > 0 else 0.0

        departamentos = sorted(depts.values(), key=lambda x: x["total_pontos"], reverse=True)
        total_users   = len(leaderboard)
        total_pontos  = sum(d["total_pontos"] for d in departamentos)

    except Exception as e:
        return f"<h1>Erro departamentos: {e}</h1>"

    return templates.TemplateResponse("Departamentos_lista.html", {
        "request":       request,
        "departamentos": departamentos,
        "total_depts":   len(departamentos),
        "total_users":   total_users,
        "total_pontos":  total_pontos,
    })


@app.get("/departamento/{nome}", response_class=HTMLResponse)
async def departamento_detalhe(nome: str, request: Request):
    """
    Detalhe de um departamento — mostra colaboradores de ambos os sistemas.
    Duplicados aparecem uma vez com pontos somados (dept SINEX prevalece).
    """
    try:
        leaderboard = obter_leaderboard_unificado()

        # Filtrar colaboradores deste departamento
        users_dept = [
            u for u in leaderboard
            if (u["departamento"] or "Sem Dept") == nome
        ]

        if not users_dept and nome != "Sem Dept":
            return f"<h1>❌ Departamento '{nome}' não encontrado</h1><a href='/departamentos'>← Lista</a>"

        total_users  = len(users_dept)
        total_pontos = sum(float(u["pontos_total"]) for u in users_dept)
        media_pontos = total_pontos / total_users if total_users > 0 else 0.0

    except Exception as e:
        return f"<h1>Erro dept: {e}</h1>"

    return templates.TemplateResponse("departamentos.html", {
        "request":      request,
        "nome_dept":    nome,
        "users_dept":   users_dept,
        "total_users":  total_users,
        "total_pontos": total_pontos,
        "media_pontos": media_pontos,
    })


# ─────────────────────────────────────────────────────────────
#  LOJA DE PONTOS
# ─────────────────────────────────────────────────────────────

@app.get("/loja", response_class=HTMLResponse)
async def loja_get(request: Request, msg: str = ""):
    try:
        with engine_socem.connect() as conn:
            recompensas = pd.read_sql(text(
                "SELECT id, nome, descricao, custo_pontos FROM recompensas WHERE ativo = 1 ORDER BY custo_pontos"
            ), conn).to_dict("records")

        # Leaderboard para dropdown (qualquer utilizador pode resgatar)
        leaderboard = obter_leaderboard_unificado()

    except Exception as e:
        return f"<h1>Erro loja: {e}</h1>"

    return templates.TemplateResponse("loja.html", {
        "request":    request,
        "recompensas": recompensas,
        "users":      leaderboard,
        "msg":        msg,
    })


@app.post("/loja/resgatar")
async def loja_resgatar(
    request: Request,
    sinex_user_id: str = Form(""),
    idontime_colaborador_id: str = Form(""),
    recompensa_id: int = Form(...),
):
    """
    Resgate de recompensa com desconto proporcional.
    Aceita utilizadores SINEX, IDOntime ou combinados.
    """
    session = request.state.user
    destino_ok  = "/minha-area" if session and session.get("tipo") == "user" else "/loja"
    destino_err = destino_ok

    sinex_uid = int(sinex_user_id) if sinex_user_id.strip() else None
    idon_uid  = int(idontime_colaborador_id) if idontime_colaborador_id.strip() else None

    if not sinex_uid and not idon_uid:
        return RedirectResponse(f"{destino_err}?msg=Utilizador+nao+identificado", status_code=303)

    try:
        # Obter custo da recompensa
        with engine_socem.connect() as conn:
            rec = conn.execute(text(
                "SELECT nome, custo_pontos FROM recompensas WHERE id = :id AND ativo = 1"
            ), {"id": recompensa_id}).fetchone()
        if not rec:
            return RedirectResponse(f"{destino_err}?msg=Recompensa+nao+encontrada", status_code=303)

        custo = int(rec[1])
        nome_rec = rec[0]

        # Obter pontos actuais de cada lado
        pts_sinex   = 0
        pts_idonics = 0

        if sinex_uid:
            with engine_socem.connect() as conn:
                pts_sinex = conn.execute(text(
                    "SELECT ISNULL(pontos_total, 0) FROM users WHERE id = :id"
                ), {"id": sinex_uid}).scalar() or 0
            pts_sinex = int(pts_sinex)

        if idon_uid:
            with engine_idonics.connect() as conn:
                pts_idonics = conn.execute(text(
                    "SELECT ISNULL(pontos_total, 0) FROM colaboradores WHERE id = :id"
                ), {"id": idon_uid}).scalar() or 0
            pts_idonics = int(pts_idonics)

        pts_total = pts_sinex + pts_idonics

        if pts_total < custo:
            return RedirectResponse(f"{destino_err}?msg=Pontos+insuficientes+({pts_total}/{custo})", status_code=303)

        # Calcular desconto proporcional
        if sinex_uid and idon_uid:
            # Combinado: proporcional
            sinex_deduct  = round(custo * pts_sinex / pts_total) if pts_total > 0 else 0
            idonics_deduct = custo - sinex_deduct
        elif sinex_uid:
            sinex_deduct   = custo
            idonics_deduct = 0
        else:
            sinex_deduct   = 0
            idonics_deduct = custo

        # Aplicar desconto SINEX
        if sinex_uid and sinex_deduct > 0:
            conn_s = pyodbc.connect(CONN_SOCEM)
            cur_s  = conn_s.cursor()
            cur_s.execute("UPDATE users SET pontos_total = pontos_total - ? WHERE id = ?",
                          (sinex_deduct, sinex_uid))
            cur_s.execute("""
                INSERT INTO resgates
                    (user_id, recompensa_id, pontos_gastos, estado,
                     idontime_colaborador_id, pontos_gastos_idontime)
                VALUES (?, ?, ?, 'pendente', ?, ?)
            """, (sinex_uid, recompensa_id, sinex_deduct,
                  idon_uid, idonics_deduct if idon_uid else 0))
            cur_s.execute("""
                INSERT INTO eventos (user_id, tipo, pontos) VALUES (?, ?, ?)
            """, (sinex_uid, f"loja: {nome_rec}", -sinex_deduct))
            conn_s.commit()
            conn_s.close()
        elif idon_uid and not sinex_uid:
            # IDOntime puro: registo em resgates com user_id NULL
            conn_s = pyodbc.connect(CONN_SOCEM)
            cur_s  = conn_s.cursor()
            cur_s.execute("""
                INSERT INTO resgates
                    (user_id, recompensa_id, pontos_gastos, estado,
                     idontime_colaborador_id, pontos_gastos_idontime)
                VALUES (NULL, ?, 0, 'pendente', ?, ?)
            """, (recompensa_id, idon_uid, idonics_deduct))
            conn_s.commit()
            conn_s.close()

        # Aplicar desconto IDOntime
        if idon_uid and idonics_deduct > 0:
            conn_i = pyodbc.connect(CONN_IDONICS)
            cur_i  = conn_i.cursor()
            cur_i.execute("UPDATE colaboradores SET pontos_total = pontos_total - ? WHERE id = ?",
                          (idonics_deduct, idon_uid))
            conn_i.commit()
            conn_i.close()

        return RedirectResponse(f"{destino_ok}?msg=Resgatado+com+sucesso", status_code=303)

    except Exception as e:
        return RedirectResponse(f"{destino_err}?msg=Erro:{str(e)[:60]}", status_code=303)


# ─────────────────────────────────────────────────────────────
#  HISTÓRICO ANUAL
# ─────────────────────────────────────────────────────────────

@app.get("/historico", response_class=HTMLResponse)
async def historico_get(request: Request, msg: str = ""):
    try:
        with engine_socem.connect() as conn:
            anos = pd.read_sql(text(
                "SELECT DISTINCT ano FROM historico_anual ORDER BY ano DESC"
            ), conn)
            anos_list = [int(r) for r in anos["ano"].tolist()] if not anos.empty else []

            historico = pd.read_sql(text("""
                SELECT h.ano, u.nome,
                       ISNULL(d.nome, 'Sem Dept') as departamento,
                       h.pontos_total, h.ferias_ganhas,
                       FORMAT(h.data_snapshot, 'dd/MM/yyyy') as data_snapshot
                FROM historico_anual h
                INNER JOIN users u ON u.id = h.user_id
                LEFT JOIN departamentos d ON d.id = u.departamento_id
                ORDER BY h.ano DESC, h.pontos_total DESC
            """), conn).to_dict("records")
    except Exception as e:
        return f"<h1>Erro histórico: {e}</h1>"

    return templates.TemplateResponse("historico.html", {
        "request":   request,
        "historico": historico,
        "anos":      anos_list,
        "msg":       msg,
    })


@app.get("/fim_ano", response_class=HTMLResponse)
async def fim_ano_get(request: Request):
    try:
        with engine_socem.connect() as conn:
            qualif = pd.read_sql(text(
                "SELECT COUNT(*) as qtd FROM users WHERE pontos_total >= 10"
            ), conn).iloc[0, 0]
            total = pd.read_sql(text(
                "SELECT COUNT(*) as qtd FROM users"
            ), conn).iloc[0, 0]
    except Exception as e:
        return f"<h1>Erro: {e}</h1>"

    return templates.TemplateResponse("fim_ano.html", {
        "request":   request,
        "qualif":    int(qualif),
        "total":     int(total),
        "ano_atual": date.today().year,
    })


@app.post("/fim_ano")
async def fim_ano_post():
    try:
        ano = date.today().year
        with engine_socem.connect() as conn:
            conn.execute(text("""
                INSERT INTO historico_anual (user_id, ano, pontos_total, ferias_ganhas)
                SELECT id, :ano, ISNULL(pontos_total, 0), ISNULL(ferias_ganhas, 0)
                FROM users
            """), {"ano": ano})
            conn.execute(text(
                "UPDATE users SET ferias_ganhas = ferias_ganhas + 1 WHERE pontos_total >= 10"
            ))
            conn.execute(text("UPDATE users SET pontos_total = 0"))
            conn.commit()
            qualif = pd.read_sql(text(
                "SELECT COUNT(*) as qtd FROM users WHERE ferias_ganhas > 0"
            ), conn).iloc[0, 0]
        return RedirectResponse(
            f"/historico?msg=Reset+{ano}+concluido+{qualif}+colaboradores+ganharam+ferias",
            status_code=303
        )
    except Exception as e:
        return {"erro": str(e)}


# ─────────────────────────────────────────────────────────────
#  RELATÓRIO MENSAL
# ─────────────────────────────────────────────────────────────

@app.get("/admin/relatorio", response_class=HTMLResponse)
async def relatorio_get(request: Request):
    hoje = date.today()
    return templates.TemplateResponse("admin_relatorio.html", {
        "request":    request,
        "resultado":  None,
        "mes_default": hoje.month,
        "ano_default": hoje.year,
    })


@app.post("/admin/relatorio", response_class=HTMLResponse)
async def relatorio_post(request: Request, mes: int = Form(...), ano: int = Form(...)):
    try:
        with engine_socem.connect() as conn:
            # Pontos por colaborador no mês
            df = pd.read_sql(text("""
                SELECT u.id, u.nome,
                       ISNULL(d.nome, 'Sem Dept') as departamento,
                       ISNULL(SUM(p.pontos), 0)   as pontos_mes,
                       COUNT(CASE WHEN p.pontos > 0 THEN 1 END) as dias_positivos,
                       COUNT(CASE WHEN p.pontos < 0 THEN 1 END) as dias_negativos,
                       COUNT(p.id) as total_registos
                FROM users u
                LEFT JOIN departamentos d ON d.id = u.departamento_id
                LEFT JOIN pontos p ON p.user_id = u.id
                    AND MONTH(p.data_pontos) = :mes
                    AND YEAR(p.data_pontos)  = :ano
                    AND p.tarefa LIKE 'sinex_%'
                GROUP BY u.id, u.nome, d.nome
                ORDER BY pontos_mes DESC
            """), conn, params={"mes": mes, "ano": ano}).fillna(0)

            # Pontos por departamento no mês
            dept_stats = pd.read_sql(text("""
                SELECT ISNULL(d.nome, 'Sem Dept') as departamento,
                       COUNT(DISTINCT u.id)        as total_users,
                       ISNULL(SUM(p.pontos), 0)    as total_pontos
                FROM departamentos d
                LEFT JOIN users u ON u.departamento_id = d.id
                LEFT JOIN pontos p ON p.user_id = u.id
                    AND MONTH(p.data_pontos) = :mes
                    AND YEAR(p.data_pontos)  = :ano
                    AND p.tarefa LIKE 'sinex_%'
                GROUP BY d.nome
                ORDER BY total_pontos DESC
            """), conn, params={"mes": mes, "ano": ano}).fillna(0)

        colaboradores = df.to_dict("records")

        # Calcular média por departamento em Python (evita problemas de divisão no SQL)
        depts_rel = []
        for row in dept_stats.to_dict("records"):
            n    = int(row.get("total_users", 0)) or 1
            pts  = float(row.get("total_pontos", 0))
            row["media_pontos"] = round(pts / n, 1)
            depts_rel.append(row)

        # Colaborador com mais pontos no mês
        melhor = colaboradores[0] if colaboradores else None

        # Colaborador mais consistente = mais dias com pontos positivos
        mais_consistente = max(
            colaboradores, key=lambda c: int(c.get("dias_positivos", 0)), default=None
        ) if colaboradores else None

        resultado = {
            "mes":                 mes,
            "ano":                 ano,
            "colaboradores":       colaboradores,
            "depts":               depts_rel,
            "melhor":              melhor,
            "mais_consistente":    mais_consistente,
            "total_colaboradores": len(colaboradores),
        }
    except Exception as e:
        resultado = {"erro": str(e)}

    return templates.TemplateResponse("admin_relatorio.html", {
        "request":     request,
        "resultado":   resultado,
        "mes_default": mes,
        "ano_default": ano,
    })


@app.post("/admin/relatorio/exportar")
async def relatorio_exportar(mes: int = Form(...), ano: int = Form(...)):
    try:
        with engine_socem.connect() as conn:
            df = pd.read_sql(text("""
                SELECT u.nome as Colaborador,
                       ISNULL(d.nome, 'Sem Dept') as Departamento,
                       ISNULL(SUM(p.pontos), 0) as Pontos_Mes,
                       COUNT(CASE WHEN p.pontos > 0 THEN 1 END) as Dias_Positivos,
                       COUNT(CASE WHEN p.pontos < 0 THEN 1 END) as Dias_Negativos
                FROM users u
                LEFT JOIN departamentos d ON d.id = u.departamento_id
                LEFT JOIN pontos p ON p.user_id = u.id
                    AND MONTH(p.data_pontos) = :mes
                    AND YEAR(p.data_pontos)  = :ano
                    AND p.tarefa LIKE 'sinex_%'
                GROUP BY u.nome, d.nome
                ORDER BY Pontos_Mes DESC
            """), conn, params={"mes": mes, "ano": ano}).fillna(0)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=f"{ano}-{mes:02d}")
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=relatorio_{ano}_{mes:02d}.xlsx"},
        )
    except Exception as e:
        return JSONResponse({"erro": str(e)}, status_code=500)


# ─────────────────────────────────────────────────────────────
#  PONTUAÇÃO SINEX (admin — por utilizador)
# ─────────────────────────────────────────────────────────────

@app.get("/admin/pontuacao-sinex", response_class=HTMLResponse)
async def admin_pontuacao_sinex(request: Request, dept: str = "", pesquisa: str = ""):
    try:
        with engine_socem.connect() as conn:
            depts = pd.read_sql(
                "SELECT id, nome FROM departamentos ORDER BY nome", conn
            ).to_dict("records")

            query = """
                SELECT u.id, u.nome,
                       ISNULL(u.sinex_employee_id, '') as numero,
                       ISNULL(d.nome, 'Sem Dept')      as departamento,
                       ISNULL(u.pontos_total, 0)        as pontos_total
                FROM users u
                LEFT JOIN departamentos d ON d.id = u.departamento_id
                WHERE 1=1
            """
            params_q = {}
            if dept:
                query += " AND d.nome = :dept"
                params_q["dept"] = dept
            if pesquisa:
                query += " AND (u.nome LIKE :p OR CAST(u.sinex_employee_id AS NVARCHAR) LIKE :p)"
                params_q["p"] = f"%{pesquisa}%"
            query += " ORDER BY u.pontos_total DESC, u.nome"

            users = pd.read_sql(text(query), conn, params=params_q).to_dict("records")

    except Exception as e:
        return f"<h1>Erro pontuação SINEX: {e}</h1>"

    return templates.TemplateResponse("admin_pontuacao_sinex.html", {
        "request":  request,
        "users":    users,
        "depts":    depts,
        "dept_sel": dept,
        "pesquisa": pesquisa,
    })


# ─────────────────────────────────────────────────────────────
#  PONTUAÇÃO IDONTIME (admin — por colaborador)
# ─────────────────────────────────────────────────────────────

@app.get("/admin/pontuacao-idontime", response_class=HTMLResponse)
async def admin_pontuacao_idontime(request: Request, dept: str = "", pesquisa: str = ""):
    try:
        with engine_idonics.connect() as conn:
            depts = pd.read_sql(
                "SELECT id, nome FROM departamentos ORDER BY nome", conn
            ).to_dict("records")

            query = """
                SELECT c.id, c.nome,
                       ISNULL(c.numero, '')          as numero,
                       ISNULL(d.nome, 'Sem Dept')    as departamento,
                       ISNULL(c.pontos_total, 0)      as pontos_total
                FROM colaboradores c
                LEFT JOIN departamentos d ON d.id = c.id_departamento
                WHERE c.activo = 1
            """
            params_q = {}
            if dept:
                query += " AND d.nome = :dept"
                params_q["dept"] = dept
            if pesquisa:
                query += " AND (c.nome LIKE :p OR c.numero LIKE :p)"
                params_q["p"] = f"%{pesquisa}%"
            query += " ORDER BY c.pontos_total DESC, c.nome"

            users = pd.read_sql(text(query), conn, params=params_q).to_dict("records")

    except Exception as e:
        return f"<h1>Erro pontuação IDOntime: {e}</h1>"

    return templates.TemplateResponse("admin_pontuacao_idontime.html", {
        "request":  request,
        "users":    users,
        "depts":    depts,
        "dept_sel": dept,
        "pesquisa": pesquisa,
    })


# ─────────────────────────────────────────────────────────────
#  REPROCESSAR SINEX
# ─────────────────────────────────────────────────────────────

@app.get("/admin/reprocessar/sinex", response_class=HTMLResponse)
async def reprocessar_sinex_get(request: Request):
    return templates.TemplateResponse("admin_reprocessar_sinex.html", {
        "request":   request,
        "resultado": None,
    })


@app.post("/admin/reprocessar/sinex", response_class=HTMLResponse)
async def reprocessar_sinex_post(
    request: Request,
    data_inicio: str = Form(...),
    data_fim: str = Form(...),
):
    resultado = sinex_processar_intervalo(data_inicio, data_fim)
    return templates.TemplateResponse("admin_reprocessar_sinex.html", {
        "request":     request,
        "resultado":   resultado,
        "data_inicio": data_inicio,
        "data_fim":    data_fim,
    })


# ─────────────────────────────────────────────────────────────
#  REPROCESSAR IDONTIME
# ─────────────────────────────────────────────────────────────

@app.get("/admin/reprocessar/idontime", response_class=HTMLResponse)
async def reprocessar_idontime_get(request: Request):
    try:
        with engine_idonics.connect() as conn:
            ultimos = pd.read_sql(text("""
                SELECT TOP 10
                       FORMAT(data_ini, 'dd/MM/yyyy')     as data_ini,
                       FORMAT(data_fim, 'dd/MM/yyyy')     as data_fim,
                       total_registos,
                       FORMAT(data_execucao, 'dd/MM/yyyy HH:mm') as executado_em,
                       obs
                FROM processamentos
                ORDER BY data_execucao DESC
            """), conn).to_dict("records")
    except Exception:
        ultimos = []

    return templates.TemplateResponse("admin_reprocessar_idontime.html", {
        "request":   request,
        "resultado": None,
        "ultimos":   ultimos,
    })


@app.post("/admin/reprocessar/idontime", response_class=HTMLResponse)
async def reprocessar_idontime_post(
    request: Request,
    data_inicio: str = Form(...),
    data_fim: str = Form(...),
):
    resultado = idontime_processar_intervalo(data_inicio, data_fim)

    try:
        with engine_idonics.connect() as conn:
            ultimos = pd.read_sql(text("""
                SELECT TOP 10
                       FORMAT(data_ini, 'dd/MM/yyyy')     as data_ini,
                       FORMAT(data_fim, 'dd/MM/yyyy')     as data_fim,
                       total_registos,
                       FORMAT(data_execucao, 'dd/MM/yyyy HH:mm') as executado_em,
                       obs
                FROM processamentos
                ORDER BY data_execucao DESC
            """), conn).to_dict("records")
    except Exception:
        ultimos = []

    return templates.TemplateResponse("admin_reprocessar_idontime.html", {
        "request":     request,
        "resultado":   resultado,
        "data_inicio": data_inicio,
        "data_fim":    data_fim,
        "ultimos":     ultimos,
    })


# ─────────────────────────────────────────────────────────────
#  SINCRONIZAR COLABORADORES IDONTIME
# ─────────────────────────────────────────────────────────────

@app.post("/admin/sincronizar-idontime")
async def sincronizar_idontime():
    try:
        resultado = sincronizar_colaboradores()
        msg = (f"✅ Sincronizado: {resultado['colaboradores']} colaboradores, "
               f"{resultado['departamentos']} departamentos, "
               f"{resultado['inactivados']} inactivados.")
        return RedirectResponse(f"/admin/reprocessar/idontime?msg={msg}", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin/reprocessar/idontime?msg=❌+Erro:+{str(e)[:80]}", status_code=303)


# ─────────────────────────────────────────────────────────────
#  ADMIN — UTILIZADORES SINEX
# ─────────────────────────────────────────────────────────────

@app.get("/admin-users", response_class=HTMLResponse)
async def admin_users_get(request: Request):
    try:
        with engine_socem.connect() as conn:
            depts = pd.read_sql("SELECT id, nome FROM departamentos ORDER BY nome", conn).to_dict("records")
            users_df = pd.read_sql("""
                SELECT u.id, u.nome,
                       COALESCE(CAST(u.pontos_total AS DECIMAL(10,1)), 0) as pontos_total,
                       COALESCE(d.nome, 'Sem departamento') as departamento_nome,
                       ISNULL(e.nome, 'Sem equipa') as equipa_nome
                FROM users u
                LEFT JOIN departamentos d ON u.departamento_id = d.id
                LEFT JOIN equipas e ON u.equipa_id = e.id
                ORDER BY u.nome
            """, conn)
            users_df["departamento_nome"] = users_df["departamento_nome"].fillna("Sem departamento")
            users_df["equipa_nome"] = users_df["equipa_nome"].fillna("Sem equipa")
            users = users_df.to_dict("records")
    except Exception as e:
        depts, users = [], []
        print(f"❌ admin-users: {e}")

    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "departamentos": depts,
        "users": users,
        "total_users": len(users),
    })


@app.post("/admin-users")
async def admin_users_post(nome: str = Form(...), departamento_id: int = Form(...)):
    try:
        nome = nome.strip()[:100]
        with engine_socem.connect() as conn:
            conn.execute(text("""
                INSERT INTO users (nome, departamento_id, pontos_total, ferias_ganhas, equipa_id)
                VALUES (:nome, :dept_id, 0, 0, NULL)
            """), {"nome": nome, "dept_id": departamento_id})
            conn.commit()
        msg = f"✅ {nome} criado!"
    except Exception as e:
        msg = f"❌ {str(e)[:60]}"
    return RedirectResponse(f"/admin-users?msg={msg}", status_code=303)


# ─────────────────────────────────────────────────────────────
#  ADMIN — DEPARTAMENTOS
# ─────────────────────────────────────────────────────────────

@app.get("/admin-departamentos", response_class=HTMLResponse)
async def admin_departamentos_get(request: Request):
    departamentos = []
    usuarios_dept = {}
    try:
        with engine_socem.connect() as conn:
            depts_df = pd.read_sql("SELECT id, nome FROM departamentos ORDER BY nome", conn)
            departamentos = depts_df.to_dict("records") if not depts_df.empty else []

            users_df = pd.read_sql("""
                SELECT u.id, u.nome, COALESCE(u.pontos_total, 0) as pontos_total,
                       COALESCE(d.id, 0) as dept_id
                FROM users u LEFT JOIN departamentos d ON u.departamento_id = d.id
                ORDER BY d.nome, u.nome
            """, conn)
            for _, row in users_df.iterrows():
                dept_id = int(row["dept_id"])
                if dept_id not in usuarios_dept:
                    usuarios_dept[dept_id] = []
                usuarios_dept[dept_id].append({
                    "id": int(row["id"]),
                    "nome": str(row["nome"]),
                    "pontos_total": float(row["pontos_total"]),
                })
    except Exception as e:
        print(f"❌ admin-departamentos: {e}")

    return templates.TemplateResponse("admin_departamentos.html", {
        "request": request,
        "departamentos": departamentos,
        "usuarios_dept": usuarios_dept,
    })


@app.post("/admin-departamentos")
async def admin_departamentos_post(
    nome: str = Form(None),
    dept_id: int = Form(None),
    user_id: int = Form(None),
):
    msg = "❌ Erro desconhecido"
    try:
        with engine_socem.connect() as conn:
            if nome:
                nome = nome.strip()[:50]
                exists = conn.execute(text(
                    "SELECT id FROM departamentos WHERE LOWER(nome) = LOWER(:nome)"
                ), {"nome": nome}).first()
                if exists:
                    msg = f"❌ '{nome}' já existe!"
                else:
                    conn.execute(text("INSERT INTO departamentos (nome) VALUES (:nome)"), {"nome": nome})
                    conn.commit()
                    msg = f"✅ '{nome}' criada!"
            elif dept_id and user_id:
                conn.execute(text(
                    "UPDATE users SET departamento_id = :dept_id WHERE id = :user_id"
                ), {"dept_id": dept_id, "user_id": user_id})
                conn.commit()
                msg = "✅ User associado!"
    except Exception as e:
        msg = f"❌ {str(e)[:60]}"
    return RedirectResponse(f"/admin-departamentos?msg={msg}", status_code=303)


# ─────────────────────────────────────────────────────────────
#  ADMIN — EQUIPAS
# ─────────────────────────────────────────────────────────────

@app.get("/admin-equipas", response_class=HTMLResponse)
async def admin_equipas_get(request: Request):
    equipas = []
    users_sem = []
    users_com = []
    try:
        with engine_socem.connect() as conn:
            equipas = pd.read_sql("""
                SELECT e.id, e.nome, COUNT(u.id) as users_count
                FROM equipas e LEFT JOIN users u ON u.equipa_id = e.id
                GROUP BY e.id, e.nome ORDER BY e.nome
            """, conn).to_dict("records")
            users_sem = pd.read_sql("""
                SELECT u.id, u.nome, COALESCE(d.nome, 'Sem Dept') as dept
                FROM users u LEFT JOIN departamentos d ON u.departamento_id = d.id
                WHERE u.equipa_id IS NULL ORDER BY u.nome
            """, conn).to_dict("records")
            users_com = pd.read_sql("""
                SELECT u.id, u.nome, u.equipa_id,
                       COALESCE(e.nome, 'Sem Nome') as equipa_nome,
                       COALESCE(d.nome, 'Sem Dept') as dept
                FROM users u
                LEFT JOIN equipas e ON u.equipa_id = e.id
                LEFT JOIN departamentos d ON u.departamento_id = d.id
                WHERE u.equipa_id IS NOT NULL ORDER BY e.nome, u.nome
            """, conn).to_dict("records")
    except Exception as e:
        print(f"❌ admin-equipas: {e}")

    return templates.TemplateResponse("admin_equipas.html", {
        "request": request,
        "equipas": equipas,
        "users_sem": users_sem,
        "users_com": users_com,
    })


@app.post("/admin-equipas")
async def admin_equipas_post(
    nome: str = Form(None),
    equipa_id: int = Form(None),
    user_id: int = Form(None),
    delete_id: int = Form(None),
    esvaziar_id: int = Form(None),
    transfer_id: int = Form(None),
    nova_equipa_id: int = Form(None),
):
    msg = "❌ Erro desconhecido"
    try:
        with engine_socem.connect() as conn:
            if nome:
                nome = nome.strip()[:50]
                exists = conn.execute(text("SELECT id FROM equipas WHERE LOWER(nome) = LOWER(:nome)"), {"nome": nome}).first()
                if exists:
                    msg = f"❌ '{nome}' já existe!"
                else:
                    conn.execute(text("INSERT INTO equipas (nome) VALUES (:nome)"), {"nome": nome})
                    conn.commit()
                    msg = f"✅ '{nome}' criada!"
            elif equipa_id and user_id:
                current = conn.execute(text("SELECT e.nome FROM users u LEFT JOIN equipas e ON u.equipa_id = e.id WHERE u.id = :uid"), {"uid": user_id}).scalar()
                if current:
                    msg = f"❌ Já tem equipa '{current}'!"
                else:
                    conn.execute(text("UPDATE users SET equipa_id = :eid WHERE id = :uid"), {"eid": equipa_id, "uid": user_id})
                    conn.commit()
                    msg = "✅ User associado!"
            elif delete_id:
                count = conn.execute(text("SELECT COUNT(*) FROM users WHERE equipa_id = :id"), {"id": delete_id}).scalar()
                if count > 0:
                    msg = f"❌ {count} users! Use 🧹 ou 🔄"
                else:
                    old = conn.execute(text("SELECT nome FROM equipas WHERE id = :id"), {"id": delete_id}).scalar()
                    conn.execute(text("DELETE FROM equipas WHERE id = :id"), {"id": delete_id})
                    conn.commit()
                    msg = f"✅ '{old}' eliminada!"
            elif esvaziar_id:
                count = conn.execute(text("SELECT COUNT(*) FROM users WHERE equipa_id = :id"), {"id": esvaziar_id}).scalar()
                old = conn.execute(text("SELECT nome FROM equipas WHERE id = :id"), {"id": esvaziar_id}).scalar()
                conn.execute(text("UPDATE users SET equipa_id = NULL WHERE equipa_id = :id"), {"id": esvaziar_id})
                conn.execute(text("DELETE FROM equipas WHERE id = :id"), {"id": esvaziar_id})
                conn.commit()
                msg = f"✅ '{old}' esvaziada ({count} users)!"
            elif transfer_id and nova_equipa_id:
                count = conn.execute(text("SELECT COUNT(*) FROM users WHERE equipa_id = :id"), {"id": transfer_id}).scalar()
                old = conn.execute(text("SELECT nome FROM equipas WHERE id = :id"), {"id": transfer_id}).scalar()
                new = conn.execute(text("SELECT nome FROM equipas WHERE id = :id"), {"id": nova_equipa_id}).scalar()
                conn.execute(text("UPDATE users SET equipa_id = :nova WHERE equipa_id = :old"), {"nova": nova_equipa_id, "old": transfer_id})
                conn.execute(text("DELETE FROM equipas WHERE id = :id"), {"id": transfer_id})
                conn.commit()
                msg = f"✅ {count} users '{old}' → '{new}'!"
    except Exception as e:
        msg = f"❌ {str(e)[:60]}"
    return RedirectResponse(f"/admin-equipas?msg={msg}", status_code=303)


# ─────────────────────────────────────────────────────────────
#  ADMIN — ATRIBUIR PONTOS MANUAL
# ─────────────────────────────────────────────────────────────

@app.get("/admin-pontos", response_class=HTMLResponse)
async def admin_pontos_get(request: Request):
    try:
        # Departamentos e utilizadores SINEX
        users_df = pd.read_sql("""
            SELECT u.id, u.nome, u.pontos_total,
                   ISNULL(d.nome, 'Sem Dept') as dept_nome
            FROM users u
            LEFT JOIN departamentos d ON u.departamento_id = d.id
            ORDER BY d.nome, u.nome
        """, engine_socem)
        depts_sinex = pd.read_sql(
            "SELECT DISTINCT id, nome FROM departamentos ORDER BY nome", engine_socem
        ).to_dict("records")

        # Departamentos IDOntime
        depts_idontime = pd.read_sql(
            text("SELECT id, nome FROM departamentos ORDER BY nome"), engine_idonics
        ).to_dict("records")

        users_list = users_df.to_dict("records")
    except Exception as e:
        users_list = depts_sinex = depts_idontime = []
        print(f"❌ admin-pontos: {e}")

    return templates.TemplateResponse("admin_pontos.html", {
        "request":        request,
        "users":          users_list,
        "departamentos":  depts_sinex,       # mantém compatibilidade com JS existente
        "depts_idontime": depts_idontime,    # novos departamentos IDOntime
    })


@app.post("/api/atribuir-pontos")
async def api_atribuir_pontos(
    user_id: int = Form(...),
    pontos: int = Form(...),
    motivo: str = Form(""),
):
    try:
        # O tarefa inclui timestamp para garantir unicidade mesmo com o mesmo motivo
        ts     = str(uuid.uuid4())[:8]  # 8 chars únicos — sem risco de colisão
        tarefa = f"manual_{ts}: {motivo.strip()[:60]}" if motivo.strip() else f"manual_{ts}"
        conn = pyodbc.connect(CONN_SOCEM)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET pontos_total = pontos_total + ? WHERE id = ?", (pontos, user_id))
        cursor.execute(
            "INSERT INTO pontos (user_id, tarefa, pontos, data_pontos) VALUES (?, ?, ?, CAST(GETDATE() AS DATE))",
            (user_id, tarefa, pontos)
        )
        cursor.execute(
            "INSERT INTO eventos (user_id, tipo, pontos) VALUES (?, ?, ?)",
            (user_id, tarefa, pontos)
        )
        conn.commit()
        cursor.execute("SELECT pontos_total FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        novos_pontos = int(row[0]) if row else 0
        cursor.close()
        conn.close()
        return JSONResponse({"ok": True, "pontos_total": novos_pontos})
    except Exception as e:
        return JSONResponse({"ok": False, "erro": str(e)}, status_code=500)


@app.post("/dept-colaboradores")
async def dept_colaboradores(dept_id: int = Form(...)):
    try:
        conn = pyodbc.connect(CONN_SOCEM)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nome, ISNULL(u.pontos_total, 0) as pontos_total,
                   ISNULL(e.nome, 'N/A') as equipa
            FROM users u
            LEFT JOIN equipas e ON u.equipa_id = e.id
            WHERE u.departamento_id = ?
            ORDER BY u.nome
        """, (dept_id,))
        users = [{"id": r.id, "nome": r.nome, "pontos_total": r.pontos_total, "equipa": r.equipa}
                 for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return JSONResponse({"users": users})
    except Exception as e:
        return JSONResponse({"users": []})


# ─────────────────────────────────────────────────────────────
#  ADMIN — LOJA
# ─────────────────────────────────────────────────────────────

@app.get("/admin/loja", response_class=HTMLResponse)
async def admin_loja_get(request: Request):
    try:
        with engine_socem.connect() as conn:
            recompensas = pd.read_sql(text(
                "SELECT id, nome, descricao, custo_pontos, ativo FROM recompensas ORDER BY custo_pontos"
            ), conn).to_dict("records")

            # Resgates — inclui utilizadores de ambos os sistemas
            resgates = pd.read_sql(text("""
                SELECT r.id,
                       ISNULL(u.nome, '— IDOntime —')   as colaborador,
                       rc.nome                           as recompensa,
                       r.pontos_gastos,
                       ISNULL(r.pontos_gastos_idontime, 0) as pontos_gastos_idontime,
                       r.estado,
                       FORMAT(r.data_resgate, 'dd/MM/yyyy HH:mm') as data_resgate,
                       r.idontime_colaborador_id
                FROM resgates r
                LEFT JOIN users u ON u.id = r.user_id
                INNER JOIN recompensas rc ON rc.id = r.recompensa_id
                ORDER BY r.data_resgate DESC
            """), conn).to_dict("records")

    except Exception as e:
        return f"<h1>Erro admin loja: {e}</h1>"

    return templates.TemplateResponse("admin_loja.html", {
        "request":    request,
        "recompensas": recompensas,
        "resgates":   resgates,
    })


@app.post("/admin/loja/criar")
async def admin_loja_criar(
    nome: str = Form(...),
    descricao: str = Form(""),
    custo_pontos: int = Form(...),
):
    try:
        with engine_socem.connect() as conn:
            conn.execute(text("""
                INSERT INTO recompensas (nome, descricao, custo_pontos, ativo)
                VALUES (:nome, :desc, :custo, 1)
            """), {"nome": nome.strip()[:100], "desc": descricao.strip()[:255], "custo": custo_pontos})
            conn.commit()
        return RedirectResponse("/admin/loja?msg=Recompensa+criada", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin/loja?msg=Erro:{str(e)[:50]}", status_code=303)


@app.post("/admin/loja/toggle")
async def admin_loja_toggle(recompensa_id: int = Form(...)):
    try:
        with engine_socem.connect() as conn:
            conn.execute(text("UPDATE recompensas SET ativo = 1 - ativo WHERE id = :id"), {"id": recompensa_id})
            conn.commit()
        return RedirectResponse("/admin/loja", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin/loja?msg=Erro:{str(e)[:50]}", status_code=303)


@app.post("/admin/loja/entregar")
async def admin_loja_entregar(resgate_id: int = Form(...)):
    try:
        with engine_socem.connect() as conn:
            conn.execute(text("UPDATE resgates SET estado = 'entregue' WHERE id = :id"), {"id": resgate_id})
            conn.commit()
        return RedirectResponse("/admin/loja", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin/loja?msg=Erro:{str(e)[:50]}", status_code=303)


# ─────────────────────────────────────────────────────────────
#  ADMIN — CONTAS (login)
# ─────────────────────────────────────────────────────────────

@app.get("/admin/contas", response_class=HTMLResponse)
async def admin_contas_get(request: Request, msg: str = ""):
    try:
        # 1. Obter todas as contas existentes em jogo_score
        with engine_score.connect() as conn:
            contas_df = pd.read_sql(text("""
                SELECT id, username, tipo,
                       sinex_user_id,
                       idontime_colaborador_id
                FROM contas
                ORDER BY tipo DESC, username
            """), conn)
        contas = contas_df.to_dict("records")

        # IDs já associados a contas (para filtrar em Python)
        usados_sinex   = set(int(x) for x in contas_df["sinex_user_id"].dropna())
        usados_idonics = set(int(x) for x in contas_df["idontime_colaborador_id"].dropna())

        # 2. Todos os utilizadores SINEX
        with engine_socem.connect() as conn:
            all_sinex = pd.read_sql(text(
                "SELECT id, nome FROM users ORDER BY nome"
            ), conn).to_dict("records")

        # 3. Todos os colaboradores IDOntime activos
        with engine_idonics.connect() as conn:
            all_idonics = pd.read_sql(text(
                "SELECT id, nome FROM colaboradores WHERE activo = 1 ORDER BY nome"
            ), conn).to_dict("records")

        # 4. Filtrar em Python — apenas os que ainda não têm conta
        users_sinex   = [u for u in all_sinex   if int(u["id"]) not in usados_sinex]
        users_idonics = [u for u in all_idonics  if int(u["id"]) not in usados_idonics]

    except Exception as e:
        return f"<h1>Erro contas: {e}</h1>"

    return templates.TemplateResponse("admin_contas.html", {
        "request":      request,
        "contas":       contas,
        "users_sinex":  users_sinex,
        "users_idonics": users_idonics,
        "msg":          msg,
    })


@app.post("/admin/contas/criar")
async def admin_contas_criar(
    username: str = Form(...),
    password: str = Form(...),
    tipo: str = Form(...),
    sinex_user_id: str = Form(""),
    idontime_colaborador_id: str = Form(""),
):
    try:
        sinex_uid = int(sinex_user_id) if sinex_user_id.strip() else None
        idon_uid  = int(idontime_colaborador_id) if idontime_colaborador_id.strip() else None
        hashed    = hash_password(password)

        conn = pyodbc.connect(CONN_SCORE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contas (username, password_hash, tipo, sinex_user_id, idontime_colaborador_id) VALUES (?, ?, ?, ?, ?)",
            (username.strip(), hashed, tipo, sinex_uid, idon_uid)
        )
        conn.commit()
        conn.close()
        return RedirectResponse(f"/admin/contas?msg=✅ Conta '{username}' criada!", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin/contas?msg=❌ Erro: {str(e)[:80]}", status_code=303)


@app.post("/admin/contas/password")
async def admin_contas_password(
    conta_id: int = Form(...),
    nova_password: str = Form(...),
):
    try:
        hashed = hash_password(nova_password)
        conn = pyodbc.connect(CONN_SCORE)
        cursor = conn.cursor()
        cursor.execute("UPDATE contas SET password_hash = ? WHERE id = ?", (hashed, conta_id))
        conn.commit()
        conn.close()
        return RedirectResponse("/admin/contas?msg=✅ Password alterada!", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin/contas?msg=❌ Erro: {str(e)[:80]}", status_code=303)


@app.post("/admin/contas/delete")
async def admin_contas_delete(conta_id: int = Form(...), request: Request = None):
    session = request.state.user if request else None
    if session and session.get("conta_id") == conta_id:
        return RedirectResponse("/admin/contas?msg=❌ Não podes apagar a tua própria conta.", status_code=303)
    try:
        conn = pyodbc.connect(CONN_SCORE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contas WHERE id = ?", (conta_id,))
        conn.commit()
        conn.close()
        return RedirectResponse("/admin/contas?msg=✅ Conta eliminada.", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin/contas?msg=❌ Erro: {str(e)[:80]}", status_code=303)


# ─────────────────────────────────────────────────────────────
#  ADMIN — COLABORADORES IDONTIME
#  Permite ver e associar colaboradores IDOntime a departamentos.
#  Fluxo: sincronizar → associar departamento → ir a Contas/Login
#         para ligar conta de login ao colaborador.
# ─────────────────────────────────────────────────────────────

@app.get("/admin-colaboradores-idontime", response_class=HTMLResponse)
async def admin_colab_idontime_get(request: Request, msg: str = ""):
    try:
        with engine_idonics.connect() as conn:
            # Todos os departamentos IDOntime
            depts = pd.read_sql(
                text("SELECT id, nome FROM departamentos ORDER BY nome"), conn
            ).to_dict("records")

            # Todos os colaboradores activos com departamento
            colaboradores = pd.read_sql(text("""
                SELECT c.id, c.nome,
                       ISNULL(c.numero, '')          as numero,
                       ISNULL(c.pontos_total, 0)      as pontos_total,
                       c.id_departamento,
                       ISNULL(d.nome, 'Sem Dept')     as departamento
                FROM colaboradores c
                LEFT JOIN departamentos d ON d.id = c.id_departamento
                WHERE c.activo = 1
                ORDER BY d.nome, c.nome
            """), conn).to_dict("records")

    except Exception as e:
        return f"<h1>Erro colaboradores IDOntime: {e}</h1>"

    return templates.TemplateResponse("admin_colaboradores_idontime.html", {
        "request":       request,
        "colaboradores": colaboradores,
        "depts":         depts,
        "msg":           msg,
    })


@app.post("/admin-colaboradores-idontime")
async def admin_colab_idontime_post(
    colaborador_id: int = Form(...),
    departamento_id: int = Form(...),
):
    """Associa um colaborador IDOntime a um departamento."""
    try:
        with engine_idonics.connect() as conn:
            conn.execute(text(
                "UPDATE colaboradores SET id_departamento = :dept WHERE id = :id"
            ), {"dept": departamento_id, "id": colaborador_id})
            conn.commit()
        return RedirectResponse(
            "/admin-colaboradores-idontime?msg=✅ Departamento actualizado!", status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            f"/admin-colaboradores-idontime?msg=❌ Erro: {str(e)[:80]}", status_code=303
        )


# ─────────────────────────────────────────────────────────────
#  COLABORADOR IDONTIME (perfil + detalhe diário)
# ─────────────────────────────────────────────────────────────

import re as _re

def _parse_obs(obs: str) -> dict:
    """
    Extrai dados estruturados do campo obs da tabela jogo_idonics.pontos.

    Exemplos de obs:
      "Cumpriu 8.2h (obj 8h, 4 picagens) [pics: 08:24:55, 13:01:26, ...]"
      "Insuficiente 3.6h de 8h (2 picagens) [pics: 19:25:51, 23:05:43]"
      "Dia sem picagens"
      "manual: motivo"
    """
    if not obs:
        return {"tipo": "—", "horas": None, "n_picagens": None, "picagens": []}

    obs = str(obs)

    # Tipo: Cumpriu / Insuficiente / Bónus / Manual / outro
    tipo = ("Cumpriu"      if obs.startswith("Cumpriu")      else
            "Insuficiente" if obs.startswith("Insuficiente") else
            "Bonus"        if obs.startswith("Bónus semana") else
            "Manual"       if obs.startswith("manual")       else obs[:30])

    # Horas trabalhadas (ex: "8.2h" ou "3.6h")
    m_horas = _re.search(r"(\d+(?:\.\d+)?)h", obs)
    horas = float(m_horas.group(1)) if m_horas else None

    # Número de picagens (ex: "4 picagens")
    m_npics = _re.search(r"(\d+)\s+picagens?", obs)
    n_picagens = int(m_npics.group(1)) if m_npics else None

    # Lista de horários de picagem (ex: "08:24:55, 13:01:26, ...")
    m_pics = _re.search(r"\[pics:\s*(.+?)\]", obs)
    picagens = [p.strip() for p in m_pics.group(1).split(",")] if m_pics else []

    return {
        "tipo":       tipo,
        "horas":      horas,
        "n_picagens": n_picagens,
        "picagens":   picagens,
    }


@app.get("/colaborador-idontime/{colaborador_id}", response_class=HTMLResponse)
async def colaborador_idontime_detalhe(request: Request, colaborador_id: int):
    try:
        with engine_idonics.connect() as conn:
            # Dados do colaborador
            df = pd.read_sql(text("""
                SELECT c.id, c.nome,
                       ISNULL(c.numero, '')         as numero,
                       ISNULL(c.pontos_total, 0)     as pontos_total,
                       ISNULL(d.nome, 'Sem Dept')   as departamento
                FROM colaboradores c
                LEFT JOIN departamentos d ON d.id = c.id_departamento
                WHERE c.id = :id
            """), conn, params={"id": colaborador_id})

            if df.empty:
                return "<h1>❌ Colaborador não encontrado</h1><a href='/admin-colaboradores-idontime'>← Lista</a>"

            colaborador = df.iloc[0].to_dict()

            # Histórico de pontos (últimos 60 dias)
            hist_df = pd.read_sql(text("""
                SELECT TOP 60
                       tarefa,
                       pontos,
                       FORMAT(data_pontos, 'dd/MM/yyyy') as data_fmt,
                       ISNULL(obs, '') as obs
                FROM pontos
                WHERE id_colaborador = :id
                ORDER BY data_pontos DESC, id DESC
            """), conn, params={"id": colaborador_id})

            # Ranking no departamento
            rank_df = pd.read_sql(text("""
                SELECT c.id, RANK() OVER (ORDER BY ISNULL(c.pontos_total,0) DESC) as pos
                FROM colaboradores c
                WHERE c.id_departamento = (
                    SELECT id_departamento FROM colaboradores WHERE id = :id
                )
                AND c.activo = 1
            """), conn, params={"id": colaborador_id})
            pos_arr = rank_df[rank_df["id"] == colaborador_id]["pos"].values
            pos_dept = int(pos_arr[0]) if len(pos_arr) > 0 else "—"

            # Ranking geral
            rank_g = pd.read_sql(text("""
                SELECT id, RANK() OVER (ORDER BY ISNULL(pontos_total,0) DESC) as pos
                FROM colaboradores WHERE activo = 1
            """), conn)
            pos_g_arr = rank_g[rank_g["id"] == colaborador_id]["pos"].values
            pos_geral = int(pos_g_arr[0]) if len(pos_g_arr) > 0 else "—"

        # Enriquecer cada registo com dados parsed do obs
        historico = []
        for _, row in hist_df.iterrows():
            parsed = _parse_obs(row["obs"])
            historico.append({
                "tarefa":      row["tarefa"],
                "pontos":      int(row["pontos"]),
                "data_fmt":    row["data_fmt"],
                "tipo":        parsed["tipo"],
                "horas":       parsed["horas"],
                "n_picagens":  parsed["n_picagens"],
                "picagens":    parsed["picagens"],
            })

    except Exception as e:
        return f"<h1>Erro colaborador IDOntime: {e}</h1>"

    return templates.TemplateResponse("colaborador_idontime.html", {
        "request":     request,
        "colaborador": colaborador,
        "historico":   historico,
        "pos_dept":    pos_dept,
        "pos_geral":   pos_geral,
    })


# ─────────────────────────────────────────────────────────────
#  ADMIN — ATRIBUIR PONTOS IDONTIME (AJAX)
# ─────────────────────────────────────────────────────────────

@app.post("/dept-colaboradores-idontime")
async def dept_colab_idontime(dept_id: int = Form(...)):
    """Devolve colaboradores IDOntime de um departamento (para o AJAX do admin_pontos)."""
    try:
        with engine_idonics.connect() as conn:
            rows = conn.execute(text("""
                SELECT id, nome, ISNULL(pontos_total, 0) as pontos_total
                FROM colaboradores
                WHERE id_departamento = :did AND activo = 1
                ORDER BY nome
            """), {"did": dept_id}).fetchall()
        users = [{"id": r[0], "nome": r[1], "pontos_total": r[2]} for r in rows]
        return JSONResponse({"users": users})
    except Exception:
        return JSONResponse({"users": []})


@app.post("/api/atribuir-pontos-idontime")
async def api_atribuir_pontos_idontime(
    user_id: int = Form(...),
    pontos: int = Form(...),
    motivo: str = Form(""),
):
    """Atribui pontos manuais a um colaborador IDOntime."""
    try:
        # O tarefa inclui timestamp para garantir unicidade (constraint uq_colab_tarefa)
        ts     = str(uuid.uuid4())[:8]  # 8 chars únicos — sem risco de colisão
        tarefa = f"manual_{ts}: {motivo.strip()[:60]}" if motivo.strip() else f"manual_{ts}"
        obs    = f"Atribuição manual: {motivo.strip()[:80]}" if motivo.strip() else "Atribuição manual"
        conn = pyodbc.connect(CONN_IDONICS)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE colaboradores SET pontos_total = pontos_total + ? WHERE id = ?",
            (pontos, user_id)
        )
        cursor.execute(
            "INSERT INTO pontos (id_colaborador, tarefa, pontos, data_pontos, obs) VALUES (?, ?, ?, CAST(GETDATE() AS DATE), ?)",
            (user_id, tarefa, pontos, obs)
        )
        conn.commit()
        cursor.execute("SELECT pontos_total FROM colaboradores WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        novos_pontos = int(row[0]) if row else 0
        cursor.close()
        conn.close()
        return JSONResponse({"ok": True, "pontos_total": novos_pontos})
    except Exception as e:
        return JSONResponse({"ok": False, "erro": str(e)}, status_code=500)
