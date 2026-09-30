import pyodbc
import os

SERVIDOR = "192.168.197.24"
BANCO = "GeoStaging"

STRING_CONEXAO = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVIDOR};DATABASE={BANCO};"
    #f"UID={os.environ['DB_USER']}"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

conexao = pyodbc.connect(STRING_CONEXAO, timeout=10)
try:
    cursor = conexao.cursor()

    # 1. Confirma em qual servidor/banco você realmente está
    cursor.execute("SELECT @@SERVERNAME, DB_NAME();")
    print("Conectado em:", cursor.fetchone())

    # 2. Consulta de teste (só leitura, limitada a 10 linhas)
    cursor.execute("SELECT TOP (10) * FROM map.Paciente;")
    colunas = [c[0] for c in cursor.description]
    print(colunas)
    for linha in cursor.fetchall():
        print(linha)
finally:
    conexao.close()