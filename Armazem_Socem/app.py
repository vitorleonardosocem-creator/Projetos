from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pyodbc import ProgrammingError, Error
from config import CONN_STR
from datetime import datetime
from utils.barcode import gerar_barcode_pdf
from utils.barcode import gerar_barcode_pdf, gerar_barcode_aco_pdf
from fastapi import FastAPI, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from functools import wraps
import utils.barcode as barcode_utils
import qrcode
import re
import pyodbc
import secrets
import os


def safe_db_operation(func):
    @wraps(func)  
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ProgrammingError, Error) as e:
            flash(f'❌ Erro BD: {str(e)[:100]}', 'danger')
            print(f"❌ SQL Error: {e}")
            return redirect(request.referrer or '/')
        except Exception as e:
            flash('❌ Erro inesperado!', 'danger')
            print(f"❌ Geral: {e}")
            return redirect(request.referrer or '/')
    return wrapper

def gerar_e_imprimir_qr(dados, pasta, filename, imprimir=False):
    os.makedirs(f'static/{pasta}', exist_ok=True)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(dados)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    filepath = f'static/{pasta}/{filename}.png'
    img.save(filepath)
    
    return filepath  # Sempre devolve path


def gerar_qr(dados, pasta, filename):
    """Gera QR PEQUENO e salva. Retorna path."""
    os.makedirs(f'static/{pasta}', exist_ok=True)
    qr = qrcode.QRCode(version=1, box_size=4, border=2)  # ✅ MUDANÇA 2: box_size=4 (era 10), border=2 (era 5)
    qr.add_data(dados)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    filepath = f'static/{pasta}/{filename}.png'
    img.save(filepath)
    return filepath

def gerar_e_imprimir_qr(dados, pasta, filename, imprimir=False):
    filepath = gerar_qr(dados, pasta, filename)  # Usa a nova pequena
    if imprimir:
        # Auto abre print se quiseres
        pass
    return filepath


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

def get_db_connection():
    return pyodbc.connect(CONN_STR)


@app.route('/')
@safe_db_operation 
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Totais (ativos)
    cursor.execute("SELECT COUNT(*) FROM Moldes WHERE ativo=1 OR ativo IS NULL")
    total_moldes = int(cursor.fetchone()[0] or 0)
    
    cursor.execute("SELECT COUNT(*) FROM Pecas WHERE ativo=1 OR ativo IS NULL")
    total_pecas = int(cursor.fetchone()[0] or 0)
    
    # MOLDES: Fora/Interno
    cursor.execute("""
        SELECT COUNT(CASE WHEN l.tipo_localizacao='Externo' THEN 1 END),
               COUNT(CASE WHEN l.tipo_localizacao='Interno' THEN 1 END)
        FROM Moldes m LEFT JOIN Localizacoes l ON m.localizacao_id = l.id
        WHERE m.ativo=1 OR m.ativo IS NULL
    """)
    moldes_row = cursor.fetchone() or (0, 0)
    moldes_fora = int(moldes_row[0])
    moldes_internos = int(moldes_row[1])
    
    # PEÇAS: Fora/Interno
    cursor.execute("""
        SELECT COUNT(CASE WHEN l.tipo_localizacao='Externo' THEN 1 END),
               COUNT(CASE WHEN l.tipo_localizacao='Interno' THEN 1 END)
        FROM Pecas p LEFT JOIN Localizacoes l ON p.localizacao_id = l.id
        WHERE p.ativo=1 OR p.ativo IS NULL
    """)
    pecas_row = cursor.fetchone() or (0, 0)
    pecas_fora = int(pecas_row[0])
    pecas_internos = int(pecas_row[1])
    
    # ✅ Moldes Finalizados (ativo=0)
    cursor.execute("SELECT COUNT(*) FROM Moldes WHERE ativo=0")
    moldes_finalizados = int(cursor.fetchone()[0] or 0)
    
    # ✅ Peças Finalizadas (ativo=0)
    cursor.execute("SELECT COUNT(*) FROM Pecas WHERE ativo=0")
    pecas_finalizadas = int(cursor.fetchone()[0] or 0)
    
    # Gráfico Moldes por Localização (apenas ativos)
    cursor.execute("""
        SELECT COALESCE(l.nome, 'Sem Loc') nome, COUNT(m.id)
        FROM Moldes m LEFT JOIN Localizacoes l ON m.localizacao_id = l.id
        WHERE m.ativo=1 OR m.ativo IS NULL
        GROUP BY l.nome
    """)
    moldes_por_loc = cursor.fetchall()
    
    # Gráfico Peças por Localização (apenas ativos)
    cursor.execute("""
        SELECT COALESCE(l.nome, 'Sem Loc') nome, COUNT(p.id)
        FROM Pecas p LEFT JOIN Localizacoes l ON p.localizacao_id = l.id
        WHERE p.ativo=1 OR p.ativo IS NULL
        GROUP BY l.nome
    """)
    pecas_por_loc = cursor.fetchall()
    
    # ✅ ✅ CORRIGIDO: Moldes Recentes (SQL Server TOP 10)
    cursor.execute("""
        SELECT TOP 10 m.id, m.nome, COALESCE(l.nome, 'Sem Loc') as localizacao_nome, m.data_criacao
        FROM Moldes m 
        LEFT JOIN Localizacoes l ON m.localizacao_id = l.id
        WHERE m.ativo=1 OR m.ativo IS NULL
        ORDER BY m.data_criacao DESC
    """)
    moldes_recentes = cursor.fetchall()
    
    conn.close()
    
    print(f"🚀 DASHBOARD OK: Moldes={total_moldes} (fora={moldes_fora}, int={moldes_internos}, fin={moldes_finalizados})")
    print(f"🚀 DASHBOARD OK: Peças={total_pecas} (fora={pecas_fora}, int={pecas_internos}, fin={pecas_finalizadas})")
    print(f"🚀 Moldes recentes: {len(moldes_recentes)}")
    
    return render_template('index.html',
        total_moldes=total_moldes, total_pecas=total_pecas,
        moldes_fora=moldes_fora, moldes_internos=moldes_internos,
        pecas_fora=pecas_fora, pecas_internos=pecas_internos,
        moldes_finalizados=moldes_finalizados,
        pecas_finalizadas=pecas_finalizadas,
        moldes_por_loc=moldes_por_loc,
        pecas_por_loc=pecas_por_loc,
        moldes_recentes=moldes_recentes)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Totais
    cursor.execute("SELECT COUNT(*) FROM Moldes WHERE ativo=1 OR ativo IS NULL")
    total_moldes = int(cursor.fetchone()[0] or 0)
    
    cursor.execute("SELECT COUNT(*) FROM Pecas WHERE ativo=1 OR ativo IS NULL")
    total_pecas = int(cursor.fetchone()[0] or 0)
    
    # MOLDES por tipo (Virgent=Externo → 1 Fora)
    cursor.execute("""
        SELECT COUNT(CASE WHEN l.tipo_localizacao='Externo' THEN 1 END) as fora,
               COUNT(CASE WHEN l.tipo_localizacao='Interno' THEN 1 END) as internos
        FROM Moldes m LEFT JOIN Localizacoes l ON m.localizacao_id = l.id
        WHERE (m.ativo=1 OR m.ativo IS NULL)
    """)
    moldes_row = cursor.fetchone() or (0, 0)
    moldes_fora = int(moldes_row[0])
    moldes_internos = int(moldes_row[1])
    
    # PEÇAS por tipo
    cursor.execute("""
        SELECT COUNT(CASE WHEN l.tipo_localizacao='Externo' THEN 1 END) as fora,
               COUNT(CASE WHEN l.tipo_localizacao='Interno' THEN 1 END) as internos
        FROM Pecas p LEFT JOIN Localizacoes l ON p.localizacao_id = l.id
        WHERE (p.ativo=1 OR p.ativo IS NULL)
    """)
    pecas_row = cursor.fetchone() or (0, 0)
    pecas_fora = int(pecas_row[0])
    pecas_internos = int(pecas_row[1])
    
    # Gráfico
    cursor.execute("""
        SELECT COALESCE(l.nome, 'Sem Loc') nome, COUNT(*) qtd
        FROM Moldes m LEFT JOIN Localizacoes l ON m.localizacao_id = l.id
        WHERE m.ativo=1 OR m.ativo IS NULL
        GROUP BY l.nome
    """)
    moldes_por_loc = cursor.fetchall()
    
    conn.close()
    
    # CONFIRMAÇÃO
    print(f"🚀 PASSANDO: moldes_fora={moldes_fora} pecas_fora={pecas_fora}")
    
    return render_template('dashboard.html',
        total_moldes=total_moldes, total_pecas=total_pecas,
        moldes_fora=moldes_fora, moldes_internos=moldes_internos,
        pecas_fora=pecas_fora, pecas_internos=pecas_internos,
        moldes_por_loc=moldes_por_loc)

