from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import get_connection
import pyodbc
from datetime import datetime, timedelta
from flask import send_file
import pandas as pd
from io import BytesIO
import io
from fastapi import Response  # ← ADICIONA esta linha
import secrets 
from zoneinfo import ZoneInfo
import time

app = FastAPI(title="GSMED v2.3 - Com Empresas + Departamentos + Strftime")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ FILTRO STRFTIME CUSTOMIZADO (resolve erro computadores.html)
def strftime_filter(value, format='%Y-%m-%d %H:%M:%S'):
    if value is None or value == "":
        return ""
    
    # ✅ Se já é datetime
    if isinstance(value, datetime):
        return value.strftime(format)
    
    # ✅ Se é string, tenta parse
    if isinstance(value, str):
        try:
            # Tenta formatos comuns do SQL Server
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d', '%Y%m%d']:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime(format)
                except ValueError:
                    continue
        except:
            pass
        return value  # Retorna string original
    
    return str(value)

templates.env.filters['strftime'] = strftime_filter

# ✅ LOGIN CORRIGIDO (com DEBUG + tratamento bytes varbinary)
def verify_user_credentials(username: str, password: str):
    print(f"🔐 DEBUG LOGIN: username='{username}', password='{password}'")
    if not username:
        print("⚠ Sem username")
        return None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PasswordHash, NomeCompleto FROM Users WHERE Username=? AND Ativo=1", (username,))
    row = cursor.fetchone()
    conn.close()

    print(f"🔍 DEBUG DB: row={row}")

    if not row:
        print("❌ Utilizador não encontrado ou inativo")
        return None

    # ✅ TRATAMENTO CORRIGIDO PARA VARBINARY
    raw_hash = row.PasswordHash
    if isinstance(raw_hash, (bytes, bytearray)):
        password_hash = raw_hash.decode('latin1').rstrip('\x00')  # ← MUDANÇA AQUI
    else:
        password_hash = str(raw_hash)

    print(f"🔍 DEBUG MATCH: hash='{password_hash}' == '{password}'")

    if password_hash == password:
        print(f"✅ LOGIN OK: {row.NomeCompleto}")
        return row.NomeCompleto  # ← Retorna NomeCompleto para compatibilidade

    print("❌ Password inválida")
    return None

def get_db_user(username: str):
    print(f"🧑 DEBUG get_db_user: '{username}'")
    if not username:
        print("⚠ Sem username")
        return None
    username = username.strip()  # ← ADICIONA ESTA LINHA
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT NomeCompleto FROM Users WHERE Username=? AND Ativo=1", (username,))
    row = cursor.fetchone()
    conn.close()
    user_exists = row.NomeCompleto if row else None
    print(f"🧑 DEBUG get_db_user: {'OK' if user_exists else 'FALHOU'} - row={row}")
    return user_exists

# 🆕 SISTEMA DE SESSÃO (dicionário em memória - simples e seguro para rede interna)
SESSION_DB = {}  # {session_token: {'username': 'admin', 'expires': timestamp}}

def create_session(username: str):
    token = secrets.token_urlsafe(32)
    SESSION_DB[token] = {
        'username': username,
        'expires': datetime.now() + timedelta(minutes=30)
    }
    print(f"🔐 SESSÃO CRIADA para '{username}'")
    return token

def get_session_user(request: Request):
    """Lê cookie de sessão e retorna username se válida, senão None"""
    session_token = request.cookies.get('gsmed_session')
    if not session_token:
        print("❌ Sem cookie de sessão")
        return None
    
    if session_token not in SESSION_DB:
        print("❌ Token inválido")
        return None
    
    session_data = SESSION_DB[session_token]
    if datetime.now() > session_data['expires']:
        print("❌ Sessão expirada")
        del SESSION_DB[session_token]
        return None
    
    username = session_data['username']
    print(f"✅ SESSÃO VÁLIDA: user='{username}' de token={session_token[:8]}...")
    return username

def clear_session(response: Response):
    """Limpa cookie de sessão"""
    response.set_cookie('gsmed_session', '', max_age=-1, httponly=True)

def get_empresas():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT IdEmpresa, Nome FROM Empresas WHERE Ativo=1 ORDER BY Nome")
        empresas = [{"id": row.IdEmpresa, "nome": row.Nome} for row in cursor.fetchall()]
        conn.close()
        return empresas
    except Exception as e:
        print(f"❌ Erro get_empresas: {e}")
        return []

