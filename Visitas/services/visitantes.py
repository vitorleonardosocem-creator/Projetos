from typing import List, Dict, Optional

from db import getconn  # Sem _, matching db.py


def listar_visitantes_hoje(tipo: str = "fornecedores") -> List[Dict]:
    """
    EXATO como VB: SELECT Id, Nome, Empresa, Data FROM ... WHERE CAST(Data AS DATE) >= CAST(GETDATE()-1 AS DATE)
    + PreConfirmado IS NULL OR 'NAO'
    """
    tabela = "Visitantes" if tipo == "clientes" else "Visitantes_Fornecedores"
    
    hoje = "CAST(GETDATE() AS DATE)"
    sql = f"""
    SELECT Id, Nome, Empresa, Responsavel, Data, PreConfirmado
    FROM {tabela}
    WHERE CAST(Data AS DATE) = {hoje}
    AND (PreConfirmado IS NULL OR PreConfirmado = 'NAO')
    ORDER BY Data DESC
    """
    
    with getconn() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        columns = [col[0] for col in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def obter_email_responsavel(visitante_id: int, tipo: str = "fornecedores") -> Optional[Dict]:
    """Obtém dados extras: Nome, Empresa, Telefone, Email, Responsavel, Observacao"""
    tabela = "Visitantes" if tipo == "clientes" else "Visitantes_Fornecedores"
    
    sql = f"""
        SELECT Nome, Empresa, Telefone, Email, Responsavel, Observacao
        FROM {tabela}
        WHERE Id = ?
    """
    with getconn() as conn:
        cur = conn.cursor()
        cur.execute(sql, (visitante_id,))
        row = cur.fetchone()
        if row:
            return {
                "Nome": row.Nome or "",
                "Empresa": row.Empresa or "",
                "Email": row.Email or "",
                "Responsavel": row.Responsavel or "",
                "Telefone": getattr(row, 'Telefone', '') or "",
                "Observacao": getattr(row, 'Observacao', '') or ""
            }
    return None

def marcar_preconfirmado(visitante_id: int) -> bool:
    """UPDATE ... SET PreConfirmado = 'SIM' WHERE Id = ? (igual VB)"""
    tabela = "Visitantes"  # Detecta pela tabela? Por agora Visitantes/Fornecedores
    for tabela_nome in ["Visitantes", "Visitantes_Fornecedores"]:
        sql_update = f"UPDATE {tabela_nome} SET PreConfirmado = 'SIM' WHERE Id = ?"
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute(sql_update, (visitante_id,))
            if cur.rowcount > 0:
                conn.commit()
                return True
    return False

def gravar_checkin(nome: str, email: str, empresa: str, responsavel: str):
    """INSERT INTO CheckIns (igual VB)"""
    try:
        sql = """
            INSERT INTO CheckIns (Nome, Email, DataCheckIn, Empresa, Responsavel)
            VALUES (?, ?, GETDATE(), ?, ?)
        """
        with getconn() as conn:
            cur = conn.cursor()
            cur.execute(sql, (nome, email, empresa, responsavel))
            conn.commit()
    except:
        pass  # Sem CheckIns OK
