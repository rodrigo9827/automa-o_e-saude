import pyodbc

# Endereço do banco (o mesmo que funcionou no teste.py)
STRING_CONEXAO = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=poc_gestante;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


def conectar():
    """Abre uma conexão com o banco."""
    return pyodbc.connect(STRING_CONEXAO)


def listar_enfermeiras():
    """Devolve a lista de enfermeiras, sem repetir, em ordem alfabética."""
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT DISTINCT enfermeira
            FROM dbo.vw_RetornoGestantes
            WHERE enfermeira IS NOT NULL
            ORDER BY enfermeira
        """)
        return [linha.enfermeira for linha in cursor.fetchall()]
    finally:
        conexao.close()


def buscar_gestantes(enfermeira):
    """Devolve as gestantes atendidas pela enfermeira, com IG, retorno, alto risco e CPF."""
    conexao = conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT gestante, cns, data_contato,
                   ig_semanas, ig_dias_resto,
                   data_retorno, alto_risco, cpf
            FROM dbo.vw_RetornoGestantes
            WHERE enfermeira = ?
            ORDER BY CASE WHEN data_retorno IS NULL THEN 1 ELSE 0 END,
                     data_retorno
        """, enfermeira)
        return cursor.fetchall()
    finally:
        conexao.close()