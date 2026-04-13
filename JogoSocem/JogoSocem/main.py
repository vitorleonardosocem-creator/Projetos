from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
import urllib.parse
import pandas as pd
from fastapi import Form
from fastapi.responses import JSONResponse
import pyodbc
from fastapi import APIRouter
import os
import io
from datetime import date
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse as StarletteRedirect
from sinex_job import processar_intervalo
from auth import (
    get_session_user, create_session_token, hash_password,
    verify_password, SESSION_COOKIE, SESSION_MAX_AGE
)


app = FastAPI(title="Jogo SOCEM Demo")
templates = Jinja2Templates(directory="templates")


# ═══════════════════════════════════════════════════════════════
#  MIDDLEWARE DE AUTENTICAÇÃO
# ═══════════════════════════════════════════════════════════════

# Rotas acessíveis sem login
PUBLIC_PATHS = {"/login", "/logout", "/tv"}

# Rotas apenas para admin (tudo o resto é admin, exceto /minha-area e /loja*)
USER_PATHS = {"/minha-area", "/loja"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Ficheiros estáticos e rotas públicas — sem verificação
        if path.startswith("/static") or path in PUBLIC_PATHS or path == "/leaderboard-json":
            request.state.user = get_session_user(request)
            return await call_next(request)

        user = get_session_user(request)
        request.state.user = user

        # Não está autenticado → login
        if not user:
            return StarletteRedirect(f"/login?next={path}")

        # Utilizador normal a tentar aceder a rota de admin
        if user.get("tipo") == "user":
            is_user_allowed = (
                path in USER_PATHS
                or path.startswith("/loja")
                or path.startswith("/minha-area")
            )
            if not is_user_allowed:
                return StarletteRedirect("/minha-area")

        return await call_next(request)


app.add_middleware(AuthMiddleware)

# CONNECTION SQL (já testada)
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=jogo_socem;"  
    "UID=GV;"
    "PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)
params = urllib.parse.quote_plus(CONN_STR)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        with engine.connect() as conn:
            # Leaderboard JOIN (top 20)
            leaderboard_query = """
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY u.pontos_total DESC) as posicao,
                    u.id, u.nome,
                    ISNULL(d.nome, 'Sem Dept') as departamento,
                    ISNULL(e.nome, 'Sem Equipa') as equipa,
                    u.pontos_total,
                    u.ferias_ganhas
                FROM users u
                LEFT JOIN departamentos d ON u.departamento_id = d.id
                LEFT JOIN equipas e ON u.equipa_id = e.id
                ORDER BY u.pontos_total DESC
            """
            leaderboard_df = pd.read_sql(text(leaderboard_query), conn)
            leaderboard = leaderboard_df.to_dict('records')  # Sempre lista válida
            
            # Total users (scalar seguro)
            total_users_df = pd.read_sql("SELECT COUNT(*) as total FROM users", conn)
            total_users = int(total_users_df['total'].iloc[0]) if not total_users_df.empty else 0
            
            # Top1 seguro (evita Series ambiguous)
            top1 = None
            if not leaderboard_df.empty:
                top1_row = leaderboard_df.iloc[0]
                top1 = {
                    'nome': top1_row['nome'],
                    'departamento': top1_row['departamento'],
                    'equipa': top1_row['equipa'],
                    'pontos_total': top1_row['pontos_total']
                }
            
        return templates.TemplateResponse("demo.html", {
            "request": request,
            "leaderboard": leaderboard,  # Sempre lista
            "total_users": total_users,  # int
            "top1": top1  # dict ou None
        })
    except Exception as e:
        return f"Erro Dashboard: {str(e)}<br><a href='/'>Tentar Novamente</a>"

@app.get("/leaderboard-json")
async def leader_json():
    try:
        with engine.connect() as conn:
            query = """
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY u.pontos_total DESC) as posicao,
                    u.nome,
                    ISNULL(d.nome, 'Sem Dept') as departamento,
                    ISNULL(e.nome, 'Sem Equipa') as equipa,
                    u.pontos_total
                FROM users u
                LEFT JOIN departamentos d ON u.departamento_id = d.id
                LEFT JOIN equipas e ON u.equipa_id = e.id
                ORDER BY u.pontos_total DESC
            """
            df = pd.read_sql(text(query), conn)
            return df.to_dict('records')  # Sempre lista
    except:
        return []



@app.get("/picar/{user_id}")
async def picar(user_id: int):
    pts = 1  # ← 1 PONTO FIXO!
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO eventos (user_id, tipo, pontos) VALUES (:u, 'picagem', :p);
            UPDATE users SET pontos_total += :p WHERE id = :u
        """), {"u": user_id, "p": pts})
        conn.commit()
    return f'<h2 style="color:green">✅ User {user_id}: +{pts} pt!</h2><script>setTimeout(() => location.href = "/", 1500);</script>'

@app.get("/nc/{user_id}")
async def nc(user_id: int):
    pts = 1  # ← 1 PONTO FIXO!
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO eventos (user_id, tipo, pontos) VALUES (:u, 'nc', :p);
            UPDATE users SET pontos_total += :p WHERE id = :u
        """), {"u": user_id, "p": pts})
        conn.commit()
    return f'<h2 style="color:orange">✅ User {user_id}: +{pts} pt NC!</h2><script>setTimeout(() => location.href = "/", 1500);</script>'


@app.get("/fim_ano", response_class=HTMLResponse)
async def fim_ano_get(request: Request):
    """Página de confirmação antes do reset anual."""
    try:
        with engine.connect() as conn:
            qualif = pd.read_sql(text(
                "SELECT COUNT(*) as qtd FROM users WHERE pontos_total >= 10"
            ), conn).iloc[0, 0]
            total = pd.read_sql(text(
                "SELECT COUNT(*) as qtd FROM users"
            ), conn).iloc[0, 0]
            ano_atual = date.today().year
    except Exception as e:
        return f"<h1>Erro: {e}</h1>"

    return templates.TemplateResponse("fim_ano.html", {
        "request": request,
        "qualif": int(qualif),
        "total": int(total),
        "ano_atual": ano_atual,
    })