@app.route('/dashboard_operador')
def dashboard_operador():
    if session.get('user_tipo') != 'operador':
        return redirect(url_for('index'))
    return render_template('dashboard_operador.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, tipo FROM Utilizadores WHERE email=? AND senha=? AND ativo=1", (email, senha))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['user_nome'] = user[1]
            session['user_tipo'] = user[2]
            
            # 🔄 NOVA LÓGICA: Redireciona por tipo
            if user[2] == 'operador':
                return redirect(url_for('dashboard_operador'))
            else:  # admin
                return redirect(url_for('index'))  # Teu dashboard atual
        else:
            flash('Credenciais inválidas!')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado!')
    return redirect(url_for('login'))



@app.route('/usuarios')
def usuarios():
    if 'user_id' not in session or session['user_tipo'] != 'admin':
        flash('Acesso negado!')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, email, tipo, ativo, data_criacao 
        FROM Utilizadores 
        ORDER BY nome
    """)
    usuarios = cursor.fetchall()
    conn.close()
    
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/criar', methods=['POST'])
def usuario_criar():
    if 'user_id' not in session or session['user_tipo'] != 'admin':
        flash('Acesso negado!')
        return redirect(url_for('index'))
    
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    tipo = request.form['tipo']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Utilizadores (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                     (nome, email, senha, tipo))
        conn.commit()
        conn.close()
        flash(f'✅ Utilizador "{nome}" criado com sucesso!', 'success')
    except pyodbc.IntegrityError:
        flash('❌ Email já existe!', 'danger')
    except Exception as e:
        flash(f'❌ Erro: {str(e)}', 'danger')
    
    # 🔧 IMPORTANTE: REDIRECIONA para a lista (NÃO JSON!)
    return redirect(url_for('usuarios'))


@app.route('/usuarios/editar/<int:user_id>', methods=['GET', 'POST'])
def usuario_editar(user_id):
    if 'user_id' not in session or session['user_tipo'] != 'admin':
        flash('Acesso negado!')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        tipo = request.form['tipo']
        ativo = 1 if 'ativo' in request.form else 0
        
        try:
            cursor.execute("""
                UPDATE Utilizadores 
                SET nome=?, email=?, tipo=?, ativo=? 
                WHERE id=?
            """, (nome, email, tipo, ativo, user_id))
            conn.commit()
            flash('Utilizador atualizado!')
        except Exception as e:
            flash(f'Erro: {str(e)}')
        
        conn.close()
        return redirect(url_for('usuarios'))
    
    cursor.execute("SELECT id, nome, email, tipo, ativo FROM Utilizadores WHERE id=?", (user_id,))
    usuario = cursor.fetchone()
    conn.close()
    
    if not usuario:
        flash('Utilizador não encontrado!')
        return redirect(url_for('usuarios'))
    
    return render_template('usuario_editar.html', usuario=usuario)

@app.route('/usuarios/reset_senha/<int:user_id>', methods=['POST'])
def usuario_reset_senha(user_id):
    if 'user_id' not in session or session['user_tipo'] != 'admin':
        return jsonify({'success': False}), 403
    
    nova_senha = '123456'
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Utilizadores SET senha=? WHERE id=?", (nova_senha, user_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'nova_senha': nova_senha})
    except:
        return jsonify({'success': False}), 500

@app.route('/usuarios/delete/<int:user_id>', methods=['POST'])
def usuario_delete(user_id):
    if 'user_id' not in session or session['user_tipo'] != 'admin':
        return jsonify({'success': False}), 403
    
    # Só desativa (não apaga mesmo)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Utilizadores SET ativo=0 WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False}), 500


@app.route('/picking')
def picking():
    return render_template('picking.html')

@app.route('/api/picking_scan', methods=['POST'])
def picking_scan():
    codigo_barra = request.json['codigo']
    nova_localizacao = request.json['localizacao']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tenta primeiro em Moldes, depois Pecas
    cursor.execute("""
        SELECT m.id, m.nome, l.codigo as loc_atual 
        FROM Moldes m
        LEFT JOIN Localizacoes l ON m.localizacao_id = l.id
        WHERE m.qr_codigo = ? OR m.nome = ?
    """, (codigo_barra, codigo_barra))
    item = cursor.fetchone()
    
    if not item:
        cursor.execute("""
            SELECT p.id, p.nome, l.codigo as loc_atual 
            FROM Pecas p
            LEFT JOIN Localizacoes l ON p.localizacao_id = l.id
            WHERE p.qr_codigo = ? OR p.codigo_peca = ?
        """, (codigo_barra, codigo_barra))
        item = cursor.fetchone()
    
    if item:
        # Atualiza (ajusta tabela conforme tipo)
        if 'm.id' in str(item):  # Moldes
            cursor.execute("""
                UPDATE Moldes SET localizacao_id=?, data_ultima_mov=? WHERE id=?
            """, (nova_localizacao, datetime.now(), item[0]))
        else:  # Pecas
            cursor.execute("""
                UPDATE Pecas SET localizacao_id=?, data_ultima_mov=? WHERE id=?
            """, (nova_localizacao, datetime.now(), item[0]))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'nome': item[1],
            'localizacao_antiga': item[2],
            'localizacao_nome': 'Nova localização'
        })
    
    conn.close()
    return jsonify({'success': False, 'error': 'Item não encontrado'})



@app.route('/procurar')
def procurar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM Localizacoes WHERE ativo=1 ORDER BY nome")
    localizacoes = cursor.fetchall()
    conn.close()
    
    return render_template('procurar.html', localizacoes=localizacoes)

@app.route('/procurar/resultados')
def procurar_resultados():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    termo = request.args.get('termo', '').strip().upper()
    localizacao_id = request.args.get('localizacao')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 🔍 UNION Moldes + Peças
    query = """
        -- Moldes
        SELECT 'molde' AS tipo, m.id, m.nome AS codigo, m.nome, 
               '-' AS molde_nome, l.nome AS localizacao, 
               m.data_ultima_movimentacao AS ultima_mov
        FROM Moldes m 
        LEFT JOIN Localizacoes l ON m.localizacao_id = l.id
        WHERE m.ativo = 1
    """
    params = []
    
    if termo:
        query += " AND (m.nome LIKE ?)"
        params.append(f'%{termo}%')
    
    if localizacao_id:
        query += " AND (m.localizacao_id = ? OR l.id = ?)"
        params.extend([localizacao_id, localizacao_id])
    
    query += """
        UNION ALL
        -- Peças
        SELECT 'peca' AS tipo, p.id, p.codigo_peca AS codigo, p.nome, 
               m.nome AS molde_nome, l.nome AS localizacao, 
               p.data_ultima_movimentacao AS ultima_mov
        FROM Pecas p 
        LEFT JOIN Moldes m ON p.molde_id = m.id
        LEFT JOIN Localizacoes l ON p.localizacao_id = l.id
        WHERE p.ativo = 1
    """
    
    if termo:
        query += " AND (p.codigo_peca LIKE ? OR p.nome LIKE ? OR m.nome LIKE ?)"
        params.extend([f'%{termo}%', f'%{termo}%', f'%{termo}%'])
    
    if localizacao_id:
        query += " AND p.localizacao_id = ?"
        params.append(localizacao_id)
    
    query += " ORDER BY codigo"
    
    cursor.execute(query, params)
    resultados_raw = cursor.fetchall()
    
    # Converte para dicts (template usa item.codigo, etc.)
    resultados = []
    for row in resultados_raw:
        resultados.append({
            'tipo': row[0],
            'id': row[1],
            'codigo': row[2],
            'nome': row[3],
            'molde_nome': row[4],
            'localizacao': row[5],
            'ultima_mov': row[6]
        })
    
    cursor.execute("SELECT id, nome FROM Localizacoes WHERE ativo=1 ORDER BY nome")
    localizacoes = cursor.fetchall()
    
    conn.close()
    
    return render_template('procurar.html', 
                         resultados=resultados, 
                         termo=termo, 
                         localizacao=localizacao_id,
                         localizacoes=localizacoes)



@app.route('/localizacoes/imprimir/<int:loc_id>')
def localizacao_imprimir(loc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nome, barcode FROM Localizacoes WHERE id=?", (loc_id,))
    loc = cursor.fetchone()
    conn.close()
    
    if loc:
        codigo_para_scan = loc[2] or f"LOC:{loc_id}"
        nome_arquivo = f"LOC_{loc[0] or loc_id}.pdf"
        barcode_pdf = gerar_barcode_pdf(codigo_para_scan, nome_arquivo)
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>🖨️ Barcode {loc[1]}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body{{text-align:center;padding:20px;font-family:Arial;background:#f8f9fa;}}
            .btn{{padding:12px 24px;font-size:16px;border-radius:8px;text-decoration:none;margin:10px;display:inline-block;}}
            .btn-success{{background:#28a745;color:white;}}
            .btn-primary{{background:#007bff;color:white;}}
            iframe{{border:2px solid #007bff;border-radius:8px;max-width:400px;}}
        </style></head>
        <body>
            <h2>📍 <strong>{loc[1]}</strong></h2>
            <h4>Scanner lê: <code>{codigo_para_scan}</code></h4>
            <iframe src="{barcode_pdf}" width="90%" height="400"></iframe>
            <br>
            <a href="{barcode_pdf}" download="{nome_arquivo}" class="btn btn-success">📥 Download</a>
            <button onclick="window.print()" class="btn btn-primary">🖨️ Imprimir</button>
        </body></html>
        '''
    flash('❌ Localização não encontrada!')
    return redirect(url_for('localizacoes'))



@app.route('/scan')
def scan_page():
    if 'user_nome' not in session:
        return redirect(url_for('login'))
    return render_template('scan_aco.html', usuario=session['user_nome'])


@app.route('/localizacoes_json')
def localizacoes_json():
    """🔧 POPULA dropdown com todas localizações"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, descricao FROM Localizacoes WHERE ativo=1 ORDER BY nome")
    locais = []
    for row in cursor.fetchall():
        locais.append({
            'nome': row[0],  # S9
            'descricao': row[1] or ''  # Descrição opcional
        })
    conn.close()
    return jsonify(locais)

