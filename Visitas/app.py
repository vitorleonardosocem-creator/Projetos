
# =========================================
# APP VISITANTES SOCEM
# Sistema de gestão de check-in de clientes e fornecedores
#
# Fluxo:
# 1. Registo visitante
# 2. Seleção de equipa (cookie)
# 3. Check-in → imprime etiqueta + envia email
# 4. Etiqueta existente → só email
#
# NOTAS:
# - Impressão é obrigatória para confirmar check-in
# - Emails são enviados para grupo + globais
# - Cookies guardam equipa selecionada
# =========================================

# ... .- -. - .. .- --. ---  .-.. --- ..- .-. . .. .-. ---

# =========================================
# GUIA PARA MANUTENÇÃO
#
# Alterar texto:
# → dicionário TEXTOS
#
# Alterar email:
# → função enviaremailcheckin()
#
# Alterar impressão:
# → função gerar_impressao_etiqueta()
#
# Problemas cliente vs fornecedor:
# → variável "tipo" (cookies)
# =========================================

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form, HTTPException, Query  # ← Query aqui!   
import pyodbc
import tempfile
import win32print
import win32api
import os
import time
import subprocess
import smtplib
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from pydantic import BaseModel
from typing import List
from qrcode import QRCode, constants
from PIL import Image as PILImage
from pathlib import Path
from fastapi.responses import JSONResponse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

import os

from typing import Optional  
from db import getconn
from services.visitantes import listar_visitantes_hoje, obter_email_responsavel, marcar_preconfirmado, gravar_checkin

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


#  TODOS OS TEXTOS DA APP
#
# ALTERAR:
# → Labels
# → Botões
# → Traduções PT / EN
 

TEXTOS = {
    "pt": {

    "selecionar_responsavel": "-- Selecionar Responsável --",
    "app_title": "Visitantes SOCEM",
    "name": "Nome",
    "company": "Empresa",
    "date": "Data",
    "action": "Ação",
    "label": "Etiqueta",
    "select_team": "Selecione a equipa antes de fazer Check-in ou clicar em Etiqueta Existente.",
    "select_team_alert": "🚫 SELECIONE EQUIPA PRIMEIRO!",
    "gdpr_title": "Proteção de Dados Pessoais",
    "gdpr_1": "Os dados pessoais recolhidos (telefone e email) serão utilizados exclusivamente para contacto no âmbito do programa de gestão de visitantes.",
    "gdpr_2": "O tratamento é realizado de acordo com o RGPD, garantindo confidencialidade e segurança.",
    "client_badge": " Crachá Cliente",
    "supplier_badge":"Crachá Fornecedor",
    "client_title": "Clientes",
    "supplier_title": "Fornecedores",
    "checkin": "Check-in",
    "existing_label": "Etiqueta Existente",
    "back": "← Voltar",
    "register_client": "Registar Cliente",
    "gdpr_3": "Os seus dados não serão partilhados com terceiros, exceto quando exigido por lei. Pode, a qualquer momento, solicitar acesso, retificação ou eliminação dos seus dados através de rececao@socem.pt.",
    "loading": "A carregar...",
    "register_supplier": "Registar Fornecedor",
    "email_exemplo": "email@exemplo.com",
    "return_crachas":" ← Voltar ",


    # Texto dos registo de fornecedores e clientes em português

     "client_registration": "Registo de Cliente",
    "supplier_registration": "Registo de Fornecedor",
    "fill_client": "Preencha os dados do cliente",
    "fill_supplier": "Preencha os dados do fornecedor",
    "phone": "Telefone",
    "email": "Email",
    "contact_person": "Responsável",
    "suggestions": "Sugestões após 2 letras",
    "register_client_btn": "Registar Cliente",
    "register_supplier_btn": "Registar Fornecedor",
},
"en": {
    "selecionar_responsavel": "-- Select Contact Person --",
    "app_title": "SOCEM Visitors",
    "name": "Name",
    "company": "Company",
    "date": "Date",
    "action": "Action",
    "label": "Label",
    "select_team": "Select the team before doing Check-in or clicking Existing Label.",
    "select_team_alert": "🚫 SELECT TEAM FIRST!",
    "gdpr_title": "Personal Data Protection",
    "gdpr_1": "The personal data collected (telephone and email) will be used exclusively for contact purposes within the visitor management program.",
    "gdpr_2": "Processing is carried out in accordance with GDPR, ensuring confidentiality and security.",
    "client_badge": "Client Badge",
    "supplier_badge":"Supplier Badge",
    "client_title": "Clients",
    "supplier_title": "Suppliers",
    "checkin": "Check-in",
    "existing_label": "Existing Label",
    "back": "← Return",
    "register_client": "Register Client",
    "gdpr_3": "Your data will not be shared with third parties, except where required by law. You may, at any time, request access to, rectification or deletion of your data by contacting rececao@socem.pt.",
    "loading": "Loading...",
    "register_supplier": "Register Supplier",
    "email_exemplo": "email@example.com",
    "return_crachas":" ← Return ",

    # Texto dos registo de fornecedores e clientes em inglês

    "client_registration": "Client Registration",
    "supplier_registration": "Supplier Registration",
    "fill_client": "Fill in your client details",
    "fill_supplier": "Fill in your supplier details",
    "phone": "Phone",
    "email": "Email",
    "contact_person": "Contact Person",
    "suggestions": "Suggestions after 2 letters",
    "register_client_btn": "Register Client",
    "register_supplier_btn": "Register Supplier",
}
}


