"""
================================================================
  ADICIONAR AO main.py  — Rota de estado do Job SINEX/CNC
================================================================
  Cola este bloco no final do teu main.py
================================================================
"""

from fastapi import APIRouter
import os

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
