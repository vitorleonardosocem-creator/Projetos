from database import get_connection

try:
    conn = get_connection()
    cursor = conn.cursor()
    print("✅ CONECTADO ao 106.168.196!")
    
    cursor.execute("SELECT @@SERVERNAME")
    print("Servidor:", cursor.fetchone()[0])
    
    cursor.execute("SELECT COUNT(*) FROM Roles")
    print("Roles:", cursor.fetchone()[0])
    
    cursor.execute("""
        SELECT TOP 3 IdPC, TagInterna, Marca FROM Computadores
    """)
    print("PCs:", [dict(row) for row in cursor.fetchall()])
    
    conn.close()
    print("🎉 APP PRONTA!")
    
except Exception as e:
    print(f"❌ {e}")