def obter_id_grupo_por_nome(nome_grupo: str):
    with getconn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT IdGrupo FROM ResponsavelGrupo WHERE NomeGrupo = ?", (nome_grupo,))
        row = cur.fetchone()
        return row[0] if row else None

def get_textos(request: Request):
    lang = request.cookies.get("lang", "pt")
    return TEXTOS.get(lang, TEXTOS["pt"])


from fastapi import Form
from fastapi.responses import RedirectResponse

@app.post("/set-language")
async def set_language(lang: str = Form(...)):
    response = RedirectResponse(url="/menu", status_code=303)
    response.set_cookie("lang", lang, max_age=3600)
    return response


# GUARDA COOKIES
#  grupoid (equipa)
#  tipo (clientes ou fornecedores)
#
#  PROBLEMAS:
#  Email errado
#  Check-in bloqueado
#
#  DEBUG:
#  print(request.cookies)


@app.post("/selecionar-grupo")
async def selecionar_grupo(
    grupoid: str = Form(..., alias="grupoid"), 
    tipo: str = Form(...),
    grupoid_query: Optional[str] = Query(None)  # ← FALLBACK
):
    grupoid_final = grupoid or grupoid_query
    if not grupoid:
         raise HTTPException(400, "Grupo inválido!")
    
    resp = RedirectResponse(url=f"/{tipo}", status_code=303)
    resp.set_cookie("grupoid", str(grupoid_final), max_age=3600, httponly=True, secure=False, samesite='lax')
    resp.set_cookie("tipo", tipo, max_age=3600, httponly=True, secure=False, samesite='lax')
    print(f"✅ COOKIE SET: grupoid={grupoid_final}, tipo={tipo}")  # LOG
    return resp



#   PÁGINA INICIAL
# → Seleção de idioma (cookie: "lang")
# → Redireciona depois para /menu

@app.get("/", response_class=HTMLResponse)
async def menu_entrada(request: Request):
    return templates.TemplateResponse("linguagem.html", {
        "request": request,
        "textos": get_textos(request)
    })


#  MENU PRINCIPAL
#  Escolha entre Clientes ou Fornecedores
#  Ponto de entrada para o sistema

@app.get("/menu", response_class=HTMLResponse)
async def menu(request: Request):
    return templates.TemplateResponse("menu_entrada.html", {
        "request": request,
        "textos": get_textos(request)
    })

from fastapi import Form
from fastapi.responses import RedirectResponse



#  LISTAGEM DE CLIENTES DO DIA
#  Vai buscar dados à BD (tabela Visitantes)
#  Agrupa por responsável (equipas)
#  Mostra botões: Check-in e Etiqueta Existente
#
#  ALTERAÇÕES COMUNS:
#  Layout: templates/clientes.html
#  Query: função listar_visitantes_hoje()

@app.get("/clientes", response_class=HTMLResponse)
async def pagina_clientes(request: Request):

    #vai buscar os visitantes do dia à base de dados 
    visitantes = listar_visitantes_hoje('clientes')


    visitantes_normalizados = []

    for v in visitantes:
        if isinstance(v, dict):
            visitantes_normalizados.append(v)
        else:
            visitantes_normalizados.append({
            "Id": v[0],
            "Nome": v[1],
            "Empresa": v[2],
            "Data": v[3],
            "Responsavel": v[4] if len(v) > 4 else "",
            "PreConfirmado": v[5] if len(v) > 5 else "NAO"
        })

    visitantes = visitantes_normalizados



    print("\n📅 CLIENTES DE HOJE:")
    for v in visitantes:
        print(f"👉 ID: {v.get('Id')} | Nome: {v.get('Nome')} | Empresa: {v.get('Empresa')} | Data: {v.get('Data')}")

    grupos_unicos = {}

    # Percorrer os visitantes
    for v in visitantes:
        print("VISITANTE:", v)

        if isinstance(v, dict):
            responsavel = v.get("Responsavel") or "Sem coordenador"
        else:
            responsavel = v[4] if len(v) > 4 else None

        print("RESPONSAVEL:", responsavel)

        if responsavel:
            grupos_unicos[responsavel] = {
                "id": responsavel,
                "nome": responsavel
            }

    grupos = list(grupos_unicos.values())

    # Envio os dados para a pagina html
    return templates.TemplateResponse("clientes.html", {
        "request": request,
        "titulo": "Client",
        "visitantes": visitantes,
        "grupos": grupos,
        "textos": get_textos(request)
    })

