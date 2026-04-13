# db.py - CORRIGIDO COMPLETO (compatível com services/visitantes.py + app.py)

import pyodbc

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.156;"
    "DATABASE=Visitantes;"
    "UID=GV;"
    "PWD=NovaSenhaForte987;"
    "TrustServerCertificate=Yes;"
)

def getconn():  # Nome EXATO que visitantes.py importa/usa
    return pyodbc.connect(CONN_STR)