def get_departamentos():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.IdDepartamento, d.Nome, d.IdEmpresa, e.Nome as EmpresaNome
            FROM Departamentos d
            LEFT JOIN Empresas e ON d.IdEmpresa = e.IdEmpresa
            ORDER BY e.Nome, d.Nome
            -- ✅ SEM WHERE Ativo=1 (não existe)
        """)
        depts = [{"id": row.IdDepartamento, "nome": row.Nome, "empresa_id": row.IdEmpresa, "empresa_nome": row.EmpresaNome} for row in cursor.fetchall()]
        conn.close()
        return depts
    except Exception as e:
        print(f"❌ Erro get_departamentos: {e}")
        return []

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print("🏠 GET / (login)")
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/do_login")
async def do_login(request: Request, username: str = Form(...), password: str = Form(...)):
    print("🚀 POST /do_login")
    user_name = verify_user_credentials(username, password)
    if user_name:
        session_token = create_session(username)
        response = RedirectResponse("/computadores", status_code=303)
        response.set_cookie(
            key='gsmed_session',
            value=session_token,
            httponly=True,
            secure=False,
            samesite='lax',
            max_age=1800  # ← SÓ ISTO: 30 minutos, sem expires
        )
        print(f"✅ LOGIN + COOKIE OK (30min)")
        return response
    
    print("❌ LOGIN FALHOU")
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "❌ Credenciais inválidas!"
    })

@app.get("/logout")
async def logout(request: Request):
    """Logout: limpa sessão"""
    response = RedirectResponse(url="/", status_code=303)
    clear_session(response)
    print("🚪 LOGOUT: sessão limpa")
    return response

@app.get("/computadores")
async def computadores(request: Request, view: str = "todos", page: int = 1, per_page: int = 20):
    print(f"🧭 DEBUG /computadores: view='{view}', page={page}, per_page={per_page}")
    
    # 🆕 VERIFICAÇÃO DE SESSÃO (IGNORA ?user= da URL)
    username = get_session_user(request)
    if not username:
        print("🔒 ACESSO NEGADO → redirect /")
        response = RedirectResponse(url="/", status_code=303)
        clear_session(response)
        return response
    
    # 🆕 Usa username da sessão (não da query!)
    db_user = get_db_user(username)
    if not db_user:
        print("🔒 USER DA SESSÃO INVÁLIDO → login")
        response = RedirectResponse(url="/", status_code=303)
        clear_session(response)
        return response
    
    # ← TODO O TEU CÓDIGO ATUAL A PARTIR DAQUI (exatamente igual)
    def normalize_estado(valor):
        if not valor:
            return ""
        return str(valor).lower().replace(" ", "")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # JOIN com nomes
    cursor.execute("""
        SELECT c.*, e.Nome as EmpresaNome, d.Nome as DepartamentoNome
        FROM Computadores c
        LEFT JOIN Empresas e ON c.IdEmpresa = e.IdEmpresa
        LEFT JOIN Departamentos d ON c.IdDepartamento = d.IdDepartamento
        ORDER BY c.IdPC DESC
    """)
    rows = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Computadores WHERE 1=0")
    colunas_base = [desc[0] for desc in cursor.description]
    
    computadores = []
    for row in rows:
        pc_dict = dict(zip(colunas_base, row))
        pc_dict['EmpresaNome'] = row.EmpresaNome or ''
        pc_dict['DepartamentoNome'] = row.DepartamentoNome or ''
        computadores.append(pc_dict)
    
    # FORMATAÇÃO (igual)
    for pc in computadores:
        for campo_data in ['DataAquisicao', 'DataFormatacao', 'DataManutencao']:
            data = pc.get(campo_data)
            if data and isinstance(data, str) and data.strip():
                try:
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                        try:
                            dt = datetime.strptime(str(data), fmt)
                            pc[f'{campo_data}Formatada'] = dt.strftime('%d/%m/%Y')
                            break
                        except ValueError:
                            continue
                except:
                    pc[f'{campo_data}Formatada'] = data
        
        pc['TipoPC'] = pc.get('TipoPC') or '—'
        pc['Utilizador'] = pc.get('Utilizador') or '—'
        pc['Anydesk'] = pc.get('Anydesk') or '—'
        
        obs = pc.get('Observacoes')
        pc['Observacoes'] = (obs[:50] + '...' if obs and len(obs) > 50 else obs) or '—'
        
        pc['Hostname'] = pc.get('Hostname') or '—'
        pc['EstadoNormalizado'] = normalize_estado(pc.get('Estado'))
    
    empresas = get_empresas()
    departamentos = get_departamentos()
    
    # LER FILTROS ATIVOS (igual)
    filtros_ativos = {
        "empresa": request.query_params.get("empresa", ""),
        "departamento": request.query_params.get("departamento", ""),
        "cpu": request.query_params.get("cpu", ""),
        "gpu": request.query_params.get("gpu", ""),
        "utilizador": request.query_params.get("utilizador", ""),
        "ram_min": request.query_params.get("ram_min", ""),
        "estado": request.query_params.get("estado", "")
    }
    
    # APLICAÇÃO DOS FILTROS COMBINADOS (igual)
    def string_match(value, filtro):
        if not filtro:
            return True
        if not value:
            return False
        return filtro.lower() in str(value).lower()
    
    def int_at_least(value, minimo):
        if not minimo:
            return True
        try:
            return int(value or 0) >= int(minimo)
        except ValueError:
            return False
    
    computadores_filtrados = []
    for pc in computadores:
        if filtros_ativos["empresa"] and str(pc.get("IdEmpresa") or "") != str(filtros_ativos["empresa"]):
            continue
        if filtros_ativos["departamento"] and str(pc.get("IdDepartamento") or "") != str(filtros_ativos["departamento"]):
            continue
        estado_filtro = normalize_estado(filtros_ativos["estado"])
        if estado_filtro and pc.get("EstadoNormalizado") != estado_filtro:
            continue
        if not string_match(pc.get("CPU"), filtros_ativos["cpu"]):
            continue
        if not string_match(pc.get("GPU"), filtros_ativos["gpu"]):
            continue
        if not string_match(pc.get("Utilizador"), filtros_ativos["utilizador"]):
            continue
        if not int_at_least(pc.get("RAM_GB"), filtros_ativos["ram_min"]):
            continue
        computadores_filtrados.append(pc)
    
    if view == "ativos":
        computadores_finais = [pc for pc in computadores_filtrados if pc.get('EstadoNormalizado') == 'emuso']
    elif view == "stock":
        computadores_finais = [pc for pc in computadores_filtrados if pc.get('EstadoNormalizado') == 'stock']
    elif view == "abate":
        computadores_finais = [pc for pc in computadores_filtrados if pc.get('EstadoNormalizado') == 'abatido']
    else:
        computadores_finais = computadores_filtrados
    
    # PAGINAÇÃO
    total_items = len(computadores_finais)
    total_pages = (total_items + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    computadores_paginados = computadores_finais[start_idx:end_idx]
    
    resumo = {
        'total': total_items,
        'emuso': sum(1 for pc in computadores_finais if pc.get('EstadoNormalizado') == 'emuso'),
        'stock': sum(1 for pc in computadores_finais if pc.get('EstadoNormalizado') == 'stock'),
        'abatido': sum(1 for pc in computadores_finais if pc.get('EstadoNormalizado') == 'abatido')
    }
    
    conn.close()
    
    # 🆕 TEMPLATE USA user_param DA SESSÃO (não da URL)
    return templates.TemplateResponse("computadores.html", {
        "request": request,
        "computadores": computadores_paginados,
        "empresas": empresas,
        "departamentos": departamentos,
        "filtros_ativos": filtros_ativos,
        "colunas": colunas_base,
        "view": view,
        "user": username,  # ← Da sessão!
        "user_param": username,  # ← Da sessão!
        "user_nome": db_user[0],
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "total_items": total_items,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": page - 1,
        "next_page": page + 1,
        "resumo": resumo
    })

@app.get("/utilizadores/novo", response_class=HTMLResponse)
async def novo_utilizador(request: Request):
    # 🔐 Só user autenticado
    username = get_session_user(request)
    if not username:
        return RedirectResponse(url="/", status_code=303)

    # (Opcional) só admins
    # conn = get_connection()
    # cur = conn.cursor()
    # cur.execute("SELECT r.Nome FROM Users u JOIN Roles r ON u.IdRole = r.IdRole WHERE u.Username=? AND u.Ativo=1", (username,))
    # role_row = cur.fetchone()
    # if not role_row or role_row.Nome.lower() != "admin":
    #     conn.close()
    #     return RedirectResponse(url="/computadores", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT IdRole, Nome FROM Roles ORDER BY Nome")
    roles = cur.fetchall()
    conn.close()

    db_user = get_db_user(username)

    return templates.TemplateResponse("novo_user.html", {
        "request": request,
        "user": username,
        "user_param": username,
        "user_nome": db_user[0],
        "roles": roles,
        "error": None
    })

@app.post("/utilizadores/novo", response_class=HTMLResponse)
async def criar_utilizador(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    nome_completo: str = Form(...),
    email: str = Form(...),
    id_role: int = Form(...),
):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT 1 FROM Users WHERE Username=?", (username,))
    if cur.fetchone():
        db_user = get_db_user(user_sess)
        cur.execute("SELECT IdRole, Nome FROM Roles ORDER BY Nome")
        roles = cur.fetchall()
        conn.close()
        return templates.TemplateResponse("novo_user.html", {
            "request": request, "user": user_sess, "user_param": user_sess, "user_nome": db_user[0],
            "roles": roles, "error": "❌ Username já existe."
        })

    # 🆕 SEM PasswordSalt (NULL automático)
    password_hash = password.encode('latin1')  # ← Bytes seguros
    password_salt = b'\x00'                    # ← Byte nulo para VARBINARY

    cur.execute("""
        INSERT INTO Users (Username, PasswordHash, PasswordSalt, NomeCompleto, Email, Ativo, IdRole, DataCriacao)
        VALUES (?, ?, ?, ?, ?, 1, ?, GETDATE())
    """, (username, password_hash, password_salt, nome_completo, email, id_role))
    conn.commit()
    
    print(f"✅ NOVO USER: '{username}' criado!")
    conn.close()
    return RedirectResponse(url="/computadores", status_code=303)

@app.get("/utilizadores", response_class=HTMLResponse)
async def listar_utilizadores(request: Request):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    db_user = get_db_user(user_sess)

    conn = get_connection()
    cur = conn.cursor()
    
    # JOIN Users + Roles
    cur.execute("""
        SELECT u.IdUser, u.Username, u.NomeCompleto, u.Email, u.Ativo, 
               r.Nome as RoleNome, u.DataCriacao
        FROM Users u
        LEFT JOIN Roles r ON u.IdRole = r.IdRole
        ORDER BY u.DataCriacao DESC
    """)
    users = cur.fetchall()
    
    # Colunas para tabela
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Users' ORDER BY ORDINAL_POSITION")
    colunas_users = [row[0] for row in cur.fetchall()]
    
    conn.close()

    return templates.TemplateResponse("lista_users.html", {
        "request": request,
        "user": user_sess, "user_param": user_sess, "user_nome": db_user[0],
        "users": users,
        "colunas": colunas_users
    })

@app.get("/utilizadores/editar/{user_id}", response_class=HTMLResponse)
async def editar_utilizador(request: Request, user_id: int):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    
    # Busca user + role atual
    cur.execute("""
        SELECT u.IdUser, u.Username, u.NomeCompleto, u.Email, u.Ativo, u.IdRole,
               r.Nome as RoleNome
        FROM Users u
        LEFT JOIN Roles r ON u.IdRole = r.IdRole
        WHERE u.IdUser = ?
    """, (user_id,))
    user_data = cur.fetchone()
    
    # Todas as roles disponíveis
    cur.execute("SELECT IdRole, Nome FROM Roles ORDER BY Nome")
    all_roles = cur.fetchall()
    
    conn.close()
    
    if not user_data:
        return RedirectResponse(url="/utilizadores", status_code=303)
    
    return templates.TemplateResponse("editar_user.html", {
        "request": request,
        "user": user_sess, "user_param": user_sess, 
        "user_nome": get_db_user(user_sess)[0],
        "user_data": user_data,
        "all_roles": all_roles
    })

@app.post("/utilizadores/editar/{user_id}")
async def salvar_edicao(request: Request, user_id: int,
                       nome_completo: str = Form(...),
                       email: str = Form(""),
                       id_role: int = Form(...),
                       ativo: int = Form(1),
                       new_password: str = Form(None)):

    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)
    
    conn = get_connection()
    cur = conn.cursor()
    
    if new_password:
        # ✅ BYTES explícitos (FUNCIONA 100%)
        password_hash_bytes = new_password.encode('latin1') + b'\x00'
        
        cur.execute("""
            UPDATE Users 
            SET NomeCompleto = ?, Email = ?, IdRole = ?, Ativo = ?, PasswordHash = ?
            WHERE IdUser = ?
        """, (nome_completo, email, id_role, bool(ativo), password_hash_bytes, user_id))
        print(f"✅ USER {user_id} atualizado + NOVA PASSWORD '{new_password}' por '{user_sess}'")
    else:
        cur.execute("""
            UPDATE Users 
            SET NomeCompleto = ?, Email = ?, IdRole = ?, Ativo = ?
            WHERE IdUser = ?
        """, (nome_completo, email, id_role, bool(ativo), user_id))
        print(f"✅ USER {user_id} atualizado por '{user_sess}'")
    
    conn.commit()
    conn.close()
    return RedirectResponse(url="/utilizadores", status_code=303)

@app.post("/utilizadores/ativar/{user_id}")
async def toggle_user_status(request: Request, user_id: int):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Toggle Ativo (1→0 ou 0→1)
    cur.execute("SELECT Ativo FROM Users WHERE IdUser = ?", (user_id,))
    current_status = cur.fetchone()
    
    new_status = 0 if current_status and current_status[0] else 1
    
    cur.execute("UPDATE Users SET Ativo = ? WHERE IdUser = ?", (new_status, user_id))
    conn.commit()
    conn.close()
    
    status_text = "ativado" if new_status else "desativado"
    print(f"✅ USER {user_id} {status_text} por '{user_sess}'")
    
    return RedirectResponse(url="/utilizadores", status_code=303)

# ---------- EMPRESAS ----------

@app.get("/empresas", response_class=HTMLResponse)
async def listar_empresas(request: Request):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT IdEmpresa, Nome, NIF, Ativo
        FROM Empresas
        ORDER BY Nome
    """)
    empresas = cur.fetchall()
    conn.close()

    return templates.TemplateResponse("lista_empresas.html", {
        "request": request,
        "user": user_sess, "user_nome": get_db_user(user_sess)[0],
        "empresas": empresas
    })


