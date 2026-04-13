import pyodbc

DATABASE_URL = """
DRIVER={SQL Server};
SERVER=192.168.10.156;
DATABASE=GSMED;
UID=GV;
PWD=NovaSenhaForte987;
"""

def get_connection():
    return pyodbc.connect(DATABASE_URL)