@app.get("/registo_clientes")
async def registoclientes(request: Request):
    return templates.TemplateResponse("registo_clientes.html", {
        "request": request,
        "textos": get_textos(request)
    })

@app.get("/registo_fornecedores")
async def registofornecedores(request: Request):
    return templates.TemplateResponse("registo_fornecedores.html", {
        "request": request,
        "textos": get_textos(request)
    })



#  LISTAGEM DE FORNECEDORES DO DIA
#  Igual a clientes mas usa tabela Visitantes_Fornecedores
#
#  IMPORTANTE:
#  Qualquer bug de fornecedor vs cliente começa aqui

@app.get("/fornecedores", response_class=HTMLResponse)
async def pagina_fornecedores(request: Request): 
    visitantes = listar_visitantes_hoje('fornecedores')

    print("\n📅 FORNECEDORES DE HOJE:")
    for v in visitantes:

        if isinstance(v, dict):

            print(f"👉 ID: {v.get('Id')} | Nome: {v.get('Nome')} | Empresa: {v.get('Empresa')} | Data: {v.get('Data')}")
        else:

            print(f"👉 {v}")

    grupos_unicos = {}

    for v in visitantes:
        if isinstance(v, dict):
            responsavel = v.get("Responsavel") or "Sem coordenador"
        else:
            responsavel = v[3] if len(v) > 3 else None

        if responsavel:
            grupos_unicos[responsavel] = {
                "id": responsavel,
                "nome": responsavel,
                "textos": get_textos(request)
            }

    grupos = list(grupos_unicos.values())

    return templates.TemplateResponse("fornecedores.html", {
        "request": request,
        "titulo": "Supplier",
        "visitantes": visitantes,
        "grupos": grupos,
        "textos": get_textos(request)

    }) 

   
import tempfile
import win32print
import win32api
import os
import time
import subprocess  # Para fallback Ghostscript se quiseres mais silencioso depois



#  CHECK-IN COMPLETO 
#
# FLUXO:
# 1. Lê cookies (grupo + tipo)
# 2. Valida equipa selecionada
# 3. Vai buscar dados do visitante
# 4. GERA + IMPRIME ETIQUETA (OBRIGATÓRIO)
# 5. Atualiza BD (PreConfirmado='SIM')
# 6. Regista em tabela CheckIns
# 7. ENVIA EMAIL
# 8. Redireciona para lista