@app.get("/empresas/nova", response_class=HTMLResponse)
async def nova_empresa(request: Request):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse("editar_empresa.html", {
        "request": request,
        "user": user_sess, "user_nome": get_db_user(user_sess)[0],
        "empresa": None
    })


@app.post("/empresas/nova")
async def criar_empresa(request: Request,
                        nome: str = Form(...),
                        nif: str = Form(""),
                        ativo: int = Form(1)):

    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Empresas (Nome, NIF, Ativo)
        VALUES (?, ?, ?)
    """, (nome, nif or None, bool(ativo)))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/empresas", status_code=303)


@app.get("/empresas/editar/{id_empresa}", response_class=HTMLResponse)
async def editar_empresa(request: Request, id_empresa: int):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT IdEmpresa, Nome, NIF, Ativo
        FROM Empresas
        WHERE IdEmpresa = ?
    """, (id_empresa,))
    empresa = cur.fetchone()
    conn.close()

    if not empresa:
        return RedirectResponse(url="/empresas", status_code=303)

    return templates.TemplateResponse("editar_empresa.html", {
        "request": request,
        "user": user_sess, "user_nome": get_db_user(user_sess)[0],
        "empresa": empresa
    })


@app.post("/empresas/editar/{id_empresa}")
async def guardar_empresa(request: Request, id_empresa: int,
                          nome: str = Form(...),
                          nif: str = Form(""),
                          ativo: int = Form(1)):

    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE Empresas
        SET Nome = ?, NIF = ?, Ativo = ?
        WHERE IdEmpresa = ?
    """, (nome, nif or None, bool(ativo), id_empresa))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/empresas", status_code=303)


@app.post("/empresas/remover/{id_empresa}")
async def remover_empresa(request: Request, id_empresa: int):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    # Opcional: validar se há computadores ligados à empresa antes de apagar
    cur.execute("DELETE FROM Empresas WHERE IdEmpresa = ?", (id_empresa,))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/empresas", status_code=303)

# ---------- DEPARTAMENTOS ----------
# =====================================================

@app.get("/departamentos", response_class=HTMLResponse)
async def listar_departamentos(request: Request):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.IdDepartamento, d.Nome, e.Nome as EmpresaNome, d.Ativo
        FROM Departamentos d
        LEFT JOIN Empresas e ON d.IdEmpresa = e.IdEmpresa
        ORDER BY e.Nome, d.Nome
    """)
    departamentos = []
    for row in cur.fetchall():
        departamentos.append({
            'IdDepartamento': row[0],
            'Nome': row[1],
            'EmpresaNome': row[2] or '-',
            'Ativo': row[3]
        })
    conn.close()

    return templates.TemplateResponse("lista_departamentos.html", {
        "request": request,
        "user": user_sess, 
        "user_nome": get_db_user(user_sess)[0],
        "departamentos": departamentos
    })