@app.route('/localizacoes')
def localizacoes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.id, l.nome, 
               COUNT(m.id) as num_moldes,
               COUNT(p.id) as num_pecas
        FROM Localizacoes l
        LEFT JOIN Moldes m ON m.localizacao_id = l.id AND m.ativo=1  -- ✅ só ativas
        LEFT JOIN Pecas p ON p.localizacao_id = l.id AND p.ativo=1   -- ✅ só ativas
        WHERE l.ativo = 1
        GROUP BY l.id, l.nome
        ORDER BY l.nome
    """)
    locais_raw = cursor.fetchall()
    conn.close()
    
    # Teu dict (perfeito pro template)
    locais = []
    for row in locais_raw:
        locais.append({
            'id': row[0],
            'nome': row[1],
            'num_moldes': row[2] or 0,
            'num_pecas': row[3] or 0
        })
    
    return render_template('localizacoes.html', locais=locais)



@app.route('/localizacoes/<int:loc_id>')
def localizacao_detalhes(loc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    search = request.args.get('search', '').strip().upper()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Nome localização
    cursor.execute("SELECT id, nome FROM Localizacoes WHERE id=?", (loc_id,))
    loc = cursor.fetchone()
    if not loc:
        flash('❌ Localização não encontrada!', 'danger')
        return redirect(url_for('index'))
    
    loc_id, loc_nome = loc
    
    # FILTRO: Moldes com nome LIKE search
    cursor.execute("""
        SELECT m.id, m.nome, m.qr_codigo, COUNT(p.id) as num_pecas
        FROM Moldes m 
        LEFT JOIN Pecas p ON p.molde_id = m.id AND p.localizacao_id = ?
        WHERE m.localizacao_id = ? 
        AND (m.nome LIKE ? OR ? = '')
        GROUP BY m.id, m.nome, m.qr_codigo
        ORDER BY m.nome
    """, (loc_id, loc_id, f'%{search}%', search))
    moldes = cursor.fetchall()
    
    # FILTRO: Peças com nome/codigo/molde LIKE search
    cursor.execute("""
        SELECT p.id, p.codigo_peca, p.nome, p.qr_codigo, m.nome as molde_nome
        FROM Pecas p
        JOIN Moldes m ON m.id = p.molde_id
        WHERE p.localizacao_id = ?
        AND (p.nome LIKE ? OR p.codigo_peca LIKE ? OR m.nome LIKE ? OR ? = '')
        ORDER BY p.codigo_peca
    """, (loc_id, f'%{search}%', f'%{search}%', f'%{search}%', search))
    pecas = cursor.fetchall()
    
    conn.close()
    
    return render_template('localizacao_detalhes.html', 
                         loc_id=loc_id, loc_nome=loc_nome, 
                         moldes=moldes, pecas=pecas, search=search)


@app.route('/localizacao/criar', methods=['GET', 'POST'])
def localizacao_criar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        codigo = request.form['codigo'].strip()
        descricao = request.form['descricao'].strip()
        tipo_localizacao = request.form['tipo_localizacao']  # ← NOVO

        if not codigo:
            flash('O campo CÓDIGO é obrigatório (vai ser usado no barcode).', 'warning')
            return render_template('localizacao_criar.html', 
                                 nome=nome, descricao=descricao, tipo_localizacao=tipo_localizacao)

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Localizacoes (codigo, nome, descricao, tipo_localizacao, ativo, data_criacao, barcode)
                VALUES (?, ?, ?, ?, 1, GETDATE(), ?)
            """, (codigo, nome, descricao, tipo_localizacao, codigo))
            conn.commit()

            flash(f'Localização {nome} ({tipo_localizacao}) criada! Barcode: {codigo}', 'success')
            return redirect(url_for('localizacoes'))

        except Exception as e:
            conn.rollback()
            flash(f'Erro ao criar: {e}', 'danger')
        finally:
            conn.close()

    return render_template('localizacao_criar.html')



@app.route('/localizacoes/nova')
def localizacoes_nova():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Usa o mesmo template de criação já usado em /localizacao/criar
    return render_template('localizacao_criar.html')


@app.route('/historico/<codigo_barra>')
def historico_aco(codigo_barra):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Histórico (sempre funciona)
    cursor.execute("""
        SELECT TOP 50 
            data_movimento, localizacao_anterior, localizacao_nova, usuario
        FROM Historico_Movimentacoes 
        WHERE codigo_barra=?
        ORDER BY data_movimento DESC
    """, (codigo_barra,))
    
    historico = []
    for row in cursor.fetchall():
        historico.append({
            'data': row[0],
            'de': row[1] or 'Criação',
            'para': row[2],
            'usuario': row[3]
        })
    
    # 2. POSIÇÃO ATUAL - TUA ESTRUTURA EXATA
    cursor.execute("""
        SELECT a.localizacao_id, l.nome as loc_nome
        FROM Acos a
        LEFT JOIN Localizacoes l ON a.localizacao_id = l.id
        WHERE a.codigo_barra = ?
    """, (codigo_barra,))
    
    atual_row = cursor.fetchone()
    if atual_row:
        atual_localizacao = atual_row[1] if atual_row[1] else f'ID {atual_row[0]}'
    else:
        atual_localizacao = 'Não encontrado'
    
    conn.close()
    return render_template('historico_aco.html', 
                         codigo=codigo_barra, 
                         historico=historico, 
                         atual_localizacao=atual_localizacao)


@app.route('/molde/criar', methods=['GET', 'POST'])
@safe_db_operation 
def molde_criar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome as designacao FROM localizacoes ORDER BY nome")
    localizacoes = cursor.fetchall()
    
    if request.method == 'POST':
        nome = request.form['nome'].strip().upper()
        localizacao_id = request.form['localizacao_id']
        observacoes = request.form['observacoes']
        imprimir = request.form.get('imprimir_qr') == '1'
        
        # 🔹 VALIDAÇÃO: nome já existe?
        cursor.execute("SELECT id FROM Moldes WHERE nome = ? AND ativo = 1", (nome,))
        if cursor.fetchone():
            flash(f'❌ Molde <strong>{nome}</strong> já existe!', 'warning')
            return render_template('molde_criar.html', 
                                 localizacoes=localizacoes, 
                                 nome_input=nome)
        
        try:
            cursor.execute("""
                SET NOCOUNT ON;
                INSERT INTO Moldes (qr_codigo, nome, localizacao_id, observacoes, data_criacao, data_ultima_movimentacao, ativo)
                VALUES ('', ?, ?, ?, GETDATE(), GETDATE(), 1);
                SELECT SCOPE_IDENTITY() as id;
            """, (nome, localizacao_id, observacoes))
            molde_id = cursor.fetchone()[0]
            
            qr_data = nome
            qr_path = gerar_e_imprimir_qr(qr_data, 'qr_moldes', f'molde_{molde_id}', False)
            
            cursor.execute("UPDATE Moldes SET qr_codigo = ? WHERE id = ?", (qr_path, molde_id))
            conn.commit()
            
            if imprimir:
                conn.close()
                return redirect(url_for('imprimir_qr_id', tipo='molde', id=molde_id))
            
            flash(f'✅ Molde <strong>{nome}</strong> criado! <a href="/imprimir_qr/molde/{molde_id}" target="_blank" class="btn btn-sm btn-primary">🖨️ Imprimir QR</a>', 'success')
                
        except Exception as e:
            conn.rollback()
            flash(f'❌ Erro: {str(e)}', 'danger')
    
    conn.close()
    return render_template('molde_criar.html', localizacoes=localizacoes)