@app.post("/checkin/{visitanteid}")
async def checkin_visitante(
    visitanteid: int,
    request: Request,
    grupoid_query: Optional[int] = Query(None)
):
    try:           
        # 🍪 COOKIES
        cookies = dict(request.cookies)
        print(f"🍪 COOKIES: {cookies}")

        grupoid_nome = cookies.get("grupoid")  # ex: "Emilio Vigia"
        tipo = cookies.get("tipo")

        if tipo not in ["clientes", "fornecedores"]:
            tipo = "fornecedores"

        print(f"DEBUG → visitante={visitanteid} | grupo={grupoid_nome} | tipo={tipo}")

        # 🚫 VALIDAR GRUPO
        if not grupoid_nome or grupoid_nome == "undefined":
            raise HTTPException(status_code=400, detail="Selecione equipa!")

        # 🔎 BUSCAR ID DO GRUPO pelo NomeGrupo na tabela ResponsavelGrupo
        grupoid = None
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT IdGrupo FROM ResponsavelGrupo WHERE NomeGrupo = ?", (grupoid_nome,))
            row = cur.fetchone()
            if row:
                grupoid = row[0]

        print(f"DEBUG → grupoid resolvido={grupoid}")

        # 🔎 BUSCAR DADOS DO VISITANTE
        with getconn() as conn:
            cur = conn.cursor()

            cur.execute("""
                SELECT Nome, Empresa, ISNULL(Email,''), ISNULL(Telefone,''), 
                       ISNULL(Responsavel,''), ISNULL(Observacao,'')
                FROM Visitantes
                WHERE Id=? AND CAST(Data AS DATE)=CAST(GETDATE() AS DATE)
            """, (visitanteid,))
            dados = cur.fetchone()

            if not dados:
                cur.execute("""
                    SELECT Nome, Empresa, ISNULL(Email,''), ISNULL(Telefone,''), 
                           ISNULL(Responsavel,''), ISNULL(Observacao,'')
                    FROM Visitantes_Fornecedores
                    WHERE Id=? AND CAST(Data AS DATE)=CAST(GETDATE() AS DATE)
                """, (visitanteid,))
                dados = cur.fetchone()

        if not dados:
            raise HTTPException(status_code=404, detail="Visitante não encontrado")

        nome, empresa, email, telefone, responsavel, observacao = dados

        # 🖨️ IMPRESSÃO (OBRIGATÓRIA)
        try:
            gerar_impressao_etiqueta(
                nome=nome,
                empresa=empresa,
                email=email,
                telefone=telefone,
                responsavel=responsavel,
                observacao=observacao
            )
            print("✅ Impressão OK")

        except Exception as e:
            print(f"❌ Impressão falhou: {e}")

            with getconn() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE Visitantes SET PreConfirmado='NAO' WHERE Id=?", (visitanteid,))
                cur.execute("UPDATE Visitantes_Fornecedores SET PreConfirmado='NAO' WHERE Id=?", (visitanteid,))
                conn.commit()

            raise HTTPException(status_code=500, detail="Erro na impressão")

        # ✅ CHECK-IN (SÓ SE IMPRIMIR)
        with getconn() as conn:
            cur = conn.cursor()

            cur.execute("""
                UPDATE Visitantes 
                SET PreConfirmado='SIM', DataCheckIn=GETDATE()
                WHERE Id=? AND CAST(Data AS DATE)=CAST(GETDATE() AS DATE)
            """, (visitanteid,))

            cur.execute("""
                UPDATE Visitantes_Fornecedores 
                SET PreConfirmado='SIM', DataCheckIn=GETDATE()
                WHERE Id=? AND CAST(Data AS DATE)=CAST(GETDATE() AS DATE)
            """, (visitanteid,))

            cur.execute("""
                INSERT INTO CheckIns (Nome, Email, DataCheckIn, Empresa, Responsavel)
                VALUES (?, ?, GETDATE(), ?, ?)
            """, (nome, email, empresa, responsavel))

            conn.commit()

        # 📧 EMAIL
        config = obter_config_smtp()
        print("🔥 CONFIG SMTP:", config)
        emails = obteremailsgrupo(grupoid)
        enviaremailcheckin(config, emails, nome, empresa, grupoid_nome, tipo)

        # 🔁 REDIRECT
        resp = RedirectResponse(url=f"/{tipo}", status_code=303)
        resp.set_cookie("grupoid", grupoid_nome, httponly=True, max_age=3600, samesite="lax")
        resp.set_cookie("tipo", tipo, httponly=True, max_age=3600, samesite="lax")

        print(f"🎉 CHECK-IN OK → ID={visitanteid}")
        return resp

    except HTTPException:
        raise

    except Exception as e:
        print(f"💥 ERRO: {e}")
        print(traceback.format_exc())

        raise HTTPException(status_code=500, detail=str(e))

  
# CHECK-IN SEM IMPRESSÃO
#
# USO:
#  Visitante já tem crachá
#
# FLUXO:
# NÃO imprime
# ENVIA EMAIL
# Marca como PreConfirmado='SIM'
#
#  IMPORTANTE:
#  Se email sair errado → verificar "tipo"


@app.post("/label-existente/{visitante_id}")
async def label_existente(visitante_id: int, request: Request):

        cookies = dict(request.cookies)

        grupoid_nome = cookies.get("grupoid")
        tipo = cookies.get("tipo", "fornecedores")

        if not grupoid_nome:
            raise HTTPException(status_code=400, detail="Selecione equipa primeiro!")

        # 🔎 ID do grupo
        grupoid = obter_id_grupo_por_nome(grupoid_nome)

        if not grupoid:
            raise HTTPException(status_code=400, detail="Grupo inválido!")

        # 🔎 Buscar dados
        with getconn() as conn:
            cur = conn.cursor()

            cur.execute("""
            SELECT Nome, Empresa, ISNULL(Email,''), ISNULL(Responsavel,'')
            FROM Visitantes
            WHERE Id=? AND CAST(Data AS DATE)=CAST(GETDATE() AS DATE)
        """, (visitante_id,))
            dados = cur.fetchone()

        if not dados:
                cur.execute("""
                SELECT Nome, Empresa, ISNULL(Email,''), ISNULL(Responsavel,'')
                FROM Visitantes_Fornecedores
                WHERE Id=? AND CAST(Data AS DATE)=CAST(GETDATE() AS DATE)
            """, (visitante_id,))
                dados = cur.fetchone()

        if not dados:
            raise HTTPException(status_code=404, detail="Visitante não encontrado")

        nome, empresa, email, responsavel = dados

        # 📧 EMAIL
        config = obter_config_smtp()
        emails = obteremailsgrupo(grupoid)

        print(f"📧 Tentativa de envio - {nome} | {empresa}")

        if not config:
            print("❌ ERRO: Config SMTP não encontrada!")

        elif not emails:
            print("❌ ERRO: Sem emails!")

        else:
            try:
                enviaremailcheckin(config, emails, nome, empresa, grupoid, tipo)
                print("✅ Email enviado!")
            except Exception as e:
                print(f"❌ ERRO email: {e}")

        # ✅ MARCAR COMO CHECK-IN
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE Visitantes SET PreConfirmado='SIM' WHERE Id=?", (visitante_id,))
            cur.execute("UPDATE Visitantes_Fornecedores SET PreConfirmado='SIM' WHERE Id=?", (visitante_id,))
            conn.commit()

        print("✅ Marcado como confirmado")

        return JSONResponse({
            "success": True,
            "emails": emails
        })