@app.post("/fim_ano")
async def fim_ano_post():
    """Executa reset anual: guarda histórico, atribui férias, zera pontos."""
    try:
        ano = date.today().year
        with engine.connect() as conn:
            # 1. Snapshot para histórico antes de resetar
            conn.execute(text("""
                INSERT INTO historico_anual (user_id, ano, pontos_total, ferias_ganhas)
                SELECT id, :ano, ISNULL(pontos_total, 0), ISNULL(ferias_ganhas, 0)
                FROM users
            """), {"ano": ano})

            # 2. +1 férias para quem atingiu >= 10 pts
            conn.execute(text(
                "UPDATE users SET ferias_ganhas = ferias_ganhas + 1 WHERE pontos_total >= 10"
            ))

            # 3. Reset pontos
            conn.execute(text("UPDATE users SET pontos_total = 0"))
            conn.commit()

            qualif = pd.read_sql(text(
                "SELECT COUNT(*) as qtd FROM users WHERE ferias_ganhas > 0"
            ), conn).iloc[0, 0]

        return RedirectResponse(f"/historico?msg=Reset+{ano}+concluido+{qualif}+colaboradores+ganharam+ferias", status_code=303)
    except Exception as e:
        return {"erro": str(e)}

@app.get("/departamento/{nome}", response_class=HTMLResponse)
async def departamento_detalhe(nome: str, request: Request):
    try:
        with engine.connect() as conn:
            # 1. Encontra ID do dept (query simples)
            dept_df = pd.read_sql(f"SELECT id FROM departamentos WHERE nome = '{nome}'", conn)
            if dept_df.empty:
                return f"<h1>❌ Departamento '{nome}' não encontrado</h1><a href='/departamentos'>← Lista</a>"
            
            dept_id = int(dept_df.iloc[0]['id'])
            
            # 2. Users do dept (F-STRING seguro - nomes internos)
            users_dept_df = pd.read_sql(f"""
                SELECT u.id, u.nome, ISNULL(u.pontos_total, 0) as pontos_total
                FROM users u
                WHERE u.departamento_id = {dept_id}
                ORDER BY pontos_total DESC, u.nome
            """, conn)
            
            # 3. Sempre lista válida para Jinja
            users_dept = users_dept_df.to_dict('records') if not users_dept_df.empty else []
            
            # Stats
            total_users = len(users_dept)
            total_pontos = sum([float(row.get('pontos_total', 0)) for row in users_dept])  # Manual safe
            media_pontos = total_pontos / total_users if total_users > 0 else 0.0

        return templates.TemplateResponse("departamentos.html", {
            "request": request, "nome_dept": nome,
            "users_dept": users_dept,  # Sempre lista perfeita
            "total_users": total_users, "total_pontos": total_pontos, "media_pontos": media_pontos
        })
    except Exception as e:
        return f"<h1>Erro: {str(e)}</h1><a href='/departamentos'>← Departamentos</a>"



# ========== ADMIN DEPARTAMENTOS ==========
@app.get("/admin-departamentos", response_class=HTMLResponse)
async def admin_departamentos_get(request: Request):
    departamentos = []
    usuarios_dept = {}  # ← Dict {dept_id: [users]}
    try:
        with engine.connect() as conn:
            # Depts
            depts_df = pd.read_sql("SELECT id, nome FROM departamentos ORDER BY nome", conn)
            departamentos = depts_df.to_dict('records') if not depts_df.empty else []
            
            # Users GROUPED por dept_id
            users_df = pd.read_sql("""
                SELECT u.id, u.nome, COALESCE(u.pontos_total, 0) as pontos_total,
                       COALESCE(d.id, 0) as dept_id
                FROM users u LEFT JOIN departamentos d ON u.departamento_id = d.id
                ORDER BY d.nome, u.nome
            """, conn)
            
            if not users_df.empty:
                for _, row in users_df.iterrows():
                    dept_id = int(row['dept_id'])
                    if dept_id not in usuarios_dept:
                        usuarios_dept[dept_id] = []
                    usuarios_dept[dept_id].append({
                        'id': int(row['id']),
                        'nome': str(row['nome']),
                        'pontos_total': float(row['pontos_total'])
                    })
                    
    except Exception as e:
        print(f"❌ admin-departamentos: {e}")
    
    print(f"✅ {len(departamentos)} depts, {len(usuarios_dept)} grupos")
    return templates.TemplateResponse("admin_departamentos.html", {
        "request": request, 
        "departamentos": departamentos, 
        "usuarios_dept": usuarios_dept  # ← Dict agora!
    })


@app.post("/admin-departamentos")
async def admin_departamentos_post(nome: str = Form(None), dept_id: int = Form(None), 
                                 user_id: int = Form(None)):
    msg = "❌ Erro desconhecido"
    try:
        nome = (nome or "").strip()[:50]
        with engine.connect() as conn:
            if nome:  # CRIAR
                exists = conn.execute(text("SELECT id FROM departamentos WHERE LOWER(nome) = LOWER(:nome)"), {"nome": nome}).first()
                if exists:
                    msg = f"❌ '{nome}' já existe!"
                else:
                    conn.execute(text("INSERT INTO departamentos (nome) VALUES (:nome)"), {"nome": nome})
                    conn.commit()
                    msg = f"✅ '{nome}' criada!"
            
            elif dept_id and user_id:  # ASSOCIAR
                # Remove dept atual se tem
                conn.execute(text("UPDATE users SET departamento_id = NULL WHERE id = :user_id AND departamento_id = :dept_id"), 
                           {"user_id": user_id, "dept_id": dept_id})
                # Associa novo
                conn.execute(text("UPDATE users SET departamento_id = :dept_id WHERE id = :user_id"), 
                           {"dept_id": dept_id, "user_id": user_id})
                conn.commit()
                msg = "✅ User associado!"
                
    except Exception as e:
        msg = f"❌ {str(e)[:60]}"
    
    return RedirectResponse(f"/admin-departamentos?msg={msg}", status_code=303)





