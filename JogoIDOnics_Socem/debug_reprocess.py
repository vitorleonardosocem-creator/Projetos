"""debug_reprocess.py
Limpa toda a base de dados do jogo e reprocessa desde o início de Abril 2026.
Só são incluídos colaboradores com planos: SC-NORM, SC-NOR-BH, ST-NORM, SC-LIMP.
"""
from base_dados import ligar_jogo
from jogo import sincronizar_colaboradores, reprocessar
from idonics import PLANOS_JOGO

DATA_INI = "2026-04-01"
DATA_FIM = "2026-04-23"

print("=" * 60)
print("JogoIDOnics — Limpeza e reprocessamento completo")
print(f"Planos elegíveis: {', '.join(PLANOS_JOGO)}")
print(f"Periodo: {DATA_INI} a {DATA_FIM}")
print("=" * 60)

# ── 1. Limpar toda a BD do jogo ───────────────────────────────
print("\n[1/3] A limpar base de dados...")
conn = ligar_jogo()
c = conn.cursor()
c.execute("DELETE FROM pontos")
c.execute("DELETE FROM processamentos")
c.execute("UPDATE colaboradores SET pontos_total = 0, activo = 0")
conn.commit()
conn.close()
print("      Feito — pontos, processamentos e colaboradores limpos.")

# ── 2. Sincronizar colaboradores (só os planos elegíveis) ─────
print("\n[2/3] A sincronizar colaboradores do IDOnics...")
resultado_sync = sincronizar_colaboradores()
print(f"      Colaboradores activos : {resultado_sync['colaboradores']}")
print(f"      Departamentos         : {resultado_sync['departamentos']}")
print(f"      Marcados inactivos    : {resultado_sync['inactivados']}")

# ── 3. Reprocessar picagens ───────────────────────────────────
print(f"\n[3/3] A reprocessar {DATA_INI} a {DATA_FIM} (pode demorar)...")
resultado = reprocessar(DATA_INI, DATA_FIM)

if "erro" in resultado:
    print(f"      ERRO: {resultado['erro']}")
else:
    print(f"      Registos processados     : {resultado['inseridos']}")
    print(f"      Ignorados (folga/s plano): {resultado['ignorados']}")
    print(f"      Colaboradores afectados  : {resultado['colaboradores_afectados']}")

# ── Resumo final ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("Top 15 por pontos totais:")
conn2 = ligar_jogo()
c2 = conn2.cursor()
c2.execute("""
    SELECT TOP 15 c.nome_disp, c.pontos_total, d.nome AS dept
    FROM colaboradores c
    LEFT JOIN departamentos d ON d.id = c.id_departamento
    WHERE c.activo = 1 AND c.pontos_total != 0
    ORDER BY c.pontos_total DESC
""")
for row in c2.fetchall():
    print(f"  {row[0]:<35} {row[1]:>+4}  [{row[2] or '—'}]")

print("\nTotal de colaboradores activos no jogo:")
c2.execute("SELECT COUNT(*) FROM colaboradores WHERE activo = 1")
print(f"  {c2.fetchone()[0]}")
conn2.close()
print("=" * 60)