@app.get("/api/nomes/clientes")
async def apinomesclientes():
    try:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT Nome FROM Clientes WHERE Nome IS NOT NULL AND Nome <> '' ORDER BY Nome")
            nomes = [row[0] for row in cur.fetchall() if row[0]]
            print(f"✅ Clientes PURA: {len(nomes)}")
            return nomes
    except Exception as e:
        print("Erro nomes clientes:", e)
        return []

@app.post("/api/registar_cliente")
async def registarcliente(nome: str = Form(...), empresa: str = Form(...), telefone: str = Form(...), 
                         email: str = Form(""), responsavel: str = Form("")):
    try:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Visitantes 
                (IdCliente, Nome, Empresa, Telefone, Email, Responsavel, Data, PreConfirmado, Almoco, Observacao)
                VALUES (0, ?, ?, ?, ?, ?, CAST(GETDATE() AS DATE), 'NAO', 'NAO', '')
            """, (nome, empresa, telefone, email, responsavel))
            conn.commit()
        print(f"✅ Cliente: {nome}")
        return {"success": True, "message": f"{nome} registado!"}
    except Exception as e:
        print("🚨 ERRO:", str(e))
        raise HTTPException(400, detail=str(e))



@app.get("/api/responsaveis")
async def listar_responsaveis():
    try:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT NomeGrupo 
                FROM ResponsavelGrupo
                ORDER BY NomeGrupo
            """)
            return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print("Erro responsaveis:", e)
        return []

    

def obter_config_smtp():
    

    sql = "SELECT smtp_server, smtp_port, email_origem, email_password FROM email_config"
    with getconn() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        if row:
            return {
                "server": row[0].strip(),
                "port": int(row[1]),
                "email": row[2].strip(),
                "password": row[3].strip()
            }
    return None



def obter_grupos_dinamicos():
    with getconn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT Responsavel
            FROM Visitantes
            WHERE CAST(Data AS DATE) = CAST(GETDATE() AS DATE)
            AND Responsavel IS NOT NULL
        """)

        grupos = []
        for row in cur.fetchall():
            grupos.append({
                "id": row[0],   # temporário
                "nome": row[0]
            })

        return grupos


def obteremailsgrupo(grupoid: int, grupoid_nome: str = None) -> list:
    emails = []

    # 1. Emails do grupo pelo IdGrupo (tabela ResponsavelGrupoEmail)
    if grupoid:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT EmailResponsavel 
                FROM ResponsavelGrupoEmail 
                WHERE IdGrupo = ? AND EmailResponsavel LIKE '%@%.%'
            """, (grupoid,))
            for row in cur.fetchall():
                if row[0]: emails.append(row[0].strip())

    # 2. Fallback: tentar pelo nome do grupo se não encontrou emails
    if not emails and grupoid_nome:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT rge.EmailResponsavel
                FROM ResponsavelGrupoEmail rge
                JOIN ResponsavelGrupo rg ON rg.IdGrupo = rge.IdGrupo
                WHERE rg.NomeGrupo = ? AND rge.EmailResponsavel LIKE '%@%.%'
            """, (grupoid_nome,))
            for row in cur.fetchall():
                if row[0]: emails.append(row[0].strip())

    # 3. Emails globais ativos
    try:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT email 
                FROM Visitantes.dbo.email_destinatarios 
                WHERE ativo = 1 AND email LIKE '%@%.%'
            """)
            for row in cur.fetchall():
                if row[0]: emails.append(row[0].strip())
    except Exception as e:
        print(f"⚠️ email_destinatarios: {e}")

    emails = list(set(emails))
    print(f"📧 FINAL grupo={grupoid_nome}: {emails}")

    return emails  