@app.get("/departamentos", response_class=HTMLResponse)
async def lista_departamentos(request: Request):
    try:
        with engine.connect() as conn:
            # Query com stats - NULLs viram 0
            depts = pd.read_sql("""
                SELECT d.id, d.nome, 
                       ISNULL(COUNT(u.id), 0) as total_users,
                       ISNULL(SUM(ISNULL(u.pontos_total, 0)), 0) as total_pontos,
                       CASE WHEN COUNT(u.id) > 0 THEN ISNULL(AVG(ISNULL(u.pontos_total, 0)), 0) ELSE 0 END as media_pontos
                FROM departamentos d
                LEFT JOIN users u ON d.id = u.departamento_id
                GROUP BY d.id, d.nome
                ORDER BY total_pontos DESC, total_users DESC
            """, conn)
            
            # Força tipos numéricos (corrige NULLs Pandas)
            depts['total_pontos'] = pd.to_numeric(depts['total_pontos'], errors='coerce').fillna(0)
            depts['media_pontos'] = pd.to_numeric(depts['media_pontos'], errors='coerce').fillna(0)
            
            total_depts = len(depts)
            total_users_df = pd.read_sql("SELECT COUNT(*) as total FROM users", conn)
            total_users = int(total_users_df['total'][0]) if not total_users_df.empty else 0
            
            total_pontos_df = pd.read_sql("SELECT ISNULL(SUM(ISNULL(pontos_total, 0)), 0) as total FROM users", conn)
            total_pontos = float(total_pontos_df['total'][0]) if not total_pontos_df.empty else 0
            
        return templates.TemplateResponse("departamentos_lista.html", {
            "request": request,
            "departamentos": depts.to_dict('records'),
            "total_depts": total_depts,
            "total_users": total_users,
            "total_pontos": total_pontos
        })
    except Exception as e:
        return f"<h1>Erro carregando departamentos: {str(e)}</h1><a href='/'>← Dashboard</a>"


# ========== ADMIN EQUIPAS (JOIN nome real + fix delete refresh) ==========
@app.get("/admin-equipas", response_class=HTMLResponse)
async def admin_equipas_get(request: Request):
    equipas = []
    users_sem = []
    users_com = []
    try:
        with engine.connect() as conn:
            # Todas equipas c/ count
            equipas_df = pd.read_sql("""
                SELECT e.id, e.nome, COUNT(u.id) as users_count
                FROM equipas e LEFT JOIN users u ON u.equipa_id = e.id
                GROUP BY e.id, e.nome ORDER BY e.nome
            """, conn)
            equipas = equipas_df.to_dict('records') if not equipas_df.empty else []
            
            # Users SEM equipa + dept
            users_sem_df = pd.read_sql("""
                SELECT u.id, u.nome, COALESCE(d.nome, 'Sem Dept') as dept
                FROM users u LEFT JOIN departamentos d ON u.departamento_id = d.id
                WHERE u.equipa_id IS NULL ORDER BY u.nome
            """, conn)
            users_sem = users_sem_df.to_dict('records') if not users_sem_df.empty else []
            
            # Users COM equipa
            users_com_df = pd.read_sql("""
                SELECT u.id, u.nome, u.equipa_id, 
                       COALESCE(e.nome, 'Sem Nome') as equipa_nome,
                       COALESCE(d.nome, 'Sem Dept') as dept
                FROM users u 
                LEFT JOIN equipas e ON u.equipa_id = e.id
                LEFT JOIN departamentos d ON u.departamento_id = d.id
                WHERE u.equipa_id IS NOT NULL ORDER BY e.nome, u.nome
            """, conn)
            users_com = users_com_df.to_dict('records') if not users_com_df.empty else []
            
    except Exception as e:
        print(f"❌ admin-equipas GET: {e}")
    
    return templates.TemplateResponse("admin_equipas.html", {
        "request": request, 
        "equipas": equipas, 
        "users_sem": users_sem, 
        "users_com": users_com
    })

@app.post("/admin-equipas")
async def admin_equipas_post(
    nome: str = Form(None),           # 👥 Criar NOVA
    equipa_id: int = Form(None),      # 🔗 Associar EXISTENTE
    user_id: int = Form(None), 
    delete_id: int = Form(None),      # 🗑️ Delete (vazia)
    esvaziar_id: int = Form(None),    # 🧹 Esvaziar + delete
    transfer_id: int = Form(None),    # 🔄 Transferir users
    nova_equipa_id: int = Form(None)  # Para transfer
):
    msg = "❌ Erro desconhecido"
    try:
        with engine.connect() as conn:
            if nome:  # 👥 CRIAR
                nome = nome.strip()[:50]
                exists = conn.execute(text("SELECT id FROM equipas WHERE LOWER(nome) = LOWER(:nome)"), {"nome": nome}).first()
                if exists:
                    msg = f"❌ '{nome}' já existe!"
                else:
                    conn.execute(text("INSERT INTO equipas (nome) VALUES (:nome)"), {"nome": nome})
                    new_id = conn.execute(text("SELECT SCOPE_IDENTITY() as new_id")).scalar()
                    conn.commit()
                    msg = f"✅ '{nome}' criada (ID {new_id})!"
            
            elif equipa_id and user_id:  # 🔗 ASSOCIAR
                current = conn.execute(text("SELECT e.nome FROM users u LEFT JOIN equipas e ON u.equipa_id = e.id WHERE u.id = :user_id"), {"user_id": user_id}).scalar()
                if current:
                    msg = f"❌ Já tem equipa '{current}'!"
                else:
                    conn.execute(text("UPDATE users SET equipa_id = :equipa_id WHERE id = :user_id"), 
                               {"equipa_id": equipa_id, "user_id": user_id})
                    conn.commit()
                    msg = "✅ User associado!"
            
            elif delete_id:  # 🗑️ DELETE (só vazia)
                count = conn.execute(text("SELECT COUNT(*) FROM users WHERE equipa_id = :id"), {"id": delete_id}).scalar()
                if count > 0:
                    msg = f"❌ {count} users! Use 🧹 ou 🔄"
                else:
                    old_name = conn.execute(text("SELECT nome FROM equipas WHERE id = :id"), {"id": delete_id}).scalar()
                    conn.execute(text("DELETE FROM equipas WHERE id = :id"), {"id": delete_id})
                    conn.commit()
                    msg = f"✅ '{old_name}' eliminada!"
            
            elif esvaziar_id:  # 🧹 ESVAZIAR + DELETE
                count = conn.execute(text("SELECT COUNT(*) FROM users WHERE equipa_id = :id"), {"id": esvaziar_id}).scalar()
                old_name = conn.execute(text("SELECT nome FROM equipas WHERE id = :id"), {"id": esvaziar_id}).scalar()
                if count == 0:
                    msg = f"❌ '{old_name}' já vazia!"
                else:
                    conn.execute(text("UPDATE users SET equipa_id = NULL WHERE equipa_id = :id"), {"id": esvaziar_id})
                    conn.execute(text("DELETE FROM equipas WHERE id = :id"), {"id": esvaziar_id})
                    conn.commit()
                    msg = f"✅ '{old_name}' esvaziada ({count} users → SEM equipa)!"
            
            elif transfer_id and nova_equipa_id:  # 🔄 TRANSFERIR + DELETE
                count = conn.execute(text("SELECT COUNT(*) FROM users WHERE equipa_id = :id"), {"id": transfer_id}).scalar()
                old_name = conn.execute(text("SELECT nome FROM equipas WHERE id = :id"), {"id": transfer_id}).scalar()
                new_name = conn.execute(text("SELECT nome FROM equipas WHERE id = :new_id"), {"new_id": nova_equipa_id}).scalar()
                if count == 0:
                    msg = f"❌ '{old_name}' vazia!"
                elif transfer_id == nova_equipa_id:
                    msg = "❌ Não pode transferir para si mesma!"
                else:
                    conn.execute(text("UPDATE users SET equipa_id = :nova WHERE equipa_id = :old"), 
                               {"nova": nova_equipa_id, "old": transfer_id})
                    conn.execute(text("DELETE FROM equipas WHERE id = :id"), {"id": transfer_id})
                    conn.commit()
                    msg = f"✅ {count} users '{old_name}' → '{new_name}'!"
            
            else:
                msg = "❌ Ação inválida"
                
    except Exception as e:
        msg = f"❌ {str(e)[:60]}"
    
    return RedirectResponse(f"/admin-equipas?msg={msg}", status_code=303)