@app.route('/peca/criar', methods=['GET', 'POST'])
@safe_db_operation 
def peca_criar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome FROM Moldes WHERE ativo=1 ORDER BY nome")
    moldes = cursor.fetchall()
    
    cursor.execute("SELECT id, nome as designacao FROM localizacoes ORDER BY nome")
    localizacoes = cursor.fetchall()
    
    if request.method == 'POST':
        molde_id = request.form['molde_id']
        codigo_peca_input = request.form['codigo_peca'].strip().upper()  # ← 2000
        localizacao_id = request.form['localizacao_id']
        observacoes = request.form['observacoes']
        imprimir = request.form.get('imprimir_qr') == '1'
        
        # 🔹 Nome do molde do banco
        cursor.execute("SELECT nome FROM Moldes WHERE id=?", (molde_id,))
        nome_molde_raw = cursor.fetchone()[0]
        
        # 🔹 LIMPA nome_molde (só letras/números)
        nome_molde = ''.join(c for c in nome_molde_raw if c.isalnum()).upper()
        codigo_peca_limpo = ''.join(c for c in codigo_peca_input if c.isalnum()).upper()
        
        # 🔹 codigo_peca = APENAS o número digitado (2000)
        codigo_peca = codigo_peca_limpo
        
        # 🔹 nome = nome_molde + codigo (ED26M40042000) ← para QR
        nome_peca_completo = f"{nome_molde}{codigo_peca_limpo}"
        
        # 🔹 VALIDAÇÃO: já existe esta peça neste molde?
        cursor.execute("""
            SELECT id FROM Pecas 
            WHERE molde_id = ? AND codigo_peca = ? AND ativo = 1
        """, (molde_id, codigo_peca))
        
        if cursor.fetchone():
            flash(f'❌ Peça <strong>{codigo_peca}</strong> já existe neste molde!', 'warning')
            return render_template('peca_criar.html', 
                                 moldes=moldes, localizacoes=localizacoes,
                                 molde_id=molde_id, codigo_peca_input=codigo_peca_input)
        
        try:
            # INSERT
            cursor.execute("""
                SET NOCOUNT ON;
                INSERT INTO Pecas (codigo_peca, nome, molde_id, localizacao_id, observacoes,
                                   data_criacao, data_ultima_movimentacao, ativo)
                VALUES (?, ?, ?, ?, ?, GETDATE(), GETDATE(), 1);
                SELECT SCOPE_IDENTITY() as id;
            """, (codigo_peca, nome_peca_completo, molde_id, localizacao_id, observacoes))
            peca_id = cursor.fetchone()[0]
            
            # 🔹 QR usa NOME COMPLETO (ED26M40042000)
            qr_data = nome_peca_completo
            qr_path = gerar_e_imprimir_qr(qr_data, 'qr_pecas', f'peca_{peca_id}', False)
            
            # UPDATE qr_codigo
            cursor.execute("UPDATE Pecas SET qr_codigo = ? WHERE id = ?", (qr_path, peca_id))
            conn.commit()
            
            if imprimir:
                conn.close()
                return redirect(url_for('imprimir_qr_id', tipo='peca', id=peca_id))
            
            flash(
                f'✅ Peça <strong>{codigo_peca}</strong> criada (QR: {nome_peca_completo})! '
                f'<a href="/imprimir_qr/peca/{peca_id}" target="_blank" class="btn btn-sm btn-primary">🖨️ Imprimir QR</a>',
                'success'
            )
                
        except Exception as e:
            conn.rollback()
            flash(f'❌ Erro: {str(e)}', 'danger')
    
    conn.close()
    return render_template('peca_criar.html', moldes=moldes, localizacoes=localizacoes)

