"""debug_reprocess.py
Script temporário para limpar e reprocessar Abril 2026.
"""
from base_dados import ligar_jogo
from jogo import reprocessar

print("A limpar pontos antigos de Abril 2026...")
conn = ligar_jogo()
c = conn.cursor()
c.execute("DELETE FROM pontos WHERE tarefa LIKE 'picagem_2026-04%'")
c.execute("UPDATE colaboradores SET pontos_total = 0")
conn.commit()
conn.close()
print("Limpeza feita.")

print("A reprocessar 01/04 a 21/04/2026 (pode demorar)...")
resultado = reprocessar("2026-04-01", "2026-04-21")
print("Resultado:", resultado)

print("\nVerificar Vitor e Ricardo:")
conn2 = ligar_jogo()
c2 = conn2.cursor()
c2.execute("SELECT nome_disp, pontos_total FROM colaboradores WHERE ID IN (1849, 74)")
for row in c2.fetchall():
    print(f"  {row[0]}: {row[1]:+d}")

print("\nTop 10:")
c2.execute("""
    SELECT TOP 10 nome_disp, pontos_total
    FROM colaboradores
    WHERE activo = 1 AND pontos_total != 0
    ORDER BY pontos_total DESC
""")
for row in c2.fetchall():
    print(f"  {row[0]}: {row[1]:+d}")
conn2.close()