# Rotas auxiliares
@app.post("/delete-equipa")
async def delete_equipa(equipa_id: int = Form(...)):
    try:
        with engine.connect() as conn:
            pyodbc_conn = conn.connection
            cursor = pyodbc_conn.cursor()
            cursor.execute("UPDATE users SET equipa_id = NULL WHERE equipa_id = ?", (equipa_id,))
            cursor.execute("DELETE FROM equipas WHERE id = ?", (equipa_id,))
            pyodbc_conn.commit()
        return RedirectResponse("/admin-equipas?msg=✅ Equipa eliminada!", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin-equipas?msg=❌ {str(e)}", status_code=303)

@app.post("/associar-equipa")
async def associar_equipa(equipa_id: int = Form(...), user_id: int = Form(...)):
    try:
        with engine.connect() as conn:
            pyodbc_conn = conn.connection
            cursor = pyodbc_conn.cursor()
            cursor.execute("UPDATE users SET equipa_id = ? WHERE id = ?", (equipa_id, user_id))
            pyodbc_conn.commit()
        return RedirectResponse("/admin-equipas?msg=✅ User associado à equipa!", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin-equipas?msg=❌ {str(e)}", status_code=303)

# ========== ADMIN USERS (com fix pyodbc raw cursor) ==========
@app.get("/admin-users", response_class=HTMLResponse)
async def admin_users_get(request: Request):
    depts = []
    users = []
    total_users = 0
    try:
        with engine.connect() as conn:
            # Departamentos para form dropdown
            depts_df = pd.read_sql("SELECT id, nome FROM departamentos ORDER BY nome", conn)
            depts = depts_df.to_dict('records') if not depts_df.empty else []
            
            # Users com JOIN FORTE (COALESCE garante string nunca NULL)
            users_df = pd.read_sql("""
                SELECT 
                    u.id, u.nome, 
                    COALESCE(CAST(u.pontos_total AS DECIMAL(10,1)), 0) as pontos_total,
                    COALESCE(d.nome, 'Sem departamento') as departamento_nome,
                    ISNULL(e.nome, 'Sem equipa') as equipa_nome
                FROM users u
                LEFT JOIN departamentos d ON u.departamento_id = d.id
                LEFT JOIN equipas e ON u.equipa_id = e.id
                ORDER BY u.nome
            """, conn)
            
            if not users_df.empty:
                # Coerce NaN → 'Sem departamento' (pandas bug comum)
                users_df['departamento_nome'] = users_df['departamento_nome'].fillna('Sem departamento')
                users_df['equipa_nome'] = users_df['equipa_nome'].fillna('Sem equipa')
                users_df['pontos_total'] = pd.to_numeric(users_df['pontos_total'], errors='coerce').fillna(0)
                users = users_df.to_dict('records')
                total_users = len(users)
    except Exception as e:
        print(f"❌ admin-users: {e}")
    
    return templates.TemplateResponse("admin_users.html", {
        "request": request, 
        "departamentos": depts, 
        "users": users, 
        "total_users": total_users
    })

@app.post("/admin-users")
async def admin_users_post(nome: str = Form(...), departamento_id: int = Form(...)):
    msg = "❌ Erro desconhecido"
    try:
        nome = nome.strip()[:100]
        with engine.connect() as conn:
            result = conn.execute(text("""
                INSERT INTO users (nome, departamento_id, pontos_total, ferias_ganhas, equipa_id) 
                VALUES (:nome, :dept_id, 0, 0, NULL)
            """), {"nome": nome, "dept_id": departamento_id})
            conn.commit()
            msg = f"✅ {nome} criado no departamento {departamento_id}!"
    except Exception as e:
        msg = f"❌ {str(e)[:60]}"
    return RedirectResponse(f"/admin-users?msg={msg}", status_code=303)




@app.get("/colaborador/{user_id}", response_class=HTMLResponse)
async def pagina_colaborador(request: Request, user_id: int):
    try:
        with engine.connect() as conn:

            # Dados do colaborador
            user = pd.read_sql(text("""
               SELECT u.id, u.nome, u.equipa, u.pontos_total, u.ferias_ganhas
                FROM users u
                INNER JOIN departamentos d ON u.departamento_id = d.id
                WHERE d.nome = :nome
                ORDER BY u.pontos_total DESC
            """), conn, params={'nome': nome}).to_dict('records')

            if not user:
                return "Utilizador não encontrado"

            user = user[0]

            # Histórico últimos 20 eventos
            eventos = pd.read_sql(text("""
                SELECT TOP 20 tipo, pontos,
                       FORMAT(data_evento, 'HH:mm dd/MM/yyyy') as data_evento
                FROM eventos
                WHERE user_id = :u
                ORDER BY data_evento DESC
            """), conn, params={"u": user_id}).to_dict("records")

            # Ranking no departamento
            ranking_dept = pd.read_sql(text("""
                SELECT id,
                       RANK() OVER (ORDER BY pontos_total DESC) as pos
                FROM users
                WHERE departamento = :d
            """), conn, params={"d": user["departamento"]})

            pos_dept = ranking_dept[ranking_dept["id"] == user_id]["pos"].values
            pos_dept = int(pos_dept[0]) if len(pos_dept) > 0 else "-"

            # Ranking geral
            ranking_geral = pd.read_sql(text("""
                SELECT id,
                       RANK() OVER (ORDER BY pontos_total DESC) as pos
                FROM users
            """), conn)

            pos_geral = ranking_geral[ranking_geral["id"] == user_id]["pos"].values
            pos_geral = int(pos_geral[0]) if len(pos_geral) > 0 else "-"

        return templates.TemplateResponse(
            "colaborador.html",
            {
                "request": request,
                "user": user,
                "eventos": eventos,
                "pos_dept": pos_dept,
                "pos_geral": pos_geral
            }
        )

    except Exception as e:
        return f"Erro colaborador: {e}"

@app.get("/admin/movimento", response_class=HTMLResponse)
async def movimento_form(request: Request):
    with engine.connect() as conn:
        users = pd.read_sql(text("SELECT id, nome FROM users ORDER BY nome"), conn).to_dict("records")

    return templates.TemplateResponse(
        "movimento.html",
        {"request": request, "users": users}
    )

@app.post("/admin/movimento")
async def movimento_submit(
    user_id: int = Form(...),
    tipo: str = Form(...),
    pontos: int = Form(...),
    motivo: str = Form(...)
):
    try:
        if tipo == "negativo":
            pontos = -abs(pontos)

        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO eventos (user_id, tipo, pontos)
                VALUES (:u, :t, :p)
            """), {"u": user_id, "t": motivo, "p": pontos})

            conn.execute(text("""
                UPDATE users SET pontos_total += :p
                WHERE id = :u
            """), {"u": user_id, "p": pontos})

            conn.commit()

        return {"status": "ok"}

    except Exception as e:
        return {"erro": str(e)}

# ========== ADMIN PONTOS (multi-tarefas + trigger auto) ==========
@app.get("/admin-pontos", response_class=HTMLResponse)
async def admin_pontos_get(request: Request):
    try:
        # Todos users + dept/equipa JOIN
        users_df = pd.read_sql("""
            SELECT u.id, u.nome, u.pontos_total,
                   ISNULL(d.nome, 'Sem Dept') as dept_nome,
                   ISNULL(e.nome, 'Sem Equipa') as equipa_nome
            FROM users u
            LEFT JOIN departamentos d ON u.departamento_id = d.id
            LEFT JOIN equipas e ON u.equipa_id = e.id
            ORDER BY d.nome, u.nome
        """, engine)
        users_list = users_df.to_dict('records') if not users_df.empty else []
        
        # Depts únicos (dropdown)
        depts_df = pd.read_sql("SELECT DISTINCT id, nome FROM departamentos ORDER BY nome", engine)
        depts_list = depts_df.to_dict('records') if not depts_df.empty else []
        
    except Exception as e:
        print(f"❌ Erro pontos: {e}")
        users_list = depts_list = []
    
    return templates.TemplateResponse("admin_pontos.html", {
        "request": request,
        "users": users_list,
        "departamentos": depts_list
    })

@app.post("/admin-pontos")
async def admin_pontos_post(
    request: Request,
    user_id: int = Form(...),
    pontos: int = Form(1),
    motivo: str = Form("")
):
    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET pontos_total = pontos_total + ? WHERE id = ?", (pontos, user_id))
        conn.commit()
    except Exception as e:
        print(f"❌ Erro atribuir pontos: {e}")
    finally:
        cursor.close()
        conn.close()
    return RedirectResponse("/admin-pontos#success", status_code=303)


@app.post("/dept-colaboradores")
async def dept_colaboradores(dept_id: int = Form(...)):
    print(f"🔍 dept-colaboradores dept_id={dept_id}")
    try:
        # pyodbc RAW (nunca falha)
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nome, ISNULL(u.pontos_total, 0) as pontos_total,
                   ISNULL(e.nome, 'N/A') as equipa
            FROM users u
            LEFT JOIN equipas e ON u.equipa_id = e.id
            WHERE u.departamento_id = ?
            ORDER BY u.nome
        """, (dept_id,))
        
        # Lista rows sempre válida
        rows = cursor.fetchall()
        users = []
        for row in rows:
            users.append({
                "id": row.id,
                "nome": row.nome,
                "pontos_total": row.pontos_total,
                "equipa": row.equipa
            })
        
        cursor.close()
        conn.close()
        print(f"✅ dept_id={dept_id}: {len(users)} users")
        return JSONResponse({"users": users})
        
    except Exception as e:
        print(f"❌ dept-colaboradores {dept_id}: {e}")
        return JSONResponse({"users": []})




@app.post("/atribuir-pontos")
async def atribuir_pontos(user_id: int = Form(...), tarefas: str = Form(...)):
    try:
        pontos = len(tarefas.split(','))  # 1pt por tarefa
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET pontos_total = pontos_total + ? WHERE id = ?", (pontos, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return JSONResponse({"success": f"+{pontos} pts ({tarefas}) atribuídos!"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/ranking", response_class=HTMLResponse)
async def ranking(request: Request):
    with engine.connect() as conn:
        leaderboard = pd.read_sql(text("""
            SELECT nome, pontos_total
            FROM users
            ORDER BY pontos_total DESC
        """), conn).to_dict("records")

    return templates.TemplateResponse(
        "ranking.html",
        {"request": request, "leader": leaderboard}
    )