def enviar_email_cracha(config, emails_destino, nome, empresa):
    if not config or not emails_destino:
        return
    
    corpo = f"O Cliente **{nome}** da empresa **{empresa}** que já tem em sua posse o Crachá, acabou de chegar."
    
    try:
        server = smtplib.SMTP(config['server'], config['port'])
        server.starttls()
        server.login(config['email'], config['password'])
        
        for email_dest in emails_destino:
            msg = f"Subject: Aviso Cliente com Crachá chegou\n\n{corpo}"
            server.sendmail(config['email'], email_dest, msg)
        
        server.quit()
    except Exception:
        pass  # Silencioso como VB


class RegisterData(BaseModel):
    nome: str
    empresa: str
    telefone: str  # Completo com prefixo
    email: str
    responsavel: str
    tipo: str  # 'clientes' ou 'fornecedores'

@app.post("/api/register")
async def api_register(data: RegisterData):
    """Insere Visitantes OU VisitantesFornecedores"""
    try:
        table = "Visitantes" if data.tipo == "clientes" else "VisitantesFornecedores"
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute(f"""
                INSERT INTO {table} (Nome, Empresa, Telefone, Email, Responsavel, Data, PreConfirmado)
                VALUES (?, ?, ?, ?, ?, CAST(GETDATE() AS DATE), 'NAO')
            """, data.nome, data.empresa, data.telefone, data.email, data.responsavel)
            conn.commit()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/registar_fornecedores")  # ← Nome exato do HTML!
async def registar_fornecedores(  # ← Mudou de register → registar
    nome: str = Form(...),
    empresa: str = Form(...),
    telefone: str = Form(...),
    email: str = Form(""),
    responsavel: str = Form("")
):
    try:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Visitantes_Fornecedores
                (IdFornecedor, Nome, Empresa, Telefone, Email, Responsavel, Data, PreConfirmado, Almoco, Observacao)
                VALUES (0, ?, ?, ?, ?, ?, CAST(GETDATE() AS DATE), 'NAO', 'NAO', '')
            """, (nome, empresa, telefone, email, responsavel))
            conn.commit()
        print(f"✅ Fornecedor inserido: {nome}")
        return {"success": True, "message": f"{nome} registado hoje!"}
    except Exception as e:
        print("🚨 ERRO INSERT:", str(e))
        raise HTTPException(400, detail=str(e))


@app.get("/api/carregar_cliente")
async def carregarcliente(nome: str):
    try:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT TOP 1 Empresa, Telefone, Email FROM Clientes WHERE Nome = ?", (nome,))
            row = cur.fetchone()
            if row:
                empresa, telefone, email = row
                telefone_str = str(telefone) if telefone is not None else ""
                if telefone_str and not telefone_str.startswith(''):
                    telefone_str = '' + telefone_str.lstrip('0')
                return {"empresa": empresa or "", "telefone": telefone_str, "email": email or ""}
            return {}
    except Exception as e:
        print("Erro carregar cliente:", e)
        return {}

@app.get("/api/nomes/fornecedores")
async def apinomesfornecedores():
    try:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT Nome FROM Fornecedores  -- ← SÓ Fornecedores!
                WHERE Nome IS NOT NULL AND Nome <> '' 
                ORDER BY Nome
            """)
            nomes = [row[0] for row in cur.fetchall() if row[0]]
            print(f"✅ Fornecedores PURA: {len(nomes)}")  # ← Mudança no print
            return nomes
    except Exception as e:
        print("Erro nomes fornecedores:", e)
        return []

@app.get("/api/carregar_fornecedor")
async def carregarfornecedor(nome: str):
    try:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT TOP 1 Empresa, Telefone, Email
                FROM Fornecedores 
                WHERE Nome = ?
            """, (nome,))
            row = cur.fetchone()
            if row:
                empresa, telefone, email = row

                # garante string mesmo que venha int ou None
                telefone_str = str(telefone) if telefone is not None else ""

                if telefone_str and not telefone_str.startswith(''):
                    telefone_str = '' + telefone_str.lstrip('0')

                return {
                    "empresa": empresa or "",
                    "telefone": telefone_str,
                    "email": email or ""
                }
            return {}
    except Exception as e:
        print("Erro carregar fornecedor:", e)
        return {}


@app.get("/api/nomes/{tipo}")
async def api_nomes(tipo: str) -> List[str]:
    """Autocomplete de Clientes/Fornecedores tabelas"""
    table = "Clientes" if tipo == "clientes" else "Fornecedores"
    try:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT DISTINCT Nome FROM {table} WHERE Nome IS NOT NULL AND Nome <> '' ORDER BY Nome")
            nomes = [row[0] for row in cur.fetchall() if row[0]]
        print(f"{tipo} nomes: {len(nomes)}")  # Debug
        return nomes
    except Exception as e:
        print(f"Erro {tipo}: {e}")
        return []

@app.get("/api/carregar/{tipo}")
async def carregar_dados(tipo: str, nome: str):
    table = "Visitantes" if tipo == "clientes" else "VisitantesFornecedores"
    try:
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT TOP 1 Empresa, Telefone, Email 
                FROM {table} WHERE Nome = ? ORDER BY Data DESC
            """, (nome,))
            row = cur.fetchone()
            if row:
                return {"empresa": row[0] or "", "telefone": row[1] or "", "email": row[2] or ""}
        return {}
    except Exception as e:
        print(f"Erro carregar {tipo}: {e}")
        return {}