@app.get("/departamentos/nova", response_class=HTMLResponse)
async def novo_departamento(request: Request):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT IdEmpresa, Nome FROM Empresas ORDER BY Nome")
    empresas = []
    for row in cur.fetchall():
        empresas.append({'IdEmpresa': row[0], 'Nome': row[1]})
    conn.close()
    
    return templates.TemplateResponse("novo_departamento.html", {
        "request": request, 
        "empresas": empresas, 
        "user": user_sess, 
        "user_nome": get_db_user(user_sess)[0]
    })

@app.post("/departamentos/nova")
async def criar_departamento(request: Request, nome: str = Form(...), empresa_id: int = Form(...)):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Departamentos (Nome, IdEmpresa, Ativo) VALUES (?, ?, 1)", (nome.strip(), empresa_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/departamentos?sucesso=criado", status_code=303)

@app.get("/departamentos/{dep_id}/editar", response_class=HTMLResponse)
async def editar_departamento(request: Request, dep_id: int):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT IdDepartamento, Nome, IdEmpresa, Ativo FROM Departamentos WHERE IdDepartamento = ?", (dep_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404)
    
    departamento = {'IdDepartamento': row[0], 'Nome': row[1], 'IdEmpresa': row[2], 'Ativo': row[3]}
    
    cur2 = get_connection().cursor()
    cur2.execute("SELECT IdEmpresa, Nome FROM Empresas ORDER BY Nome")
    empresas = [{'IdEmpresa': r[0], 'Nome': r[1]} for r in cur2.fetchall()]
    cur2.connection.close()
    
    return templates.TemplateResponse("editar_departamento.html", {
        "request": request, "departamento": departamento, "empresas": empresas,
        "user": user_sess, "user_nome": get_db_user(user_sess)[0]
    })

@app.post("/departamentos/editar/{id_departamento}")
async def guardar_departamento(request: Request, id_departamento: int, nome: str = Form(...), 
                               id_empresa: int = Form(...), ativo: int = Form(1)):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Departamentos SET Nome = ?, IdEmpresa = ?, Ativo = ? WHERE IdDepartamento = ?",
                (nome.strip(), id_empresa, bool(ativo), id_departamento))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/departamentos?sucesso=editado", status_code=303)

@app.post("/departamentos/remover/{id_departamento}")
async def remover_departamento(request: Request, id_departamento: int):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Departamentos WHERE IdDepartamento = ?", (id_departamento,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/departamentos?removido=ok", status_code=303)
# =====================================================



@app.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard_admin(request: Request):
    user_sess = get_session_user(request)
    if not user_sess:
        return RedirectResponse(url="/", status_code=303)
    
    # 🔢 STATS COMPUTADORES
    conn = get_connection()
    cur = conn.cursor()
    
    # Total PCs + estados
    cur.execute("SELECT COUNT(*) FROM Computadores")
    total_pcs = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM Computadores WHERE Estado='EmUso'")
    em_uso = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM Computadores WHERE Estado='Stock'")
    stock = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM Computadores WHERE Estado='Abatido'")
    abatido = cur.fetchone()[0]
    
    # 🆕 STATS UTILIZADORES
    cur.execute("SELECT COUNT(*) FROM Users WHERE Ativo=1")
    users_ativos = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM Users WHERE Ativo=0")
    users_inativos = cur.fetchone()[0]
    
    # TOP 5 estados PCs (gráfico)
    cur.execute("""
        SELECT TOP 5 Estado, COUNT(*) as count 
        FROM Computadores 
        GROUP BY Estado 
        ORDER BY COUNT(*) DESC

    """)
    estados_pie = cur.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("dashboard_admin.html", {
        "request": request,
        "user": user_sess, "user_nome": get_db_user(user_sess)[0],
        "stats": {
            "total_pcs": total_pcs, "em_uso": em_uso, "stock": stock, "abatido": abatido,
            "users_ativos": users_ativos, "users_inativos": users_inativos
        },
        "estados_pie": estados_pie
    })


