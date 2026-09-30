"""Grava os registros das janelas no banco, SÓ nas tabelas novas do schema "app".
Nenhuma tabela existente (dbo.*, stg.*) é alterada.

- app.Monitora_Gestante_Adm : histórico. Cada envio = UMA linha nova (INSERT).
- app.Gestante_Atual        : situação atual de cada gestante (MERGE = insere ou atualiza).
                              Cada gestante é identificada pela "chave": o CNS, ou
                              "CPF 12345678909" quando não houver CNS.

As duas gravações acontecem juntas numa TRANSAÇÃO: ou as duas dão certo, ou nenhuma fica.
"""
import pyodbc
from tratando_csv import STRING_CONEXAO

TEMPO_CONEXAO = 5      # segundos: se o SQL Server estiver fora, desiste rápido (a janela não trava)

TABELA_ADM   = "app.Monitora_Gestante_Adm"
TABELA_ATUAL = "app.Gestante_Atual"

# ------------------------------------------------------------
# Situação atual: insere se a gestante é nova; se já existe, atualiza.
# - Só atualiza se o contato novo for do mesmo dia ou mais novo que o guardado
#   (um registro atrasado não "volta" a gestante para trás).
# - Campo que veio vazio (NULL) NÃO apaga o que já estava lá (COALESCE).
# - IG: semanas e dias andam juntos.
# - Caso crítico "Não": limpa a descrição do caso crítico.
# ------------------------------------------------------------
SQL_ATUAL = f"""
MERGE {TABELA_ATUAL} WITH (HOLDLOCK) AS t
USING (SELECT
        CAST(? AS varchar(20))     AS chave,
        CAST(? AS varchar(15))     AS cns,
        CAST(? AS varchar(11))     AS cpf,
        CAST(? AS nvarchar(255))   AS gestante,
        CAST(? AS nvarchar(255))   AS enfermeira,
        CAST(? AS nvarchar(50))    AS teleoperador,
        CAST(? AS nvarchar(20))    AS classificacao,
        CAST(? AS nvarchar(3))     AS conseguiu_contato,
        CAST(? AS date)            AS data_contato,
        CAST(? AS tinyint)         AS ig_semanas,
        CAST(? AS tinyint)         AS ig_dias,
        CAST(? AS date)            AS data_retorno,
        CAST(? AS bit)             AS alto_risco,
        CAST(? AS nvarchar(3))     AS caso_critico,
        CAST(? AS nvarchar(1000))  AS qual_caso_critico,
        CAST(? AS nvarchar(max))   AS ultima_observacao,
        CAST(? AS nvarchar(30))    AS ultimo_formulario,
        CAST(? AS datetime2(0))    AS data_hora_modificacao
      ) AS s
   ON t.chave = s.chave
WHEN MATCHED AND s.data_contato >= t.data_contato THEN UPDATE SET
    cns                   = COALESCE(s.cns, t.cns),
    cpf                   = COALESCE(s.cpf, t.cpf),
    gestante              = COALESCE(s.gestante, t.gestante),
    enfermeira            = COALESCE(s.enfermeira, t.enfermeira),
    teleoperador          = COALESCE(s.teleoperador, t.teleoperador),
    classificacao         = COALESCE(s.classificacao, t.classificacao),
    conseguiu_contato     = COALESCE(s.conseguiu_contato, t.conseguiu_contato),
    data_contato          = s.data_contato,
    ig_semanas            = CASE WHEN s.ig_semanas IS NULL THEN t.ig_semanas ELSE s.ig_semanas END,
    ig_dias               = CASE WHEN s.ig_semanas IS NULL THEN t.ig_dias    ELSE s.ig_dias    END,
    data_retorno          = COALESCE(s.data_retorno, t.data_retorno),
    alto_risco            = COALESCE(s.alto_risco, t.alto_risco),
    caso_critico          = COALESCE(s.caso_critico, t.caso_critico),
    qual_caso_critico     = CASE WHEN s.caso_critico = N'Não' THEN NULL
                                 ELSE COALESCE(s.qual_caso_critico, t.qual_caso_critico) END,
    ultima_observacao     = COALESCE(s.ultima_observacao, t.ultima_observacao),
    ultimo_formulario     = s.ultimo_formulario,
    data_hora_modificacao = s.data_hora_modificacao
WHEN NOT MATCHED THEN INSERT
    (chave, cns, cpf, gestante, enfermeira, teleoperador, classificacao, conseguiu_contato,
     data_contato, ig_semanas, ig_dias, data_retorno, alto_risco, caso_critico,
     qual_caso_critico, ultima_observacao, ultimo_formulario, data_hora_modificacao)
VALUES
    (s.chave, s.cns, s.cpf, s.gestante, s.enfermeira, s.teleoperador, s.classificacao, s.conseguiu_contato,
     s.data_contato, s.ig_semanas, s.ig_dias, s.data_retorno, s.alto_risco, s.caso_critico,
     s.qual_caso_critico, s.ultima_observacao, s.ultimo_formulario, s.data_hora_modificacao);
"""

# ordem dos "?" do SQL_ATUAL
CAMPOS_ATUAL = [
    "chave", "cns", "cpf", "gestante", "enfermeira", "teleoperador", "classificacao", "conseguiu_contato",
    "data_contato", "ig_semanas", "ig_dias", "data_retorno", "alto_risco", "caso_critico",
    "qual_caso_critico", "ultima_observacao", "ultimo_formulario", "data_hora_modificacao",
]


def sql_adm(colunas):
    """INSERT do histórico. Os nomes das colunas vêm da lista fixa do programa
    (CAMPOS_ADM), nunca do que foi digitado; os VALORES vão sempre como parâmetro (?)."""
    nomes = ", ".join(f"[{c}]" for c in colunas)
    marcas = ", ".join("?" for _ in colunas)
    return f"INSERT INTO {TABELA_ADM} ({nomes}) VALUES ({marcas});"


def salvar(adm, atual):
    """adm: dicionário {coluna: valor} do histórico.
    atual: dicionário com os CAMPOS_ATUAL.
    Grava os dois numa transação só. Se der erro, desfaz tudo e repassa o erro."""
    conexao = pyodbc.connect(STRING_CONEXAO, timeout=TEMPO_CONEXAO, autocommit=False)
    try:
        cursor = conexao.cursor()
        colunas = list(adm)
        cursor.execute(sql_adm(colunas), [adm[c] for c in colunas])
        cursor.execute(SQL_ATUAL, [atual.get(c) for c in CAMPOS_ATUAL])
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