# ===== MOLDES =====
@app.route('/molde/editar/<int:id>', methods=['GET', 'POST'])
@safe_db_operation 
def molde_editar(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form['nome'].strip().upper()
        localizacao_id = request.form['localizacao_id']
        observacoes = request.form.get('observacoes', '')
        estado = request.form['estado']
        
        # Pega localização anterior
        cursor.execute("SELECT localizacao_id FROM Moldes WHERE id=?", (id,))
        loc_anterior = cursor.fetchone()[0]
        
        # UPDATE básico
        cursor.execute("""
            UPDATE Moldes SET nome=?, localizacao_id=?, observacoes=?, estado=?, 
            data_ultima_movimentacao=GETDATE()
            WHERE id=? AND ativo=1
        """, (nome, localizacao_id, observacoes, estado, id))
        
        # 🔥 LÓGICA ESPECIAL: FINALIZADO → EXPORTADO + HISTÓRICO
        if estado == 'Finalizado':
            # Encontra ID "Exportado"
            cursor.execute("SELECT id FROM Localizacoes WHERE nome = 'Exportado'")
            exportado = cursor.fetchone()
            
            if exportado:
                exportado_id = exportado[0]
                
                # 1️⃣ Histórico MOLDE
                cursor.execute("""
                    INSERT INTO Historico_Movimentacoes 
                    (tipo_entidade, entidade_id, codigo, localizacao_anterior, 
                     localizacao_nova, observacoes)
                    VALUES ('molde', ?, ?, ?, ?, 'Finalizado → Exportado')
                """, (id, nome, loc_anterior or 0, exportado_id))
                
                # 2️⃣ UPDATE Molde → Exportado + inativo
                cursor.execute("""
                    UPDATE Moldes SET localizacao_id=?, ativo=0 WHERE id=?
                """, (exportado_id, id))
                
                # 3️⃣ Histórico PEÇAS (todas do molde)
                cursor.execute("""
                    INSERT INTO Historico_Movimentacoes_Pecas 
                    (peca_id, codigo_peca, localizacao_anterior, localizacao_nova, 
                     observacoes, data_movimento, Utilizador)
                    SELECT p.id, p.codigo_peca, p.localizacao_id, ?, 
                           'Molde Finalizado → Exportado', GETDATE(), ?
                    FROM Pecas p WHERE p.molde_id = ?
                """, (exportado_id, session['user_nome'], id))
                
                # 4️⃣ UPDATE Peças → Exportado + inativo
                cursor.execute("""
                    UPDATE Pecas SET localizacao_id=?, ativo=0 WHERE molde_id=?
                """, (exportado_id, id))
                
                # Conta peças
                cursor.execute("SELECT COUNT(*) FROM Pecas WHERE molde_id=?", (id,))
                qtd_pecas = cursor.fetchone()[0]
                
                flash(f'✅ FINALIZADO! Molde + {qtd_pecas} peças → Exportado (histórico registado)', 'success')
            else:
                flash('❌ Crie localização "Exportado" primeiro!', 'warning')
        
        conn.commit()
        conn.close()
        return redirect(url_for('moldes_listar'))
    
    # GET: carrega molde
    cursor.execute("""
        SELECT id, nome, localizacao_id, observacoes, estado 
        FROM Moldes WHERE id=? AND ativo=1
    """, (id,))
    molde = cursor.fetchone()
    
    if not molde:
        flash('❌ Molde não encontrado', 'danger')
        conn.close()
        return redirect(url_for('moldes_listar'))
    
    cursor.execute("SELECT id, nome FROM Localizacoes WHERE ativo=1 ORDER BY nome")
    localizacoes = cursor.fetchall()
    conn.close()
    
    return render_template('molde_editar.html', molde=molde, localizacoes=localizacoes)


@app.route('/molde/apagar/<int:id>')
@safe_db_operation 
def molde_apagar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Pecas WHERE molde_id=? AND ativo=1", (id,))
    pecas = cursor.fetchone()[0]
    
    if pecas > 0:
        flash(f'❌ {pecas} peça(s) associada(s)!', 'danger')
    else:
        cursor.execute("UPDATE Moldes SET ativo=0 WHERE id=? AND ativo=1", (id,))
        conn.commit()
        flash('🗑️ Molde inativado!', 'success')
    
    conn.close()
    return redirect(url_for('moldes_listar'))  # ✅ moldes_listar

@app.route('/moldes-finalizados')
def moldes_finalizados():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search = request.args.get('search', '').strip()
    query = """
        SELECT m.id, m.nome, m.qr_codigo, m.observacoes, 
               m.data_criacao, m.data_ultima_movimentacao,
               COUNT(p.id) as total_pecas
        FROM Moldes m 
        LEFT JOIN Pecas p ON m.id = p.molde_id 
        WHERE m.ativo = 0
    """
    params = []
    
    if search:
        query += " AND (m.nome LIKE ? OR m.id LIKE ? OR m.qr_codigo LIKE ?)"
        search_param = f"%{search}%"
        params = [search_param, search_param, search_param]
    
    query += " GROUP BY m.id, m.nome, m.qr_codigo, m.observacoes, m.data_criacao, m.data_ultima_movimentacao ORDER BY m.data_ultima_movimentacao DESC"
    
    cursor.execute(query, params)
    moldes_finalizados = cursor.fetchall()
    
    conn.close()
    return render_template('moldes_finalizados.html', moldes=moldes_finalizados, search=search)


@app.route('/molde/reativar/<int:molde_id>', methods=['POST'])
def reativar_molde(molde_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Reativar molde (usa ? para pyodbc)
        cursor.execute("""
            UPDATE Moldes 
            SET ativo=1, estado='Montagem', data_ultima_movimentacao=GETDATE()
            WHERE id = ?
        """, (molde_id,))
        
        # Reativar peças associadas
        cursor.execute("""
            UPDATE Pecas 
            SET ativo=1 
            WHERE molde_id = ?
        """, (molde_id,))
        
        conn.commit()
        print(f"✅ Molde {molde_id} reativado + peças!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro reativar molde {molde_id}: {e}")
        flash('❌ Erro ao reativar molde!', 'danger')
        return redirect(url_for('moldes_finalizados'))
    
    conn.close()
    flash('✅ Molde e peças reativados com sucesso!', 'success')
    return redirect(url_for('moldes_finalizados'))

@app.route('/molde/visualizar/<int:molde_id>')
def visualizar_molde(molde_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Molde completo
    cursor.execute("""
        SELECT m.id, m.qr_codigo, m.nome, m.localizacao_id,
               COALESCE(l.nome, 'Sem Loc') as loc_nome, 
               COALESCE(l.tipo_localizacao, 'N/A') as tipo_loc,
               m.observacoes, m.data_criacao, m.data_ultima_movimentacao,
               m.ativo, m.estado, m.data_movimento
        FROM Moldes m 
        LEFT JOIN Localizacoes l ON m.localizacao_id = l.id
        WHERE m.id = ?
    """, (molde_id,))
    molde = cursor.fetchone()
    
    if not molde:
        flash('❌ Molde não encontrado!', 'warning')
        return redirect(url_for('moldes_finalizados'))
    
    # Peças do molde (colunas reais)
    cursor.execute("""
        SELECT p.id, p.codigo_peca, p.nome, p.localizacao_id,
               COALESCE(l.nome, 'Sem Loc') as loc_nome,
               COALESCE(l.tipo_localizacao, 'N/A') as tipo_loc,
               p.qr_codigo, p.ativo, p.data_criacao, p.data_ultima_movimentacao
        FROM Pecas p 
        LEFT JOIN Localizacoes l ON p.localizacao_id = l.id
        WHERE p.molde_id = ? 
        ORDER BY p.id
    """, (molde_id,))
    pecas = cursor.fetchall()
    
    conn.close()
    return render_template('molde_inativos_visualizar.html', molde=molde, pecas=pecas, total_pecas=len(pecas))


# ===== PEÇAS ===== (similar)
@app.route('/peca/editar/<int:id>', methods=['GET', 'POST'])
@safe_db_operation 
def peca_editar(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        localizacao_id = request.form['localizacao_id']
        observacoes = request.form.get('observacoes', '')
        
        cursor.execute("""
            UPDATE Pecas SET localizacao_id=?, observacoes=?, 
            data_ultima_movimentacao=GETDATE()
            WHERE id=? AND ativo=1
        """, (localizacao_id, observacoes, id))
        conn.commit()
        flash('✅ Peça atualizada!', 'success')
        conn.close()
        return redirect(url_for('pecas_listar'))
    
    cursor.execute("""
        SELECT id, codigo_peca, nome, molde_id, localizacao_id, observacoes
        FROM Pecas WHERE id=? AND ativo=1
    """, (id,))
    peca = cursor.fetchone()
    
    if not peca:
        flash('❌ Peça não encontrada', 'danger')
        return redirect(url_for('pecas_listar'))
    
    cursor.execute("SELECT id, nome FROM Moldes WHERE ativo=1 ORDER BY nome")
    moldes = cursor.fetchall()
    
    cursor.execute("SELECT id, nome FROM Localizacoes WHERE ativo=1 ORDER BY nome")
    localizacoes = cursor.fetchall()
    conn.close()
    
    return render_template('peca_editar.html', peca=peca, moldes=moldes, localizacoes=localizacoes)

@app.route('/peca/apagar/<int:id>')
@safe_db_operation 
def peca_apagar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT nome FROM Pecas WHERE id=? AND ativo=1", (id,))
    peca_nome = cursor.fetchone()
    
    cursor.execute("UPDATE Pecas SET ativo=0 WHERE id=? AND ativo=1", (id,))
    conn.commit()
    
    if peca_nome:
        flash(f'🗑️ Peça {peca_nome[0]} inativada!', 'success')
    else:
        flash('❌ Peça não encontrada', 'danger')
    
    conn.close()
    return redirect(url_for('pecas_listar'))


# ===== LOCALIZAÇÕES =====
@app.route('/localizacao/editar/<int:id>', methods=['GET', 'POST'])
@safe_db_operation 
def localizacao_editar(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nome = request.form['nome'].strip().upper()
        tipo_localizacao = request.form['tipo_localizacao']
        
        cursor.execute("""
            UPDATE Localizacoes SET nome=?, tipo_localizacao=? 
            WHERE id=? AND ativo=1
        """, (nome, tipo_localizacao, id))
        conn.commit()
        flash('✅ Localização atualizada!', 'success')
        conn.close()
        return redirect(url_for('localizacoes'))
    
    cursor.execute("SELECT id, nome, tipo_localizacao FROM Localizacoes WHERE id=? AND ativo=1", (id,))
    loc = cursor.fetchone()
    
    if not loc:
        flash('❌ Localização não encontrada', 'danger')
        return redirect(url_for('localizacoes'))
    
    conn.close()
    return render_template('localizacao_editar.html', localizacao=loc)

@app.route('/localizacao/apagar/<int:id>')
@safe_db_operation 
def localizacao_apagar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as total FROM (
            SELECT localizacao_id FROM Moldes WHERE localizacao_id=? AND ativo=1
            UNION ALL
            SELECT localizacao_id FROM Pecas WHERE localizacao_id=? AND ativo=1
        ) t
    """, (id, id))
    usados = cursor.fetchone()[0]
    
    if usados > 0:
        flash(f'❌ {usados} item(ns) nesta localização!', 'danger')
    else:
        cursor.execute("UPDATE Localizacoes SET ativo=0 WHERE id=? AND ativo=1", (id,))
        conn.commit()
        flash('🗑️ Localização inativada!', 'success')
    
    conn.close()
    return redirect(url_for('localizacoes'))



@app.route('/movimento/molde', methods=['GET', 'POST'])
@safe_db_operation 
def movimento_molde():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nome_molde = request.form['qr_molde'].strip().upper()
        barcode_loc = request.form['barcode_localizacao'].strip()
        utilizador = session['user_nome']
        now = datetime.now()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Molde (MESMO)
        cursor.execute("""
            SELECT m.id, m.nome, m.localizacao_id, l.nome AS loc_atual_nome, m.estado
            FROM Moldes m LEFT JOIN Localizacoes l ON m.localizacao_id = l.id
            WHERE m.nome = ?
        """, (nome_molde,))
        molde_row = cursor.fetchone()
        if not molde_row:
            conn.close()
            flash(f'❌ Molde <code>{nome_molde}</code> não encontrado!')
            return render_template('movimento_molde.html')
        
        molde_id, nome_ok, loc_ant_id, loc_ant_nome, estado = molde_row
        
        # Nova loc (MESMO)
        cursor.execute("""
            SELECT l1.id, l1.nome 
            FROM Localizacoes l1 WHERE l1.barcode = ?
        """, (barcode_loc,))
        loc_nova_row = cursor.fetchone()
        if not loc_nova_row:
            conn.close()
            flash(f'❌ Localização <code>{barcode_loc}</code> não encontrada!')
            return render_template('movimento_molde.html')
        
        loc_nova_id, loc_nova_nome = loc_nova_row
        
        # ✅ NOVO: Se Finalizado → MOVE PEÇAS AUTOMATICAMENTE
        pecas_movidas = 0
        if estado == 'Finalizado':
            cursor.execute("""
                UPDATE Pecas SET localizacao_id=?, data_ultima_movimentacao=?, data_movimento=?
                WHERE molde_id=? AND ativo=1
            """, (loc_nova_id, now, now, molde_id))
            pecas_movidas = cursor.rowcount  # Nº peças afetadas
            
            # REGISTRO PEÇAS (tua tabela específica)
            cursor.execute("""
                INSERT INTO Historico_Movimentacoes_Pecas 
                (peca_id, codigo_peca, localizacao_anterior, localizacao_nova, 
                 data_movimento, observacoes, Utilizador)
                SELECT id, codigo_peca, localizacao_id AS anterior, ?, ?, 
                       'Movimento automático com Molde ' + ? + ' (Finalizado)', ?
                FROM Pecas WHERE molde_id=? AND ativo=1
            """, (loc_nova_id, now, nome_ok, utilizador, molde_id))
        
        # UPDATE Moldes (MESMO)
        cursor.execute("""
            UPDATE Moldes SET localizacao_id=?, data_ultima_movimentacao=?, data_movimento=?
            WHERE id=?
        """, (loc_nova_id, now, now, molde_id))
        
        # INSERT Molde (MELHORADO com info lote)
        obs = f"Peças movidas: {pecas_movidas}" if pecas_movidas > 0 else "Molde simples"
        cursor.execute("""
            INSERT INTO Historico_Movimentacoes 
            (tipo_entidade, entidade_id, codigo, localizacao_anterior, localizacao_nova, 
             data_movimento, observacoes, Utilizador)
            VALUES ('MOLDE', ?, ?, ?, ?, ?, ?, ?)
        """, (molde_id, nome_ok, loc_ant_id, loc_nova_id, now, obs, utilizador))
        
        conn.commit()
        conn.close()
        flash(f'✅ <strong>{nome_ok}</strong> → <strong>{loc_nova_nome}</strong> {obs}')
        return redirect(url_for('movimento_molde'))
    
    return render_template('movimento_molde.html')


# ===== Para user Tipo Operador =====

@app.route('/mover_molde', methods=['GET', 'POST'])
@safe_db_operation 
def mover_molde():
    if not session.get('user_tipo') in ['operador', 'admin']:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        qr_molde = request.form['qr_molde'].strip()
        barcode_localizacao = request.form['barcode_localizacao'].strip()
        
        # ✅ BUSCA ESTADO do molde
        cursor.execute("""
            SELECT id, nome, localizacao_id, estado 
            FROM Moldes WHERE qr_codigo=? OR nome=?
        """, (qr_molde, qr_molde))
        molde = cursor.fetchone()
        
        if molde:
            cursor.execute("SELECT id, nome FROM Localizacoes WHERE codigo=?", (barcode_localizacao,))
            nova_loc = cursor.fetchone()
            
            if nova_loc:
                loc_anterior = molde[2] or 0
                estado = molde[3] or 'Montagem'
                
                # SEMPRE move molde
                cursor.execute("""
                    UPDATE Moldes SET localizacao_id=?, data_ultima_movimentacao=GETDATE() 
                    WHERE id=?
                """, (nova_loc[0], molde[0]))
                
                qtd_pecas_movidas = 0
                
                # ✅ SÓ move peças se Finalizado
                if estado == 'Finalizado':
                    cursor.execute("""
                        UPDATE Pecas SET localizacao_id=? WHERE molde_id=?
                    """, (nova_loc[0], molde[0]))
                    qtd_pecas_movidas = cursor.rowcount
                
                # Histórico
                obs = f'Movimento molde (estado: {estado})'
                if qtd_pecas_movidas > 0:
                    obs += f' + {qtd_pecas_movidas} peças'
                
                cursor.execute("""
                    INSERT INTO Historico_Movimentacoes 
                    (tipo_entidade, entidade_id, codigo, localizacao_anterior, 
                     localizacao_nova, observacoes, Utilizador)
                    VALUES ('molde', ?, ?, ?, ?, ?, ?)
                """, (molde[0], molde[1], loc_anterior, nova_loc[0], obs, session['user_nome']))
                
                conn.commit()
                flash(f'✅ {obs} → {nova_loc[1]} por {session["user_nome"]}', 'success')
            else:
                flash('❌ Localização inválida!', 'danger')
        else:
            flash('❌ Molde não encontrado!', 'danger')
        conn.close()
    
    return render_template('movimento_molde.html')




@app.route('/mover_peca', methods=['GET', 'POST'])
@safe_db_operation 
def mover_peca():
    # Admin redireciona para dashboard, operador usa
    if session.get('user_tipo') == 'admin':
        flash('👨‍💼 Use dashboard admin para movimentações', 'info')
        return redirect(url_for('index'))
    
    if not session.get('user_tipo') == 'operador':
        return redirect(url_for('index'))
   
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        codigo_peca = request.form['codigo_peca'].strip()
        barcode_localizacao = request.form['barcode_localizacao'].strip()
        observacoes = request.form.get('observacoes', '')
        
        # ✅ SELECT 4 COLUNAS (id, nome, codigo_peca, localizacao_id)
        cursor.execute("""
            SELECT id, nome, codigo_peca, localizacao_id FROM Pecas 
            WHERE qr_codigo=? OR nome=? OR codigo_peca=?
        """, (codigo_peca, codigo_peca, codigo_peca))
        peca = cursor.fetchone()
        
        if not peca:
            flash('❌ Peça não encontrada!', 'danger')
        else:
            cursor.execute("SELECT id, nome FROM Localizacoes WHERE codigo=?", (barcode_localizacao,))
            nova_loc = cursor.fetchone()
            
            if nova_loc:
                # UPDATE
                cursor.execute("""
                    UPDATE Pecas SET localizacao_id=?, data_ultima_movimentacao=GETDATE(), 
                    data_movimento=GETDATE() WHERE id=?
                """, (nova_loc[0], peca[0]))
                
                # INSERT (peca[0]=id, peca[2]=codigo_peca, peca[3]=localizacao_id)
                cursor.execute("""
                    INSERT INTO Historico_Movimentacoes_Pecas 
                    (peca_id, codigo_peca, localizacao_anterior, localizacao_nova, 
                     observacoes, data_movimento, Utilizador)
                    VALUES (?, ?, ?, ?, ?, GETDATE(), ?)
                """, (peca[0], peca[2], peca[3] or 0, nova_loc[0], observacoes, session['user_nome']))
                
                conn.commit()
                flash(f'✅ Peça {peca[2]} ({peca[1]}) → {nova_loc[1]} por {session["user_nome"]}', 'success')
                conn.close()
                return render_template('movimento_peca.html', limpar_form=True)
            else:
                flash('❌ Localização inválida!', 'danger')
        conn.close()
        return render_template('movimento_peca.html')
    
    # Últimas
    cursor.execute("""
        SELECT TOP 5 p.nome, ISNULL(l_ant.nome,'-'), ISNULL(l_nova.nome,'-'), h.data_movimento
        FROM Historico_Movimentacoes_Pecas h
        JOIN Pecas p ON h.peca_id = p.id
        LEFT JOIN Localizacoes l_ant ON h.localizacao_anterior = l_ant.id
        LEFT JOIN Localizacoes l_nova ON h.localizacao_nova = l_nova.id
        ORDER BY h.data_movimento DESC
    """)
    ultimas_pecas = cursor.fetchall()
    conn.close()
    
    return render_template('movimento_peca.html', ultimas_pecas=ultimas_pecas)


# ===== Historicos =====


@app.route('/historico/molde/<int:molde_id>')
def historico_molde(molde_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.nome, l.nome AS loc_atual
        FROM Moldes m LEFT JOIN Localizacoes l ON m.localizacao_id = l.id
        WHERE m.id = ?
    """, (molde_id,))
    molde_info = cursor.fetchone()
    if not molde_info:
        flash('Molde não encontrado')
        conn.close()
        return redirect(url_for('index'))
    
    nome_molde, loc_atual = molde_info
    
    # ✅ Histórico com JOINs corretos (IDs → nomes)
    cursor.execute("""
        SELECT h.data_movimento, 
               la.nome AS localizacao_anterior, 
               ln.nome AS localizacao_nova, 
               h.Utilizador
        FROM Historico_Movimentacoes h
        LEFT JOIN Localizacoes la ON h.localizacao_anterior = la.id
        LEFT JOIN Localizacoes ln ON h.localizacao_nova = ln.id
        WHERE h.tipo_entidade = 'MOLDE' AND h.entidade_id = ?
        ORDER BY h.data_movimento DESC
    """, (molde_id,))
    hist_molde = cursor.fetchall()
    
    cursor.execute("""
        SELECT p.id, p.codigo_peca AS nome, l.nome AS loc_peca
        FROM Pecas p LEFT JOIN Localizacoes l ON p.localizacao_id = l.id
        WHERE p.molde_id = ? AND p.ativo = 1 ORDER BY p.codigo_peca
    """, (molde_id,))
    pecas = cursor.fetchall()
    
    conn.close()
    return render_template('historico_molde.html',
                         nome_molde=nome_molde, loc_atual=loc_atual,
                         historico=hist_molde, pecas=pecas)


@app.route('/moldes')
@safe_db_operation 
def moldes_listar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    search = request.args.get('search', '').strip().upper()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT m.id, m.nome, COALESCE(l.nome, 'Sem') as loc_nome, 
               COALESCE(m.qr_codigo, '') as qr_codigo,
               ISNULL(pecas_ativas.num_pecas, 0) as num_pecas,
               MAX(h.data_movimento) as ultima_mov
        FROM Moldes m
        LEFT JOIN Localizacoes l ON l.id = m.localizacao_id
        LEFT JOIN (
            SELECT molde_id, COUNT(*) as num_pecas 
            FROM Pecas WHERE ativo=1 
            GROUP BY molde_id
        ) pecas_ativas ON pecas_ativas.molde_id = m.id
        LEFT JOIN Historico_Movimentacoes h ON h.entidade_id = m.id AND h.tipo_entidade = 'MOLDE'
        WHERE m.ativo=1
    """
    params = []
    if search:
        query += " AND m.nome LIKE ?"
        params.append(f'%{search}%')
    
    query += " GROUP BY m.id, m.nome, l.nome, m.qr_codigo, pecas_ativas.num_pecas ORDER BY m.nome"
    
    cursor.execute(query, params)
    moldes = cursor.fetchall()
    conn.close()
    
    return render_template('moldes.html', moldes=moldes, search=search)


@app.route('/pecas')
@safe_db_operation 
def pecas_listar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    search = request.args.get('search', '').strip()
    sort_col = request.args.get('sort', 'id')
    sort_dir = request.args.get('dir', 'asc')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT p.id, p.codigo_peca, p.nome, ISNULL(m.nome, 'Sem Molde') as molde_nome, 
               ISNULL(l.nome, 'Sem Loc') as localizacao_nome, 
               p.data_ultima_movimentacao as ultima_mov
        FROM Pecas p
        LEFT JOIN Moldes m ON p.molde_id = m.id
        LEFT JOIN Localizacoes l ON p.localizacao_id = l.id
        WHERE p.ativo = 1
    """
    
    params = []
    if search:
        query += """
            AND (
                UPPER(p.codigo_peca) LIKE ? 
                OR UPPER(p.nome) LIKE ? 
                OR UPPER(ISNULL(m.nome, '')) LIKE ? 
                OR UPPER(ISNULL(l.nome, '')) LIKE ?
            )
        """
        params = [f"%{search}%"] * 4
    
    # ✅ Ordenação SEMProblemas
    if sort_col == 'codigo':
        order_by = f"p.codigo_peca {'DESC' if sort_dir == 'asc' else 'ASC'}"
    elif sort_col == 'moldes':
        order_by = f"ISNULL(m.nome, 'ZZZ') {'DESC' if sort_dir == 'asc' else 'ASC'}"
    elif sort_col == 'localizacao':
        order_by = f"ISNULL(l.nome, 'ZZZ') {'DESC' if sort_dir == 'asc' else 'ASC'}"
    else:
        order_by = "p.id ASC"
    
    query += f" ORDER BY {order_by}"
    
    print(f"🔍 QUERY: {query}")
    print(f"🔍 SORT: {sort_col}/{sort_dir}")
    
    cursor.execute(query, params)
    pecas = cursor.fetchall()
    conn.close()
    
    print(f"✅ {len(pecas)} peças")
    return render_template('pecas.html', pecas=pecas, search=search, sort_col=sort_col, sort_dir=sort_dir)



@app.route('/pecas_json/<int:molde_id>')
@safe_db_operation 
def pecas_json(molde_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.codigo_peca, l.nome as loc_nome, p.qr_codigo
        FROM Pecas p JOIN Localizacoes l ON l.id = p.localizacao_id
        WHERE p.molde_id = ?
        ORDER BY p.codigo_peca
    """, (molde_id,))
    pecas = cursor.fetchall()
    conn.close()
    
    html = '<div class="row g-3"><h6>Peças do Molde:</h6>'
    for peca_id, codigo, loc, qr_codigo in pecas:
        qr_btn = '<a href="/imprimir_qr/peca/' + str(peca_id) + '" class="btn btn-sm btn-primary">QR</a>' if qr_codigo else ''
        html += f'''
            <div class="col-md-3">
                <div class="card shadow-sm">
                    <div class="card-body p-2 text-center">
                        <strong>{codigo}</strong><br>
                        <small class="text-muted">{loc}</small>
                        <div class="mt-1">
                            {qr_btn}
                            <a href="/historico/peca/{peca_id}" class="btn btn-sm btn-info">Histórico</a>
                        </div>
                    </div>
                </div>
            </div>
        '''
    html += '</div>'
    return html



@app.route('/historico/<tipo>/<int:item_id>')
def historico(tipo, item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if tipo == 'molde':
        cursor.execute("""
            SELECT h.data_movimento,
                   la.nome,
                   ln.nome,
                   m.nome,
                   h.Utilizador
            FROM Historico_Movimentacoes h
            JOIN Moldes m ON h.entidade_id = m.id
            LEFT JOIN Localizacoes la ON h.localizacao_anterior = la.id
            LEFT JOIN Localizacoes ln ON h.localizacao_nova = ln.id
            WHERE h.tipo_entidade = 'MOLDE' AND h.entidade_id = ?
            ORDER BY h.data_movimento DESC
        """, (item_id,))
        
    elif tipo == 'peca':
        cursor.execute("""
            SELECT h.data_movimento,
                   la.nome,
                   ln.nome,
                   p.codigo_peca,
                   h.Utilizador
            FROM Historico_Movimentacoes_Pecas h
            JOIN Pecas p ON h.peca_id = p.id
            LEFT JOIN Localizacoes la ON h.localizacao_anterior = la.id
            LEFT JOIN Localizacoes ln ON h.localizacao_nova = ln.id
            WHERE h.peca_id = ?
            ORDER BY h.data_movimento DESC
        """, (item_id,))
    
    movimentacoes = cursor.fetchall()
    conn.close()
    
    return render_template('historico.html', 
                         tipo=tipo, item_id=item_id, 
                         movimentacoes=movimentacoes)


@app.route('/historico')
def historico_geral():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 50 m.data_mov, m.item_tipo, m.item_id,
               CASE WHEN m.item_tipo='molde' THEN md.nome ELSE pc.nome END as item_nome,
               la.nome as de, ln.nome as para, u.nome as usuario
        FROM Movimentacoes m
        LEFT JOIN Moldes md ON m.item_tipo='molde' AND m.item_id=md.id
        LEFT JOIN Pecas pc ON m.item_tipo='peca' AND m.item_id=pc.id
        LEFT JOIN Localizacoes la ON m.localizacao_id_anterior=la.id
        LEFT JOIN Localizacoes ln ON m.localizacao_id_nova=ln.id
        LEFT JOIN Utilizadores u ON m.utilizador_id=u.id
        ORDER BY m.data_mov DESC
    """)
    movimentacoes = cursor.fetchall()
    conn.close()
    
    return render_template('historico.html', movimentacoes=movimentacoes)

@app.route('/api/moldes/<int:molde_id>/pecas')
@safe_db_operation 
def api_pecas_molde(molde_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.id, p.codigo_peca, COALESCE(l.nome, 'Sem') AS localizacao, 
               p.qr_codigo, h.data_movimento AS ultima_mov
        FROM Pecas p 
        LEFT JOIN Localizacoes l ON p.localizacao_id = l.id
        LEFT JOIN (
            SELECT peca_id, MAX(data_movimento) as data_movimento
            FROM Historico_Movimentacoes_Pecas 
            GROUP BY peca_id
        ) h ON h.peca_id = p.id
        WHERE p.molde_id = ? AND p.ativo = 1 
        ORDER BY h.data_movimento DESC, p.codigo_peca
    """, (molde_id,))
    
    html = '<div class="row g-0 gy-1"><h6 class="mb-2"><i class="fas fa-cubes me-2"></i>Peças:</h6>'  # ✅ MUDANÇA 1: g-0 gy-1 = 4px
    
    if cursor.rowcount == 0:
        html += '<div class="col-12"><div class="alert alert-info">Nenhuma peça ativa</div></div>'
    else:
        for row in cursor.fetchall():
            p_id, codigo, loc, qr_codigo, ultima_mov = row
            qr_btn = f'<a href="/imprimir_qr/peca/{p_id}" class="btn btn-sm btn-outline-primary" target="_blank"><i class="fas fa-qrcode"></i></a>' if qr_codigo else ''
            hist_btn = f'<a href="/historico/peca/{p_id}" class="btn btn-sm btn-outline-info"><i class="fas fa-history"></i></a>'
            move_btn = '<a href="/movimento/peca" class="btn btn-sm btn-outline-warning"><i class="fas fa-exchange-alt"></i></a>'
            
            mov_text = ultima_mov.strftime('%d/%m %H:%M') if ultima_mov else '--/-- --:--'
            
            html += f'''
            <div class="col-12 mt-1 mb-0">  <!-- ✅ MUDANÇA 2: mt-1=4px top, mb-0=0 baixo -->
                <div class="card shadow-sm mb-0">  <!-- ✅ MUDANÇA 3: mb-0 zero margem card -->
                    <div class="card-body p-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="d-flex align-items-center gap-2 flex-grow-1">  <!-- ✅ MUDANÇA 4: flex-grow-1 ocupa espaço -->
                                <div class="d-flex align-items-center gap-1">
                                    <h6 class="mb-0 fw-bold me-2">{codigo}</h6>
                                    <small class="text-muted">
                                        <i class="fas fa-map-marker-alt me-1"></i>{loc}
                                    </small>
                                </div>
                                <div class="d-flex align-items-center gap-1 ms-4">  <!-- ms-4=24px direita -->
                                    <small class="text-muted">
                                        <i class="fas fa-clock me-1"></i>Últ.Mov.
                                    </small>
                                    <span class="badge bg-secondary fs-6">{mov_text}</span>  <!-- fs-6 menor -->
                                </div>
                            </div>
                            <div class="btn-group btn-group-sm">
                                {qr_btn}{hist_btn}{move_btn}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            '''
    
    html += '</div>'
    conn.close()
    return html


@app.route('/movimento/peca', methods=['GET', 'POST'])
@safe_db_operation 
def movimento_peca():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        codigo_peca_raw = request.form['codigo_peca'].strip().upper()
        barcode_loc = request.form['barcode_localizacao'].strip()  # ✅ MUDANÇA 1: barcode
        obs = request.form.get('observacoes', '').strip()
        utilizador = session['user_nome']
        now = datetime.now()
        
        try:
            # 1️⃣ Encontra peça
            cursor.execute("""
                SELECT id, codigo_peca, localizacao_id, molde_id 
                FROM Pecas 
                WHERE (codigo_peca = ? OR nome = ?) AND ativo=1
            """, (codigo_peca_raw, codigo_peca_raw))
            peca_row = cursor.fetchone()
            
            if not peca_row:
                flash(f'❌ Peça {codigo_peca_raw} não encontrada!', 'danger')
            else:
                peca_id, codigo_peca, loc_anterior_id, molde_id = peca_row
                
                # ✅ MUDANÇA 2: Busca localização por barcode (igual molde)
                cursor.execute("""
                    SELECT id, nome FROM Localizacoes WHERE barcode = ?
                """, (barcode_loc,))
                loc_nova_row = cursor.fetchone()
                if not loc_nova_row:
                    flash(f'❌ Localização <code>{barcode_loc}</code> não encontrada!', 'danger')
                else:
                    loc_nova_id, loc_nova_nome = loc_nova_row
                    
                    # 3️⃣ Nome anterior
                    cursor.execute("SELECT nome FROM Localizacoes WHERE id=?", (loc_anterior_id,))
                    loc_ant_nome_result = cursor.fetchone()
                    loc_ant_nome = loc_ant_nome_result[0] if loc_ant_nome_result else 'Sem'
                    
                    # 4️⃣ INSERE HISTÓRICO
                    cursor.execute("""
                        INSERT INTO Historico_Movimentacoes_Pecas 
                        (peca_id, codigo_peca, localizacao_anterior, localizacao_nova, 
                         data_movimento, observacoes, Utilizador)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (peca_id, codigo_peca, loc_anterior_id, loc_nova_id, now, obs, utilizador))
                    
                    # 5️⃣ ATUALIZA peça
                    cursor.execute("""
                        UPDATE Pecas 
                        SET localizacao_id = ?, data_ultima_movimentacao = ?, data_movimento = ?
                        WHERE id = ?
                    """, (loc_nova_id, now, now, peca_id))
                    
                    conn.commit()
                    flash(f'✅ {codigo_peca} → {loc_nova_nome}', 'success')
        
        except Exception as e:
            conn.rollback()
            flash(f'❌ Erro: {e}', 'danger')
        finally:
            conn.close()
            return redirect(url_for('movimento_peca'))
    
    # 🔹 ÚLTIMAS PEÇAS MOVIDAS (mantem igual)
    cursor.execute("""
        SELECT TOP 5 p.codigo_peca, p.data_ultima_movimentacao, m.nome
        FROM Pecas p 
        LEFT JOIN Moldes m ON p.molde_id = m.id
        WHERE p.data_ultima_movimentacao IS NOT NULL
        ORDER BY p.data_ultima_movimentacao DESC
    """)
    ultimas_pecas = cursor.fetchall()
    conn.close()
    
    return render_template('movimento_peca.html', ultimas_pecas=ultimas_pecas)



@app.route('/imprimir_qr/<tipo>/<int:id>')
@safe_db_operation 
def imprimir_qr_id(tipo, id):
    from urllib.parse import quote  # ← adiciona esta linha
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if tipo == 'molde':
        cursor.execute("SELECT qr_codigo FROM Moldes WHERE id=?", (id,))
    else:
        cursor.execute("SELECT qr_codigo FROM Pecas WHERE id=?", (id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        qr_path = result[0]
        # ✅ Passa página anterior (ou default)
        origem = request.referrer or '/moldes'
        origem_encoded = quote(origem)
        return render_template('imprimir_qr_limpo.html', 
                             qr_path=qr_path, 
                             origem=origem_encoded)
    
    return "❌ QR não encontrado", 404


@app.route('/mover_moldes', methods=['GET', 'POST'])  # ← Remove <id>, usa QR
@safe_db_operation 
def mover_molde_por_qr():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        qr_codigo = request.form['qr_codigo'].strip()
        localizacao_id = int(request.form['localizacao_id'])
        obs = request.form.get('observacoes', '').strip()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Procura molde pelo qr_codigo
        cursor.execute("""
            SELECT id, nome, localizacao_id, l.nome as loc_atual
            FROM Moldes m
            LEFT JOIN Localizacoes l ON l.id = m.localizacao_id
            WHERE qr_codigo = ? AND ativo = 1
        """, (qr_codigo,))
        molde = cursor.fetchone()

        if not molde:
            conn.close()
            flash(f'❌ Molde com QR <code>{qr_codigo}</code> não encontrado!', 'danger')
            return render_template('mover_molde.html')

        molde_id, nome, loc_ant_id, loc_ant_nome = molde
        now = datetime.now()

        # Nome nova loc
        cursor.execute("SELECT nome FROM Localizacoes WHERE id = ?", (localizacao_id,))
        loc_nova_nome = cursor.fetchone()[0]

        # UPDATE
        cursor.execute("""
            UPDATE Moldes SET localizacao_id = ?, data_ultima_movimentacao = ?, 
                              data_movimento = ? WHERE id = ?
        """, (localizacao_id, now, now, molde_id))

        # Movimentacoes
        cursor.execute("""
            INSERT INTO Movimentacoes (item_tipo, item_id, localizacao_id_anterior, 
                                     localizacao_id_nova, utilizador_id, data_mov, observacoes)
            VALUES ('molde', ?, ?, ?, ?, ?, ?)
        """, (molde_id, loc_ant_id, localizacao_id, session['user_id'], now, obs))

        conn.commit()
        conn.close()

        flash(f'✅ <strong>{nome}</strong> movido: {loc_ant_nome or "Criação"} → {loc_nova_nome}', 'success')
        return redirect(url_for('moldes_listar'))

    # GET: carrega dropdowns
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, barcode FROM Localizacoes WHERE ativo = 1 ORDER BY nome")
    localizacoes = cursor.fetchall()
    conn.close()

    return render_template('mover_molde.html', localizacoes=localizacoes)


@app.route('/mover_moldes/<int:molde_id>')
@safe_db_operation 
def mover_molde_por_id(molde_id):
    return redirect(url_for('movimento_molde'))  # Redireciona para template mobile


@app.route('/mover_pecas/<int:peca_id>')
@safe_db_operation 
def mover_peca_por_id(peca_id):
    return redirect(url_for('movimento_peca'))  # Redireciona para template mobile



if __name__ == '__main__':
    app.run(
        debug=True, 
        host='0.0.0.0',      # ← Aceita conexões externas
        port=5000,           # ← Porta padrão
        threaded=True        # ← Melhor performance
    )