class RegisterData(BaseModel):
    nome: str
    empresa: str  
    telefone: str
    email: str = ""  # ← str vazio default (não Optional)
    responsavel: str = ""  # ← str vazio default

import os
from pathlib import Path

import os
from pathlib import Path

import os
from pathlib import Path

def gerar_pdf_etiqueta(visitante_id: int, nome: str, empresa: str,
                       email: str, telefone: str, responsavel: str = ""):
    """
    ETIQUETA FINAL - LOGO + QR SEM TEMP FILES (Windows OK)
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from io import BytesIO
    from PIL import Image as PILImage
    from qrcode import QRCode
    from qrcode.constants import ERROR_CORRECT_M
    from pathlib import Path

    buffer = BytesIO()
    width, height = 255, 142
    c = canvas.Canvas(buffer, pagesize=(width, height))

    print(f"📄 Etiqueta: {nome}")

    # 1️⃣ LOGO (sem temp file)
    current_dir = Path(__file__).parent
    logo_path = current_dir / "static" / "imagens" / "socem.jpg"
    if logo_path.exists():
        try:
            logo_img = PILImage.open(str(logo_path)).rotate(90, expand=True).resize((25, 130))
            logo_buffer = BytesIO()
            logo_img.save(logo_buffer, 'JPEG')
            logo_buffer.seek(0)
            c.drawImage(ImageReader(logo_buffer), 2, 5, 25, 130, mask='auto')
            print("✅ Logo desenhada!")
        except Exception as e:
            print(f"⚠️ Logo erro: {e}")

    # 2️⃣ DADOS + VISTO
    c.setFont("Helvetica-Bold", 13)
    c.drawString(35, 130, nome)
    c.setFont("Helvetica", 10)
    c.drawString(35, 108, empresa)
    if responsavel:
        c.setFont("Helvetica", 9)
        c.drawString(35, 70, f" {responsavel}")
    c.setFont("Helvetica-Bold", 20)
    c.drawString(235, 125, "✓")

    # 3️⃣ QR CODE (sem temp file)
    try:
        qr_data = f"TEL:{telefone}\nEMAIL:{email}"
        print(f"🔲 QR: {qr_data}")
        qr = QRCode(version=1, error_correction=ERROR_CORRECT_M, box_size=3, border=1)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((85, 85))
        
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, 'PNG')
        qr_buffer.seek(0)
        c.drawImage(ImageReader(qr_buffer), 160, 10, 85, 85, mask='auto')
        print("✅ QR desenhado!")
    except Exception as e:
        print(f"⚠️ QR erro: {e}")
        c.setFillColorRGB(0,0,0)
        c.rect(202, 10, 48, 48, fill=1)

    c.save()
    buffer.seek(0)
    print("✅ PDF FINAL!")
    return buffer.getvalue()


#  IMPRESSÃO DIRETA PARA IMPRESSORA
#
# DEFINE:
#  Nome
#  Empresa
#  Responsável
#  QR Code
#
#  ALTERAR:
#  Layout da etiqueta → posições (base_x, base_y)
#  Impressora → variável PRINTER_NAME


def gerar_impressao_etiqueta(
    nome: str,
    empresa: str,
    email: str,
    telefone: str,
    responsavel: str = "",
    observacao: str = ""   # ← NOVO CAMPO
):
    """
    IMPRESSÃO DIRETA ETIQUETA
    ED Rececao Brother
    SEM PDF | SEM TEMP FILE
    Windows only (win32 GDI)
    """
    import win32print
    import win32ui
    from PIL import Image, ImageWin
    from qrcode import QRCode
    from qrcode.constants import ERROR_CORRECT_M
    from pathlib import Path

    # 🖨️ FORÇAR IMPRESSORA
    
    PRINTER_NAME = "ED Rececao Brother"

    printers = [p[2] for p in win32print.EnumPrinters(2)]
    if PRINTER_NAME not in printers:
        raise Exception(f"Impressora '{PRINTER_NAME}' não encontrada")

    print(f"🖨️ Impressora usada: {PRINTER_NAME}")

    # Criar DC da impressora
    hprinter = win32print.OpenPrinter(PRINTER_NAME)
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(PRINTER_NAME)

    try:
        hdc.StartDoc("Etiqueta Visitante")
        hdc.StartPage()

        # 📐 POSIÇÃO BASE (ajusta se necessário)
        base_x = 100
        base_y = 90

        # 🖼️ LOGO
        logo_path = Path(__file__).parent / "static" / "imagens" / "socem.jpg"
        if logo_path.exists():
            logo = (
                Image.open(logo_path)
                .rotate(90, expand=True)
                .resize((80, 350))
            )
            dib_logo = ImageWin.Dib(logo)
            dib_logo.draw(
                hdc.GetHandleOutput(),
                (base_x, base_y, base_x + 80, base_y + 350)
            )

        # 📝 NOME
        hdc.SetTextColor(0x000000)
        hdc.SelectObject(
            win32ui.CreateFont({
                "name": "Arial",
                "height": 60,
                "weight": 700
            })
        )
        hdc.TextOut(base_x + 100, base_y, nome)

        # 🏢 EMPRESA
        hdc.SelectObject(
            win32ui.CreateFont({
                "name": "Arial",
                "height": 60,
                "weight": 400
            })
        )
        hdc.TextOut(base_x + 100, base_y + 60, empresa)

        # 👤 RESPONSÁVEL / GRUPO
        if responsavel:
            hdc.SelectObject(
                win32ui.CreateFont({
                    "name": "Arial",
                    "height": 60
                })
            )
            hdc.TextOut(base_x + 100, base_y + 200, responsavel)

        # 🗒️ OBSERVAÇÃO (abaixo do responsável)
        if observacao:
            hdc.SelectObject(
                win32ui.CreateFont({
                    "name": "Arial",
                    "height": 50  # ligeiramente mais pequena
                })
            )
            # 60 px abaixo do responsável
            hdc.TextOut(base_x + 100, base_y + 290, observacao)

        # ✓ CHECK
        hdc.SelectObject(
            win32ui.CreateFont({
                "name": "Arial",
                "height": 80,
                "weight": 700
            })
        )
        hdc.TextOut(base_x + 840, base_y - 30, "✓")

        # 🔲 QR CODE
        qr = QRCode(
            version=1,
            error_correction=ERROR_CORRECT_M,
            box_size=6,
            border=1
        )
        qr.add_data(f"TEL:{telefone}\nEMAIL:{email}")
        qr.make(fit=True)

        qr_img = (
            qr.make_image(fill_color="black", back_color="white")
            .resize((260, 260))
        )

        dib_qr = ImageWin.Dib(qr_img)
        dib_qr.draw(
            hdc.GetHandleOutput(),
            (base_x + 550, base_y + 80, base_x + 860, base_y + 380)
        )

        hdc.EndPage()
        hdc.EndDoc()

        print("🖨️ Etiqueta impressa com sucesso")
        return True

    finally:
        hdc.DeleteDC()
        win32print.ClosePrinter(hprinter)




#  ENVIO DE EMAIL DE CHECK-IN
#
# DEFINE:
#  Tipo (Cliente ou Fornecedor)
#  Assunto
#  Corpo HTML
#
#  ALTERAR TEXTO DO EMAIL:
# → Variável html_corpo


def enviaremailcheckin(config, emailsdestino: list, nome: str, empresa: str, grupoid: int, tipo: str = "fornecedores"):
    print("🔥 CONFIG RECEBIDA:", config)
    if not config or not emailsdestino:
        print("✗ Sem emails")
        return
    
    server = config["server"]
    port = config["port"]
    email_from = config["email"]
    password = config["password"]
    
    if tipo == "clientes":
        tipo_texto = "Cliente"
    elif tipo == "fornecedores":
        tipo_texto = "Fornecedor"
    else:
        tipo_texto = "Visitante"

    assunto = f"Confirmação de Presença de {tipo_texto}"
    hora_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # HTML simples (batch compatível)
    html_corpo = f"""
    Confirma-se a presença do <b>{tipo_texto} {nome}</b>, da <b>empresa {empresa}</b>, às <b>{hora_atual}</b>.<br>
    <b>Encontra-se na receção</b> 
    """
    
    try:
        smtp = smtplib.SMTP(server, port)
        smtp.starttls()
        smtp.login(email_from, password)
        
        # 🔄 BATCH como ANTES (To: todos)
        to_str = '; '.join(emailsdestino)
        msg = f"Subject: {assunto}\nTo: {to_str}\nContent-Type: text/html; charset=utf-8\n\n{html_corpo}"
        
        smtp.sendmail(email_from, emailsdestino, msg.encode('utf-8'))
        print(f"📧 ✓ {len(emailsdestino)} emails ({tipo_texto})")
        
        smtp.quit()
    except Exception as e:
        print(f"✗ SMTP: {e}")
    return


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
