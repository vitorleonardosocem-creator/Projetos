from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import pyodbc
from datetime import date

app = Flask(__name__)
app.secret_key = 'cal_almocos_secret_2025'

DB_SERVER   = '192.168.10.156'
DB_DATABASE = 'Visitantes'
DB_USER     = 'GV'
DB_PASSWORD = 'NovaSenhaForte987'

APP_PASSWORD_USER  = 'RefeicoesED'
APP_PASSWORD_ADMIN = 'SocemED'
APP_PORT           = 5002


def get_conn():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('auth'):
        return redirect(url_for('calendario'))
    error = None
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if pwd == APP_PASSWORD_ADMIN:
            session['auth'] = True
            session['role'] = 'admin'
            return redirect(url_for('calendario'))
        elif pwd == APP_PASSWORD_USER:
            session['auth'] = True
            session['role'] = 'user'
            return redirect(url_for('calendario'))
        else:
            error = 'Password incorreta. Tente novamente.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# Calendar page
# ---------------------------------------------------------------------------

@app.route('/calendario')
def calendario():
    if not session.get('auth'):
        return redirect(url_for('login'))
    today = date.today()
    year  = request.args.get('year',  today.year,  type=int)
    month = request.args.get('month', today.month, type=int)
    role  = session.get('role', 'user')
    return render_template('calendar.html', year=year, month=month, role=role)


# ---------------------------------------------------------------------------
# API – lunch counts for a month (confirmed + present)
# ---------------------------------------------------------------------------

@app.route('/api/almocos')
def api_almocos():
    if not session.get('auth'):
        return jsonify({'error': 'Não autorizado'}), 401

    year  = request.args.get('year',  type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        return jsonify({'error': 'Parâmetros inválidos'}), 400

    try:
        conn   = get_conn()
        cursor = conn.cursor()

        # Confirmed counts (both tables)
        cursor.execute("""
            SELECT CAST(Data AS DATE) AS dia, COUNT(*) AS total
            FROM (
                SELECT Data FROM dbo.Visitantes
                WHERE  UPPER(LTRIM(RTRIM(Almoco))) = 'SIM'
                  AND  YEAR(Data) = ? AND MONTH(Data) = ?
                UNION ALL
                SELECT Data FROM dbo.Visitantes_Fornecedores
                WHERE  UPPER(LTRIM(RTRIM(Almoco))) = 'SIM'
                  AND  YEAR(Data) = ? AND MONTH(Data) = ?
            ) AS combined
            GROUP BY CAST(Data AS DATE)
        """, year, month, year, month)
        confirmed_rows = cursor.fetchall()

        # Present counts from AlmocoPresencas
        cursor.execute("""
            SELECT Data, COUNT(*) AS presentes
            FROM   dbo.AlmocoPresencas
            WHERE  Presente = 1
              AND  YEAR(Data) = ? AND MONTH(Data) = ?
            GROUP BY Data
        """, year, month)
        present_rows = cursor.fetchall()
        conn.close()

        result = {}
        for row in confirmed_rows:
            dia_str = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
            result[dia_str] = {'confirmados': row[1], 'presentes': 0}

        for row in present_rows:
            dia_str = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
            if dia_str in result:
                result[dia_str]['presentes'] = row[1]

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# API – detail for a specific day
# ---------------------------------------------------------------------------

@app.route('/api/dia/<data_str>')
def api_dia(data_str):
    if not session.get('auth'):
        return jsonify({'error': 'Não autorizado'}), 401

    try:
        conn   = get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.Id, v.Nome, v.Empresa, v.Responsavel,
                   'Cliente' AS Tipo,
                   ISNULL(p.Presente, 0) AS Presente
            FROM   dbo.Visitantes v
            LEFT JOIN dbo.AlmocoPresencas p
                   ON p.IdVisitante = v.Id
                  AND p.TipoVisitante = 'Cliente'
                  AND p.Data = ?
            WHERE  UPPER(LTRIM(RTRIM(v.Almoco))) = 'SIM'
              AND  CAST(v.Data AS DATE) = ?
            UNION ALL
            SELECT f.Id, f.Nome, f.Empresa, f.Responsavel,
                   'Fornecedor' AS Tipo,
                   ISNULL(p.Presente, 0) AS Presente
            FROM   dbo.Visitantes_Fornecedores f
            LEFT JOIN dbo.AlmocoPresencas p
                   ON p.IdVisitante = f.Id
                  AND p.TipoVisitante = 'Fornecedor'
                  AND p.Data = ?
            WHERE  UPPER(LTRIM(RTRIM(f.Almoco))) = 'SIM'
              AND  CAST(f.Data AS DATE) = ?
            ORDER BY Tipo, Nome
        """, data_str, data_str, data_str, data_str)
        rows = cursor.fetchall()
        conn.close()

        result = [
            {
                'id':          r[0],
                'nome':        r[1] or '',
                'empresa':     r[2] or '',
                'responsavel': r[3] or '',
                'tipo':        r[4] or '',
                'presente':    bool(r[5])
            }
            for r in rows
        ]
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# API – toggle presence (admin only)
# ---------------------------------------------------------------------------

@app.route('/api/presenca', methods=['POST'])
def api_presenca():
    if not session.get('auth'):
        return jsonify({'error': 'Não autorizado'}), 401
    if session.get('role') != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403

    data         = request.get_json()
    id_visitante = data.get('id_visitante')
    tipo         = data.get('tipo')
    data_str     = data.get('data')
    presente     = data.get('presente', False)

    if not all([id_visitante, tipo, data_str]):
        return jsonify({'error': 'Parâmetros inválidos'}), 400

    try:
        conn   = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Id FROM dbo.AlmocoPresencas
            WHERE IdVisitante = ? AND TipoVisitante = ? AND Data = ?
        """, id_visitante, tipo, data_str)
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE dbo.AlmocoPresencas
                SET    Presente = ?, DataMarcacao = GETDATE()
                WHERE  IdVisitante = ? AND TipoVisitante = ? AND Data = ?
            """, 1 if presente else 0, id_visitante, tipo, data_str)
        else:
            cursor.execute("""
                INSERT INTO dbo.AlmocoPresencas (IdVisitante, TipoVisitante, Data, Presente)
                VALUES (?, ?, ?, ?)
            """, id_visitante, tipo, data_str, 1 if presente else 0)

        conn.commit()
        conn.close()
        return jsonify({'ok': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT, debug=False)