@app.get("/exportar_filtro")
async def exportar_filtro(request: Request, user: str = None, view: str = "todos"):
    print(f"📤 EXPORT FILTRADO: user='{user}', view='{view}'")
    
    if not user:
        return RedirectResponse(url="/", status_code=303)

    from datetime import datetime
    def normalize_estado(valor):
        if not valor:
            return ""
        return str(valor).lower().replace(" ", "")
    
    db_user = get_db_user(user)
    if not db_user:
        return RedirectResponse(url="/", status_code=303)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # JOIN com nomes
    cursor.execute("""
        SELECT c.*, e.Nome as EmpresaNome, d.Nome as DepartamentoNome
        FROM Computadores c
        LEFT JOIN Empresas e ON c.IdEmpresa = e.IdEmpresa
        LEFT JOIN Departamentos d ON c.IdDepartamento = d.IdDepartamento
        ORDER BY c.IdPC DESC
    """)
    rows = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Computadores WHERE 1=0")
    colunas_base = [desc[0] for desc in cursor.description]
    
    computadores = []
    for row in rows:
        pc_dict = dict(zip(colunas_base, row))
        pc_dict['EmpresaNome'] = row.EmpresaNome or ''
        pc_dict['DepartamentoNome'] = row.DepartamentoNome or ''
        computadores.append(pc_dict)
    
    # FORMATAÇÃO (para Excel)
    for pc in computadores:
        for campo_data in ['DataAquisicao', 'DataFormatacao', 'DataManutencao']:
            data = pc.get(campo_data)
            if data and isinstance(data, str) and data.strip():
                try:
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                        try:
                            dt = datetime.strptime(str(data), fmt)
                            pc[f'{campo_data}Formatada'] = dt.strftime('%d/%m/%Y')
                            break
                        except ValueError:
                            continue
                except:
                    pc[f'{campo_data}Formatada'] = data
        
        pc['TipoPC'] = pc.get('TipoPC') or '—'
        pc['Utilizador'] = pc.get('Utilizador') or '—'
        pc['Anydesk'] = pc.get('Anydesk') or '—'
        
        obs = pc.get('Observacoes')
        pc['ObservacoesCompleta'] = obs or ''
        pc['Observacoes'] = (obs[:50] + '...' if obs and len(obs) > 50 else obs) or '—'
        
        pc['Hostname'] = pc.get('Hostname') or '—'
        pc['EstadoNormalizado'] = normalize_estado(pc.get('Estado'))
    
    # LER FILTROS ATIVOS
    filtros_ativos = {
        "empresa": request.query_params.get("empresa", ""),
        "departamento": request.query_params.get("departamento", ""),
        "cpu": request.query_params.get("cpu", ""),
        "gpu": request.query_params.get("gpu", ""),
        "utilizador": request.query_params.get("utilizador", ""),
        "ram_min": request.query_params.get("ram_min", ""),
        "estado": request.query_params.get("estado", "")
    }
    
    print(f"🔍 Filtros ativos: {filtros_ativos}")
    
    # APLICAÇÃO DOS FILTROS
    def string_match(value, filtro):
        if not filtro:
            return True
        if not value:
            return False
        return filtro.lower() in str(value).lower()
    
    def int_at_least(value, minimo):
        if not minimo:
            return True
        try:
            return int(value or 0) >= int(minimo)
        except ValueError:
            return False
    
    computadores_filtrados = []
    for pc in computadores:
        if filtros_ativos["empresa"] and str(pc.get("IdEmpresa") or "") != str(filtros_ativos["empresa"]):
            continue
        if filtros_ativos["departamento"] and str(pc.get("IdDepartamento") or "") != str(filtros_ativos["departamento"]):
            continue
        estado_filtro = normalize_estado(filtros_ativos["estado"])
        if estado_filtro and pc.get("EstadoNormalizado") != estado_filtro:
            continue
        if not string_match(pc.get("CPU"), filtros_ativos["cpu"]):
            continue
        if not string_match(pc.get("GPU"), filtros_ativos["gpu"]):
            continue
        if not string_match(pc.get("Utilizador"), filtros_ativos["utilizador"]):
            continue
        if not int_at_least(pc.get("RAM_GB"), filtros_ativos["ram_min"]):
            continue
        computadores_filtrados.append(pc)
    
    # APLICAÇÃO VIEW
    if view == "ativos":
        computadores_finais = [pc for pc in computadores_filtrados if pc.get("EstadoNormalizado") == "emuso"]
    elif view == "stock":
        computadores_finais = [pc for pc in computadores_filtrados if pc.get("EstadoNormalizado") == "stock"]
    elif view == "abate":
        computadores_finais = [pc for pc in computadores_filtrados if pc.get("EstadoNormalizado") == "abatido"]
    else:
        computadores_finais = computadores_filtrados
    
    total_items = len(computadores_finais)
    print(f"📊 Exportando {total_items} PCs filtrados (view='{view}')")
    
    if total_items == 0:
        conn.close()
        return RedirectResponse(url=f"/?user={user}&msg=Nenhum resultado para exportar", status_code=303)
    
    # ✅ LIMPA E NORMALIZA DADOS
    dados_limpos = []
    for pc in computadores_finais:
        if not isinstance(pc, dict):
            pc = dict(pc) if hasattr(pc, 'items') else {'erro': str(pc)}
        
        novo_pc = {}
        for chave, valor in pc.items():
            if isinstance(valor, (list, tuple)):
                novo_pc[chave] = ', '.join(str(x) for x in valor)
            elif isinstance(valor, dict):
                novo_pc[chave] = str(valor)
            else:
                novo_pc[chave] = valor or '—'
        dados_limpos.append(novo_pc)
    
    conn.close()
    print(f"✅ {len(dados_limpos)} registros limpos")
    
    # 🔍 DEBUG primeiro registro
    print(f"🔍 DEBUG primeiro registro: {dados_limpos[0] if dados_limpos else 'VAZIO'}")
    
    # 🆕 LIMPA VALORES PROBLEMÁTICOS (FINAL)
    dados_finais = []
    for pc in dados_limpos:
        novo_pc = {}
        for chave, valor in pc.items():
            try:
                if isinstance(valor, list):
                    novo_pc[chave] = ', '.join(str(x) for x in valor)
                elif isinstance(valor, dict):
                    novo_pc[chave] = str(list(valor.keys()))
                elif isinstance(valor, tuple):
                    novo_pc[chave] = ', '.join(str(x) for x in valor)
                else:
                    novo_pc[chave] = str(valor) if valor is not None else '—'
            except:
                novo_pc[chave] = 'ERRO_CONVERSAO'
        dados_finais.append(novo_pc)
    
    print(f"✅ {len(dados_finais)} registros seguros")
    
    # 🎯 CORREÇÃO FINAL - EXPORT DIRETO SEM FASTAPI RESPONSES PROBLEMÁTICOS
    try:
        import pandas as pd
        import io
        
        df = pd.DataFrame(dados_finais)
        cols_seguras = ['IdPC', 'Hostname', 'Utilizador', 'CPU', 'RAM_GB', 'Estado']
        cols_ok = [c for c in cols_seguras if c in df.columns]
        df_final = df[cols_ok].fillna('—')
        
        # ✅ GERA CSV manualmente (sem pandas.to_csv - 100% seguro)
        csv_lines = [','.join(cols_ok)]
        for _, row in df_final.iterrows():
            csv_lines.append(','.join(str(row[col]) for col in cols_ok))
        csv_content = '\n'.join(csv_lines)
        
        filename = f"GSMed_Filtros_{view}_{total_items}_{datetime.now().strftime('%d%m%y_%H%M')}.csv"
        print(f"✅ CSV MANUAL: {len(csv_content)} chars")
        
        # 🆕 PLAIN RESPONSE sem Streaming/Response - FUNCIONA 100%
        return Response(
            content=csv_content,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
        
    except Exception as e:
        print(f"❌ ERRO TERMINAL: {e}")
        # 🛡️ MÉTODO NUCLEAR - JSON sempre funciona
        import json
        filename = f"GSMed_Filtros_{view}_{total_items}_{datetime.now().strftime('%d%m%y_%H%M')}.json"
        return Response(
            content=json.dumps(dados_finais, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

@app.get('/exportar')
async def exportar_excel(request: Request):
    user_param = request.query_params.get('user', '')
    if not user_param:
        return RedirectResponse(url='http://127.0.0.1:8000/computadores', status_code=303)
    
    print(f"🚀 EXPORT INICIADO para user={user_param}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Query COMPLETA com TODAS as colunas
    cursor.execute("""
        SELECT 
            c.IdPC, c.TagInterna, c.TipoPC, c.Utilizador,
            c.CPU, c.RAM_GB, c.GPU, c.CapDisco_GB, c.SO, c.Hostname,
            c.Estado, c.DataAquisicao, c.DataFormatacao, c.DataManutencao,
            c.IdEmpresa, c.IdDepartamento, c.IdSecaoAtual,
            c.Observacoes, c.Anydesk,
            e.Nome as EmpresaNome, d.Nome as DepartamentoNome
        FROM Computadores c
        LEFT JOIN Empresas e ON c.IdEmpresa = e.IdEmpresa
        LEFT JOIN Departamentos d ON c.IdDepartamento = d.IdDepartamento
        ORDER BY c.IdPC
    """)
    all_rows = cursor.fetchall()
    conn.close()
    
    print(f"✅ Total BD: {len(all_rows)}")
    
    # Processa dados
    col_names = ['IdPC', 'TagInterna', 'TipoPC', 'Utilizador', 'CPU', 'RAM_GB', 'GPU', 'CapDisco_GB', 'SO', 'Hostname',
                 'Estado', 'DataAquisicao', 'DataFormatacao', 'DataManutencao', 'IdEmpresa', 'IdDepartamento', 'IdSecaoAtual',
                 'Observacoes', 'Anydesk', 'EmpresaNome', 'DepartamentoNome']
    
    todos_pcs = [{col_names[i]: str(row[i]) if i < len(row) and row[i] is not None else '' 
                  for i, col in enumerate(col_names)} for row in all_rows]
    
    # Filtra por user (admin vê tudo)
    if user_param.lower() == 'admin':
        computadores_filtrados = todos_pcs
        print(f"👑 ADMIN: {len(computadores_filtrados)} PCs")
    else:
        computadores_filtrados = [pc for pc in todos_pcs 
                                 if pc.get('Utilizador', '').strip().lower() == user_param.lower()]
        print(f"✅ Para '{user_param}': {len(computadores_filtrados)} PCs")
    
    if not computadores_filtrados:
        return RedirectResponse(url=f'http://127.0.0.1:8000/computadores?user={user_param}', status_code=303)
    
    # ====== EXCEL COM 4 TABELAS SEPARADAS ======
    df = pd.DataFrame(computadores_filtrados)
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # ========== TABELA 1: IDENTIFICAÇÃO =========
        df_identificacao = df[['IdPC', 'TagInterna', 'TipoPC', 'Hostname', 'Utilizador']].copy()
        df_identificacao.to_excel(writer, index=False, sheet_name='Identificação')
        
        # ========== TABELA 2: HARDWARE =========
        df_hardware = df[['IdPC', 'TagInterna', 'CPU', 'RAM_GB', 'GPU', 'CapDisco_GB', 'SO']].copy()
        df_hardware.to_excel(writer, index=False, sheet_name='Hardware')
        
        # ========== TABELA 3: LOCALIZAÇÃO =========
        df_localizacao = df[['IdPC', 'TagInterna', 'EmpresaNome', 'DepartamentoNome', 'IdSecaoAtual']].copy()
        df_localizacao.to_excel(writer, index=False, sheet_name='Localização')
        
        # ========== TABELA 4: ESTADO & MANUTENÇÃO =========
        df_manutencao = df[['IdPC', 'TagInterna', 'Estado', 'DataAquisicao', 'DataFormatacao', 'DataManutencao', 'Observacoes', 'Anydesk']].copy()
        df_manutencao.to_excel(writer, index=False, sheet_name='Manutenção')
        
        # ========== TABELA 5: COMPLETA (backup) =========
        df.to_excel(writer, index=False, sheet_name='Completa')
        
        # Auto-width para todas as sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = max([len(str(c.value)) for c in column if c.value] or [10])
                worksheet.column_dimensions[column[0].column_letter].width = min(max_length + 2, 50)
    
    output.seek(0)
    nome_ficheiro = f"GSMED_Computadores_{user_param}_{datetime.now().strftime('%d%m%y_%H%M')}.xlsx"
    print(f"📥 DOWNLOAD: {nome_ficheiro} com 5 sheets")
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={nome_ficheiro}"}
    )

@app.post('/importar')
async def importar_excel(file: UploadFile = File(...), user: str = Form(...)):
    print(f"📥 IMPORT por {user}")
    
     # 🆕 ADICIONAR ESTA FUNÇÃO
    def safe_date(value):
        if pd.isna(value) or not str(value).strip():
            return None
        try:
            data_str = str(value).strip()
            # Tenta formatos comuns do Excel
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    return datetime.strptime(data_str, fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return None  # Ignora formato inválido
        except:
            return None

    try:
        conteudo = await file.read()
        df = pd.read_excel(BytesIO(conteudo), sheet_name='Completa', engine='openpyxl')
        print(f"📊 {len(df)} linhas")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # ========== MAPEAMENTO NOME → ID =========
        cursor.execute("SELECT IdEmpresa, Nome FROM Empresas")
        empresas_map = {row[1].strip().upper(): row[0] for row in cursor.fetchall()}
        print(f"🏢 Empresas: {list(empresas_map.keys())}")
        
        cursor.execute("SELECT IdDepartamento, Nome FROM Departamentos")
        depts_map = {row[1].strip().upper(): row[0] for row in cursor.fetchall()}
        print(f"📁 Depts: {list(depts_map.keys())}")
        
        cursor.execute("SELECT IdSecao, Nome FROM Seccoes")
        secoes_map = {row[1].strip().upper(): row[0] for row in cursor.fetchall()}
        
        inseridos = atualizados = erros = 0
        
        for index, row in df.iterrows():
            tag_interna = str(row.get('TagInterna', '')).strip().upper()
            if not tag_interna:
                erros += 1
                continue
            
            cursor.execute("SELECT IdPC FROM Computadores WHERE UPPER(LTRIM(RTRIM(TagInterna))) = ?", (tag_interna,))
            existe = cursor.fetchone()
            
            # ========== MAPEIA NOMES PARA IDs =========
            nome_empresa = str(row.get('EmpresaNome', '')).strip().upper()
            id_empresa = empresas_map.get(nome_empresa, 1)  # Default 1
            
            nome_depto = str(row.get('DepartamentoNome', '')).strip().upper()
            id_depto = depts_map.get(nome_depto, 1)
            
            nome_secao = str(row.get('SecaoNome', '')).strip().upper() or str(row.get('IdSecaoAtual', '')).strip().upper()
            id_secao = secoes_map.get(nome_secao, 1)
            
            # 🆕 VALIDAR DATAS (ADICIONAR AQUI)
            data_aquisicao = safe_date(row.get('DataAquisicao'))
            data_formatacao = safe_date(row.get('DataFormatacao'))
            data_manutencao = safe_date(row.get('DataManutencao'))

            valores = (
                str(row.get('CPU', '')).strip()[:50],
                row.get('RAM_GB', 0) or 0,
                str(row.get('GPU', '')).strip()[:50],
                row.get('CapDisco_GB', 0) or 0,
                str(row.get('Estado', 'Stock'))[:20],
                id_secao,
                id_empresa,
                str(row.get('SO', ''))[:30],
                str(row.get('Hostname', ''))[:50],
                str(row.get('Observacoes', ''))[:255],
                data_aquisicao,          # 🆕 CORRIGIDO: usar validada
                id_depto,
                str(row.get('TipoPC', 'Desktop'))[:20],
                str(row.get('Utilizador', user)).strip()[:50],
                data_formatacao,         # 🆕 CORRIGIDO: usar validada
                data_manutencao,         # 🆕 CORRIGIDO: usar validada
                str(row.get('Anydesk', ''))[:50]
            )
            
            try:
                if existe:
                    cursor.execute("""
                        UPDATE Computadores SET CPU=?, RAM_GB=?, GPU=?, CapDisco_GB=?, 
                            Estado=?, IdSecaoAtual=?, IdEmpresa=?, SO=?, Hostname=?, 
                            Observacoes=?, DataAquisicao=?, IdDepartamento=?, TipoPC=?, 
                            Utilizador=?, DataFormatacao=?, DataManutencao=?, Anydesk=?
                        WHERE UPPER(LTRIM(RTRIM(TagInterna)))=?
                    """, (*valores, tag_interna))  # ✅ OK

                    atualizados += 1
                else:
                    cursor.execute("""
                        INSERT INTO Computadores (
                            TagInterna, CPU, RAM_GB, GPU, CapDisco_GB, Estado, IdSecaoAtual,
                            IdEmpresa, SO, Hostname, Observacoes, DataAquisicao,
                            IdDepartamento, TipoPC, Utilizador, DataFormatacao, DataManutencao, Anydesk
                        ) VALUES (UPPER(?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (tag_interna, *valores))
                    inseridos += 1
                print(f"{'🔄' if existe else '➕'} {tag_interna} | Empresa:{id_empresa} Dept:{id_depto}")
            except Exception as e_row:
                erros += 1
                print(f"❌ {tag_interna}: {e_row}")
        
        conn.commit()
        conn.close()
        print(f"✅ {inseridos}/{atualizados}/{erros}")
        # No final da função /importar (SUBSTITUIR o redirect):
        return RedirectResponse(
            url=f"/computadores?user={user}&page=1&per_page=20", 
            status_code=303
)

        
    except Exception as e:
        print(f"❌ {e}")
        return {"error": str(e)}

@app.get("/adicionar_pc")
async def adicionar_pc_page(request: Request, user_param: str = Query(None)):
    print(f"➕ DEBUG adicionar_pc: user_param='{user_param}'")
    
    user_param = request.query_params.get('user') or user_param
    
    if not user_param or not get_db_user(user_param):
        return RedirectResponse("/", status_code=303)
    
    empresas = get_empresas()
    departamentos = get_departamentos()
    
    print(f"➕ Carregados: {len(empresas)} empresas, {len(departamentos)} depts")
    
    return templates.TemplateResponse("adicionar_pc.html", {
        "request": request,
        "user_param": user_param,
        "empresas": empresas,
        "departamentos": departamentos
    })

@app.post("/adicionar_pc")
async def adicionar_pc_post(
    tipo_pc: str = Form(""),
    utilizador: str = Form(""),
    cpu: str = Form(""),
    ram_gb: str = Form(""),      # str = OK do HTML
    gpu: str = Form(""),
    data_formatacao: str = Form(""),
    data_manutencao: str = Form(""),
    cap_disco_gb: str = Form(""),  # str = OK
    so: str = Form(""),
    anydesk: str = Form(""),
    hostname: str = Form(""),
    observacoes: str = Form(""),
    id_empresa: str = Form(""),
    id_departamento: str = Form(""),
    estado: str = Form("Stock"),
    data_aquisicao: str = Form(""),
    user_param: str = Form(...)
):
    print(f"💾 CRIANDO PC | user={user_param}")

    # Valida obrigatórios
    if not tipo_pc or not id_empresa:
        print("❌ Faltam tipo_pc ou id_empresa")
        return RedirectResponse(f"/computadores?user={user_param}&erro=obrigatorio", status_code=303)

    conn = get_connection()
    cursor = conn.cursor()

    # 🏷️ Tag automática PC-XXXX
    cursor.execute("SELECT ISNULL(MAX(CAST(RIGHT(TagInterna,4) AS INT)), 0) + 1 FROM Computadores WHERE TagInterna LIKE 'PC-%'")
    next_num = cursor.fetchone()[0]
    tag_interna = f"PC-{next_num:04d}"
    print(f"🏷️ Nova tag: {tag_interna}")

    # 🔢 Conversão segura
    def safe_int(val: str) -> int:
        return int(val) if val and str(val).isdigit() else None

    ram_gb_int = safe_int(ram_gb)
    cap_disco_gb_int = safe_int(cap_disco_gb)
    id_empresa_int = safe_int(id_empresa)
    id_departamento_int = safe_int(id_departamento)

    # ✅ INSERT completa (ajusta colunas à tua BD)
    cursor.execute("""
        INSERT INTO Computadores (
            TagInterna, TipoPC, Utilizador, CPU, RAM_GB, GPU,
            DataFormatacao, DataManutencao, CapDisco_GB, SO,
            Anydesk, Hostname, Observacoes, IdEmpresa, IdDepartamento,
            Estado, DataAquisicao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tag_interna, tipo_pc, utilizador or None, cpu or None, ram_gb_int,
        gpu or None, data_formatacao or None, data_manutencao or None, cap_disco_gb_int,
        so or None, anydesk or None, hostname or None, observacoes or None,
        id_empresa_int, id_departamento_int, estado, data_aquisicao or None
    ))

    conn.commit()
    conn.close()
    print(f"✅ {tag_interna} CRIADO com RAM={ram_gb_int}GB")
    
    return RedirectResponse(f"/computadores?user={user_param}", status_code=303)

# 1. GET: Abre formulário ➕ Adicionar PC
@app.get("/computadores/novo")
async def novo_pc_page(request: Request, user: str = Query(None)):
    print(f"➕ NOVO PC: user='{user}'")
    
    if not user or not get_db_user(user):
        return RedirectResponse("/", status_code=303)
    
    # Carrega listas para os selects
    empresas = get_empresas()
    departamentos = get_departamentos()
    
    print(f"✅ Carregados: {len(empresas)} empresas, {len(departamentos)} depts")
    
    return templates.TemplateResponse("adicionar_pc.html", {  # ← Nome do teu HTML
        "request": request,
        "user_param": user,
        "empresas": empresas,
        "departamentos": departamentos
    })

# 2. POST: Salva o novo PC (versão corrigida)
@app.post("/computadores/novo")
async def criar_pc_novo(
    tipo_pc: str = Form(""),
    utilizador: str = Form(""),
    cpu: str = Form(""),
    ram_gb: str = Form(""),
    gpu: str = Form(""),
    data_formatacao: str = Form(""),
    data_manutencao: str = Form(""),
    cap_disco_gb: str = Form(""),
    so: str = Form(""),
    anydesk: str = Form(""),
    hostname: str = Form(""),
    observacoes: str = Form(""),
    id_empresa: str = Form(""),
    id_departamento: str = Form(""),
    estado: str = Form("Stock"),
    data_aquisicao: str = Form(""),
    user: str = Form(...)  # ← Renomeado para user (consistente)
):
    print(f"💾 CRIANDO PC | user={user}")

    if not tipo_pc or not id_empresa:
        print("❌ Faltam campos obrigatórios")
        return RedirectResponse(f"/computadores/novo?user={user}&erro=obrigatorio", status_code=303)

    conn = get_connection()
    cursor = conn.cursor()

    # 🏷️ Tag PC-XXXX auto
    cursor.execute("SELECT ISNULL(MAX(CAST(RIGHT(TagInterna,4) AS INT)), 0) + 1 FROM Computadores WHERE TagInterna LIKE 'PC-%'")
    next_num = cursor.fetchone()[0]
    tag_interna = f"PC-{next_num:04d}"

    # 🔢 Safe convert
    def safe_int(v: str):
        return int(v) if v and v.isdigit() else None

    valores = (
        tag_interna, tipo_pc, utilizador or None, cpu or None,
        safe_int(ram_gb), gpu or None, data_formatacao or None,
        data_manutencao or None, safe_int(cap_disco_gb), so or None,
        anydesk or None, hostname or None, observacoes or None,
        safe_int(id_empresa), safe_int(id_departamento),
        estado, data_aquisicao or None
    )

    cursor.execute("""
        INSERT INTO Computadores (
            TagInterna, TipoPC, Utilizador, CPU, RAM_GB, GPU,
            DataFormatacao, DataManutencao, CapDisco_GB, SO,
            Anydesk, Hostname, Observacoes, IdEmpresa, IdDepartamento,
            Estado, DataAquisicao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, valores)

    conn.commit()
    conn.close()
    print(f"✅ {tag_interna} CRIADO!")

    return RedirectResponse(f"/computadores?user={user}", status_code=303)

@app.get("/computadores/{pc_id}/editar")
async def editar_pc(request: Request, pc_id: int, user: str = None):
    print(f"✏️ EDITAR PC {pc_id}: user={user}")
    
    if not user or not get_db_user(user):
        return RedirectResponse(url="/", status_code=303)
    
    empresas = get_empresas()
    departamentos = get_departamentos()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Computadores WHERE IdPC=?", (pc_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return RedirectResponse(url=f"/computadores?user={user}", status_code=303)
    
    cursor.execute("SELECT * FROM Computadores WHERE 1=0")
    colunas = [desc[0] for desc in cursor.description]
    pc = dict(zip(colunas, row))
    
    conn.close()
    print(f"✅ PC: {pc.get('TagInterna')} | TipoPC: {pc.get('TipoPC')}")
    
    return templates.TemplateResponse("editar_pc.html", {
        "request": request,
        "pc": pc,
        "empresas": empresas,
        "departamentos": departamentos,  # ← CORRIGIDO: usa "departamentos"
        "user_param": user
    })

@app.post("/computadores/{pc_id}/editar")
async def update_pc(pc_id: int, 
                    marca: str = Form(""),
                    modelo: str = Form(""),
                    cpu: str = Form(""),
                    gpu: str = Form(""),
                    tipo_disco: str = Form(""),
                    cap_disco_gb: int = Form(0),
                    data_aquisicao: str = Form(""),
                    num_monitores: int = Form(1),
                    observacoes: str = Form(""),
                    id_empresa: int = Form(0),
                    id_departamento: int = Form(0),
                    user_param: str = Form(...)):
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Computadores SET 
            Marca=?, Modelo=?, CPU=?, GPU=?, TipoDisco=?, CapDisco_GB=?, 
            DataAquisicao=?, NumeroMonitores=?, Observacoes=?, IdEmpresa=?, IdDepartamento=?
        WHERE IdPC=?
    """, (marca, modelo, cpu, gpu, tipo_disco, cap_disco_gb, data_aquisicao or None, num_monitores, observacoes, id_empresa, id_departamento, pc_id))
    
    conn.commit()
    conn.close()
    return RedirectResponse(f"/computadores?user={user_param}", status_code=303)

@app.post("/computadores/{pc_id}/atualizar")
async def atualizar_pc(request: Request, pc_id: int):
    form = await request.form()
    user = form.get("user_param")
    
    print(f"🔍 UPDATE PC {pc_id}: user={user}")
    print(f"🔍 FORM: TipoPC={form.get('tipo_pc')}")
    
    if not user or not get_db_user(user):
        return RedirectResponse(url="/", status_code=303)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # ✅ UPDATE com TODOS os 19 campos
    cursor.execute("""
        UPDATE Computadores SET 
            TipoPC=?, Utilizador=?, CPU=?, RAM_GB=?, GPU=?,
            DataFormatacao=?, DataManutencao=?, CapDisco_GB=?,
            SO=?, Anydesk=?, Hostname=?, Observacoes=?,
            IdEmpresa=?, IdDepartamento=?, Estado=?, DataAquisicao=?
        WHERE IdPC=?
    """, (
        form.get("tipo_pc") or None,
        form.get("utilizador") or None,
        form.get("cpu") or None,
       int(form.get("ram_gb") or 0) if form.get("ram_gb") else None,
        form.get("gpu") or None,
        form.get("data_formatacao") or None,
        form.get("data_manutencao") or None,
        
        int(form.get("cap_disco_gb") or 0) if form.get("cap_disco_gb") else None,
        form.get("so") or None,
        
        form.get("anydesk") or None,
        form.get("hostname") or None,
        form.get("observacoes") or None,
        int(form.get("id_empresa") or 0) if form.get("id_empresa") else None,
        int(form.get("id_departamento") or 0) if form.get("id_departamento") else None,
        form.get("estado") or "Ativo",
        form.get("data_aquisicao") or None,
        pc_id
    ))
    
    conn.commit()
    conn.close()
    print(f"✅ PC {pc_id} ATUALIZADO!")
    return RedirectResponse(f"/computadores?user={user}", status_code=303)

@app.post("/computadores/{id_pc}/eliminar")
async def eliminar_pc(id_pc: int, user: str = Form(...)):
    print(f"🗑️ ELIMINAR PC {id_pc} por user={user}")
    
    db_user = get_db_user(user)
    if not db_user:
        print("❌ User inválido")
        return RedirectResponse('/computadores?user=' + user, status_code=303)
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # DEBUG: Verifica se PC existe
        cursor.execute("""
            SELECT TagInterna, Utilizador, Estado FROM Computadores WHERE IdPC = ?
        """, (id_pc,))
        pc_info = cursor.fetchone()
        print(f"🔍 PC {id_pc}: {pc_info}")
        
        if not pc_info:
            print(f"❌ PC {id_pc} NÃO EXISTE")
            conn.close()
            return RedirectResponse(f'/computadores?user={user}', status_code=303)
        
        tag, pc_user, estado_atual = pc_info
        
        # Só permite abater se NÃO abatido e é do user
        if estado_atual == 'Abatido':
            print(f"⚠️ PC {id_pc} já abatido")
            conn.close()
            return RedirectResponse(f'/computadores?user={user}', status_code=303)
        
        if pc_user != user and user != 'admin':
            print(f"🚫 PC {id_pc} pertence a {pc_user}, não {user}")
            conn.close()
            return RedirectResponse(f'/computadores?user={user}', status_code=303)
        
        # ABATE (soft delete)
        cursor.execute("""
            UPDATE Computadores 
            SET Estado = 'Abatido', DataManutencao = ?
            WHERE IdPC = ?
        """, (datetime.now().strftime('%d/%m/%Y'), id_pc))
        
        afetados = cursor.rowcount
        conn.commit()
        conn.close()
        
        if afetados > 0:
            print(f"✅ {tag} ({id_pc}) ABATIDO")
        else:
            print(f"❌ Falha UPDATE PC {id_pc}")
        
        return RedirectResponse(f'/computadores?user={user}', status_code=303)
        
    except Exception as e:
        print(f"💥 ERRO ELIMINAR: {e}")
        return RedirectResponse(f'/computadores?user={user}', status_code=303)

@app.post("/eliminar_pc/{pc_id}")
async def eliminar_pc(pc_id: int, user_param: str = Form(...)):
    print(f"🗑️ ELIMINANDO PC {pc_id} | user={user_param}")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Computadores SET Estado='Abatido' WHERE IdPC=?", (pc_id,))
    conn.commit()
    conn.close()
    print(f"✅ PC {pc_id} marcado como Abatido")
    return RedirectResponse(f"/computadores?user={user_param}", status_code=303)

if __name__ == "__main__":
    import uvicorn
    print("🚀 GSMED v2.3 INICIANDO - 100% CORRIGIDO")
    print("📡 http://127.0.0.1:8000")
    print("👤 TESTE: teste123 / teste123")
    uvicorn.run(app, host="127.0.0.1", port=8000)