def calcular_nivel(pontos):
    if pontos >= 1000:
        return "PLATINA", 1000
    elif pontos >= 500:
        return "OURO", 1000
    elif pontos >= 200:
        return "PRATA", 500
    else:
        return "BRONZE", 200


@app.get("/leader")
async def leader_json():
    with engine.connect() as conn:
        return pd.read_sql(text("SELECT * FROM vw_leaderboard"), conn).to_dict('records')


# ── Rota: painel de estado do job CNC ───────────────────────
@app.get("/admin/cnc-status", response_class=HTMLResponse)
async def cnc_status(request: Request):
    """Mostra os últimos registos do log do job Sinex."""
    linhas = []
    log_path = os.path.join(os.path.dirname(__file__), "sinex_job.log")
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            linhas = f.readlines()[-80:]   # últimas 80 linhas

    # Utilizadores do dept CNC
    users_cnc = []
    try:
        with engine.connect() as conn:
            users_cnc = pd.read_sql(text("""
                SELECT u.nome,
                       ISNULL(u.pontos_total, 0)  AS pontos_total,
                       ISNULL(u.ferias_ganhas, 0) AS ferias_ganhas
                FROM users u
                INNER JOIN departamentos d ON u.departamento_id = d.id
                WHERE LOWER(d.nome) = 'cnc'
                ORDER BY u.pontos_total DESC
            """), conn).to_dict("records")
    except Exception as e:
        users_cnc = [{"nome": f"Erro: {e}", "pontos_total": 0, "ferias_ganhas": 0}]

    # Gera HTML simples inline (sem template extra)
    rows_users = "".join(
        f"<tr><td>{u['nome']}</td>"
        f"<td style='text-align:center'>{u['pontos_total']}</td>"
        f"<td style='text-align:center'>{u['ferias_ganhas']}</td></tr>"
        for u in users_cnc
    )

    log_html = "".join(
        f"<span style='color:{'#e74c3c' if 'ERROR' in l or '❌' in l else '#2ecc71' if '✅' in l else '#ecf0f1'}'>"
        f"{l.rstrip()}</span><br>"
        for l in linhas
    )

    html = f"""
    <!DOCTYPE html><html><head>
    <meta charset='utf-8'>
    <title>CNC Job Status</title>
    <style>
      body {{ font-family: monospace; background:#1a1a2e; color:#ecf0f1; padding:20px; }}
      h1 {{ color:#f39c12; }}
      h2 {{ color:#3498db; border-bottom:1px solid #3498db; padding-bottom:6px; }}
      table {{ border-collapse:collapse; width:100%; margin-bottom:30px; }}
      th {{ background:#2c3e50; padding:8px 12px; text-align:left; }}
      td {{ padding:6px 12px; border-bottom:1px solid #2c3e50; }}
      tr:hover td {{ background:#16213e; }}
      .log-box {{ background:#0d0d1a; padding:16px; border-radius:8px;
                  max-height:500px; overflow-y:auto; font-size:12px; line-height:1.6; }}
      a {{ color:#3498db; }}
    </style>
    </head><body>
    <h1>⚙️ CNC Job Status</h1>
    <p><a href='/'>← Dashboard</a> &nbsp;|&nbsp;
       <a href='/departamento/CNC'>Ver Dept CNC</a></p>

    <h2>👷 Operadores CNC ({len(users_cnc)})</h2>
    <table>
      <tr><th>Operador</th><th>Pontos</th><th>Férias Ganhas</th></tr>
      {rows_users if rows_users else "<tr><td colspan='3'>Nenhum operador ainda</td></tr>"}
    </table>

    <h2>📋 Últimas 80 linhas do Log</h2>
    <p style='color:#7f8c8d; font-size:12px'>Ficheiro: sinex_job.log</p>
    <div class='log-box'>{log_html if log_html else "Log vazio — job ainda não correu."}</div>
    </body></html>
    """
    return HTMLResponse(content=html)


