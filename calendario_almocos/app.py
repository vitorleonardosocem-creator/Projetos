from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import pyodbc
from datetime import date

app = Flask(__name__)
app.secret_key = 'cal_almocos_secret_2025'

DB_SERVER   = '192.168.10.156'
DB_DATABASE = 'Visitantes'
DB_USER     = 'GV'
DB_PASSWORD = 'NovaSenhaForte987'

APP_PASSWORD = 'RefeicoesED'
APP_PORT     = 5002


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
        if request.form.get('password') == APP_PASSWORD:
            session['auth'] = True
            return redirect(url_for('calendario'))
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
    return render_template('calendar.html', year=year, month=month)


# ---------------------------------------------------------------------------
# API – lunch counts for a month
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
        cursor.execute("""
            SELECT CAST(Data AS DATE) AS dia,
                   COUNT(*)          AS total
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
        rows = cursor.fetchall()
        conn.close()

        result = {}
        for row in rows:
            dia_str = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
            result[dia_str] = row[1]

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
            SELECT Nome, Empresa, Responsavel, 'Cliente' AS Tipo
            FROM   dbo.Visitantes
            WHERE  UPPER(LTRIM(RTRIM(Almoco))) = 'SIM'
              AND  CAST(Data AS DATE) = ?
            UNION ALL
            SELECT Nome, Empresa, Responsavel, 'Fornecedor' AS Tipo
            FROM   dbo.Visitantes_Fornecedores
            WHERE  UPPER(LTRIM(RTRIM(Almoco))) = 'SIM'
              AND  CAST(Data AS DATE) = ?
            ORDER BY Tipo, Nome
        """, data_str, data_str)
        rows = cursor.fetchall()
        conn.close()

        result = [
            {'nome': r[0] or '', 'empresa': r[1] or '', 'responsavel': r[2] or '', 'tipo': r[3] or ''}
            for r in rows
        ]
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT, debug=False)