# ═══════════════════════════════════════════════════════════════
#  LOJA DE PONTOS
# ═══════════════════════════════════════════════════════════════

@app.get("/loja", response_class=HTMLResponse)
async def loja_get(request: Request):
    try:
        with engine.connect() as conn:
            recompensas = pd.read_sql(text(
                "SELECT id, nome, descricao, custo_pontos FROM recompensas WHERE ativo = 1 ORDER BY custo_pontos"
            ), conn).to_dict("records")
            users = pd.read_sql(text(
                "SELECT id, nome, pontos_total FROM users ORDER BY nome"
            ), conn).to_dict("records")
    except Exception as e:
        return f"<h1>Erro loja: {e}</h1>"
    return templates.TemplateResponse("loja.html", {
        "request": request,
        "recompensas": recompensas,
        "users": users,
    })


@app.post("/loja/resgatar")
async def loja_resgatar(user_id: int = Form(...), recompensa_id: int = Form(...)):
    try:
        with engine.connect() as conn:
            rec = conn.execute(text(
                "SELECT nome, custo_pontos FROM recompensas WHERE id = :id AND ativo = 1"
            ), {"id": recompensa_id}).fetchone()
            if not rec:
                return RedirectResponse("/loja?msg=Recompensa+nao+encontrada", status_code=303)

            custo = int(rec[1])
            pts_atual = conn.execute(text(
                "SELECT pontos_total FROM users WHERE id = :id"
            ), {"id": user_id}).scalar()

            if pts_atual is None:
                return RedirectResponse("/loja?msg=Utilizador+nao+encontrado", status_code=303)
            if int(pts_atual) < custo:
                return RedirectResponse("/loja?msg=Pontos+insuficientes", status_code=303)

            # Desconta pontos
            conn.execute(text(
                "UPDATE users SET pontos_total = pontos_total - :custo WHERE id = :uid"
            ), {"custo": custo, "uid": user_id})

            # Regista resgate
            conn.execute(text("""
                INSERT INTO resgates (user_id, recompensa_id, pontos_gastos, estado)
                VALUES (:uid, :rid, :pts, 'pendente')
            """), {"uid": user_id, "rid": recompensa_id, "pts": custo})

            # Evento no histórico
            conn.execute(text("""
                INSERT INTO eventos (user_id, tipo, pontos)
                VALUES (:uid, :tipo, :pts)
            """), {"uid": user_id, "tipo": f"loja: {rec[0]}", "pts": -custo})

            conn.commit()
        return RedirectResponse(f"/loja?msg=Resgatado+com+sucesso", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/loja?msg=Erro:{str(e)[:50]}", status_code=303)


@app.get("/admin/loja", response_class=HTMLResponse)
async def admin_loja_get(request: Request):
    try:
        with engine.connect() as conn:
            recompensas = pd.read_sql(text(
                "SELECT id, nome, descricao, custo_pontos, ativo FROM recompensas ORDER BY custo_pontos"
            ), conn).to_dict("records")
            resgates = pd.read_sql(text("""
                SELECT r.id, u.nome as colaborador, rc.nome as recompensa,
                       r.pontos_gastos, r.estado,
                       FORMAT(r.data_resgate, 'dd/MM/yyyy HH:mm') as data_resgate
                FROM resgates r
                INNER JOIN users u ON u.id = r.user_id
                INNER JOIN recompensas rc ON rc.id = r.recompensa_id
                ORDER BY r.data_resgate DESC
            """), conn).to_dict("records")
    except Exception as e:
        return f"<h1>Erro admin loja: {e}</h1>"
    return templates.TemplateResponse("admin_loja.html", {
        "request": request,
        "recompensas": recompensas,
        "resgates": resgates,
    })


@app.post("/admin/loja/criar")
async def admin_loja_criar(
    nome: str = Form(...),
    descricao: str = Form(""),
    custo_pontos: int = Form(...),
):
    try:
        with engine.connect() as conn:
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
        with engine.connect() as conn:
            conn.execute(text(
                "UPDATE recompensas SET ativo = 1 - ativo WHERE id = :id"
            ), {"id": recompensa_id})
            conn.commit()
        return RedirectResponse("/admin/loja", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin/loja?msg=Erro:{str(e)[:50]}", status_code=303)


@app.post("/admin/loja/entregar")
async def admin_loja_entregar(resgate_id: int = Form(...)):
    try:
        with engine.connect() as conn:
            conn.execute(text(
                "UPDATE resgates SET estado = 'entregue' WHERE id = :id"
            ), {"id": resgate_id})
            conn.commit()
        return RedirectResponse("/admin/loja", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin/loja?msg=Erro:{str(e)[:50]}", status_code=303)


# ═══════════════════════════════════════════════════════════════
#  HISTÓRICO ANUAL
# ═══════════════════════════════════════════════════════════════

@app.get("/historico", response_class=HTMLResponse)
async def historico_get(request: Request, msg: str = ""):
    try:
        with engine.connect() as conn:
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
        "request": request,
        "historico": historico,
        "anos": anos_list,
        "msg": msg,
    })


# ═══════════════════════════════════════════════════════════════
#  TV DASHBOARD
# ═══════════════════════════════════════════════════════════════

@app.get("/tv", response_class=HTMLResponse)
async def tv_dashboard(request: Request):
    try:
        with engine.connect() as conn:
            top5 = pd.read_sql(text("""
                SELECT TOP 5
                    ROW_NUMBER() OVER (ORDER BY u.pontos_total DESC) as pos,
                    u.nome,
                    ISNULL(d.nome, 'Sem Dept') as departamento,
                    u.pontos_total
                FROM users u
                LEFT JOIN departamentos d ON d.id = u.departamento_id
                ORDER BY u.pontos_total DESC
            """), conn).to_dict("records")

            depts = pd.read_sql(text("""
                SELECT d.nome as departamento,
                       COUNT(u.id) as total_users,
                       ISNULL(SUM(u.pontos_total), 0) as total_pontos,
                       ISNULL(AVG(CAST(u.pontos_total AS FLOAT)), 0) as media_pontos
                FROM departamentos d
                LEFT JOIN users u ON u.departamento_id = d.id
                GROUP BY d.nome
                ORDER BY media_pontos DESC
            """), conn).to_dict("records")
    except Exception as e:
        return f"<h1>Erro TV: {e}</h1>"
    return templates.TemplateResponse("tv.html", {
        "request": request,
        "top5": top5,
        "depts": depts,
    })


# ═══════════════════════════════════════════════════════════════
#  RELATÓRIO MENSAL
# ═══════════════════════════════════════════════════════════════

@app.get("/admin/relatorio", response_class=HTMLResponse)
async def relatorio_get(request: Request):
    hoje = date.today()
    return templates.TemplateResponse("admin_relatorio.html", {
        "request": request,
        "resultado": None,
        "mes_default": hoje.month,
        "ano_default": hoje.year,
    })


@app.post("/admin/relatorio", response_class=HTMLResponse)
async def relatorio_post(request: Request, mes: int = Form(...), ano: int = Form(...)):
    try:
        with engine.connect() as conn:
            # Pontos ganhos no mês por colaborador
            df = pd.read_sql(text("""
                SELECT u.id, u.nome,
                       ISNULL(d.nome, 'Sem Dept') as departamento,
                       ISNULL(SUM(p.pontos), 0) as pontos_mes,
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

            # Stats por departamento
            dept_stats = pd.read_sql(text("""
                SELECT ISNULL(d.nome, 'Sem Dept') as departamento,
                       COUNT(DISTINCT u.id) as total_users,
                       ISNULL(SUM(p.pontos), 0) as total_pontos,
                       ISNULL(AVG(CAST(p.pontos AS FLOAT)), 0) as media_pontos
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
        depts_rel = dept_stats.to_dict("records")

        melhor = colaboradores[0] if colaboradores else None
        mais_consistente = max(colaboradores, key=lambda x: x["dias_positivos"]) if colaboradores else None

        resultado = {
            "mes": mes,
            "ano": ano,
            "colaboradores": colaboradores,
            "depts": depts_rel,
            "melhor": melhor,
            "mais_consistente": mais_consistente,
            "total_colaboradores": len(colaboradores),
        }
    except Exception as e:
        resultado = {"erro": str(e)}

    return templates.TemplateResponse("admin_relatorio.html", {
        "request": request,
        "resultado": resultado,
        "mes_default": mes,
        "ano_default": ano,
    })


@app.post("/admin/relatorio/exportar")
async def relatorio_exportar(mes: int = Form(...), ano: int = Form(...)):
    """Exporta relatório mensal em Excel."""
    try:
        with engine.connect() as conn:
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
        filename = f"relatorio_{ano}_{mes:02d}.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        return JSONResponse({"erro": str(e)}, status_code=500)


# ── Rota: reprocessamento manual por intervalo de datas ─────────────────────
@app.get("/admin/reprocessar", response_class=HTMLResponse)
async def admin_reprocessar_get(request: Request):
    return templates.TemplateResponse("admin_reprocessar.html", {
        "request": request,
        "resultado": None,
    })


@app.post("/admin/reprocessar", response_class=HTMLResponse)
async def admin_reprocessar_post(
    request: Request,
    data_inicio: str = Form(...),
    data_fim: str = Form(...),
):
    resultado = processar_intervalo(data_inicio, data_fim)
    return templates.TemplateResponse("admin_reprocessar.html", {
        "request": request,
        "resultado": resultado,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
    })


# ═══════════════════════════════════════════════════════════════
#  AUTENTICAÇÃO — LOGIN / LOGOUT
# ═══════════════════════════════════════════════════════════════

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request, next: str = "/"):
    user = get_session_user(request)
    if user:
        return RedirectResponse("/minha-area" if user.get("tipo") == "user" else "/")
    return templates.TemplateResponse("login.html", {"request": request, "next": next, "erro": ""})


@app.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
):
    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, user_id, username, password_hash, tipo FROM contas WHERE username = ?",
            (username.strip(),)
        )
        row = cursor.fetchone()
        conn.close()
    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request, "next": next,
            "erro": f"Erro de ligação à base de dados: {e}"
        })

    if not row or not verify_password(password, row.password_hash):
        return templates.TemplateResponse("login.html", {
            "request": request, "next": next,
            "erro": "Utilizador ou password incorretos."
        })

    session_data = {
        "conta_id": int(row.id),
        "user_id":  int(row.user_id) if row.user_id else None,
        "username": row.username,
        "tipo":     row.tipo,
    }
    token = create_session_token(session_data)

    destino = next if next and next != "/" else (
        "/minha-area" if row.tipo == "user" else "/"
    )
    response = RedirectResponse(destino, status_code=303)
    response.set_cookie(
        SESSION_COOKIE, token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


# ═══════════════════════════════════════════════════════════════
#  ÁREA DO UTILIZADOR (user normal)
# ═══════════════════════════════════════════════════════════════

@app.get("/minha-area", response_class=HTMLResponse)
async def minha_area(request: Request):
    session = request.state.user
    if not session:
        return RedirectResponse("/login")

    user_id = session.get("user_id")
    if not user_id:
        # Conta de admin sem user associado
        return templates.TemplateResponse("minha_area.html", {
            "request": request,
            "colaborador": None,
            "eventos": [],
            "pos_geral": "-",
            "total_users": "-",
            "recompensas": [],
        })

    try:
        with engine.connect() as conn:
            colab_df = pd.read_sql(text("""
                SELECT u.id, u.nome,
                       ISNULL(u.pontos_total, 0) as pontos_total,
                       ISNULL(u.ferias_ganhas, 0) as ferias_ganhas,
                       ISNULL(d.nome, 'Sem Dept') as departamento,
                       ISNULL(e.nome, 'Sem Equipa') as equipa
                FROM users u
                LEFT JOIN departamentos d ON d.id = u.departamento_id
                LEFT JOIN equipas e ON e.id = u.equipa_id
                WHERE u.id = :uid
            """), conn, params={"uid": user_id})

            if colab_df.empty:
                return templates.TemplateResponse("minha_area.html", {
                    "request": request, "colaborador": None,
                    "eventos": [], "pos_geral": "-", "total_users": "-", "recompensas": [],
                })

            colaborador = colab_df.iloc[0].to_dict()

            eventos = pd.read_sql(text("""
                SELECT TOP 15 tarefa, pontos,
                       FORMAT(data_pontos, 'dd/MM/yyyy') as data_fmt
                FROM pontos
                WHERE user_id = :uid
                ORDER BY data_pontos DESC, id DESC
            """), conn, params={"uid": user_id}).to_dict("records")

            ranking = pd.read_sql(text("""
                SELECT COUNT(*) as pos
                FROM users
                WHERE pontos_total > :pts
            """), conn, params={"pts": int(colaborador["pontos_total"])}).iloc[0, 0]
            pos_geral = int(ranking) + 1

            total_users = pd.read_sql(
                "SELECT COUNT(*) as t FROM users", conn
            ).iloc[0, 0]

            recompensas = pd.read_sql(text(
                "SELECT id, nome, descricao, custo_pontos FROM recompensas WHERE ativo = 1 ORDER BY custo_pontos"
            ), conn).to_dict("records")

    except Exception as e:
        return f"<h1>Erro: {e}</h1>"

    return templates.TemplateResponse("minha_area.html", {
        "request": request,
        "colaborador": colaborador,
        "eventos": eventos,
        "pos_geral": pos_geral,
        "total_users": int(total_users),
        "recompensas": recompensas,
    })


# ═══════════════════════════════════════════════════════════════
#  GESTÃO DE CONTAS (admin)
# ═══════════════════════════════════════════════════════════════

@app.get("/admin/contas", response_class=HTMLResponse)
async def admin_contas_get(request: Request, msg: str = ""):
    try:
        with engine.connect() as conn:
            contas = pd.read_sql(text("""
                SELECT c.id, c.username, c.tipo,
                       ISNULL(u.nome, '— sem colaborador —') as colaborador_nome,
                       c.user_id
                FROM contas c
                LEFT JOIN users u ON u.id = c.user_id
                ORDER BY c.tipo DESC, c.username
            """), conn).to_dict("records")

            users_sem_conta = pd.read_sql(text("""
                SELECT u.id, u.nome
                FROM users u
                WHERE u.id NOT IN (SELECT user_id FROM contas WHERE user_id IS NOT NULL)
                ORDER BY u.nome
            """), conn).to_dict("records")

    except Exception as e:
        return f"<h1>Erro contas: {e}</h1>"

    return templates.TemplateResponse("admin_contas.html", {
        "request": request,
        "contas": contas,
        "users_sem_conta": users_sem_conta,
        "msg": msg,
    })


@app.post("/admin/contas/criar")
async def admin_contas_criar(
    username: str = Form(...),
    password: str = Form(...),
    tipo: str = Form(...),
    user_id: str = Form(""),
):
    try:
        uid = int(user_id) if user_id.strip() else None
        hashed = hash_password(password)
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contas (user_id, username, password_hash, tipo) VALUES (?, ?, ?, ?)",
            (uid, username.strip(), hashed, tipo)
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
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE contas SET password_hash = ? WHERE id = ?",
            (hashed, conta_id)
        )
        conn.commit()
        conn.close()
        return RedirectResponse("/admin/contas?msg=✅ Password alterada!", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin/contas?msg=❌ Erro: {str(e)[:80]}", status_code=303)


@app.post("/admin/contas/delete")
async def admin_contas_delete(conta_id: int = Form(...), request: Request = None):
    # Não permite apagar a própria conta
    session = request.state.user if request else None
    if session and session.get("conta_id") == conta_id:
        return RedirectResponse("/admin/contas?msg=❌ Não podes apagar a tua própria conta.", status_code=303)
    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contas WHERE id = ?", (conta_id,))
        conn.commit()
        conn.close()
        return RedirectResponse("/admin/contas?msg=✅ Conta eliminada.", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin/contas?msg=❌ Erro: {str(e)[:80]}", status_code=303)


# ── RECALCULAR pontos_total (correção de emergência) ──────────────────────────
@app.post("/admin/recalcular-pontos")
async def recalcular_pontos_total():
    """
    Recalcula users.pontos_total a partir da soma real da tabela pontos.
    Corrige qualquer desvio causado por triggers, double-updates, etc.
    """
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=192.168.10.156;"
            "DATABASE=jogo_socem;"
            "UID=GV;"
            "PWD=NovaSenhaForte987;"
            "TrustServerCertificate=Yes;"
        )
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE u
            SET u.pontos_total = ISNULL(p.soma, 0)
            FROM users u
            LEFT JOIN (
                SELECT user_id, SUM(pontos) AS soma
                FROM pontos
                GROUP BY user_id
            ) p ON p.user_id = u.id
        """)
        afetados = cursor.rowcount
        conn.commit()
        conn.close()
        return JSONResponse({"ok": True, "utilizadores_atualizados": afetados})
    except Exception as e:
        return JSONResponse({"ok": False, "erro": str(e)}, status_code=500)