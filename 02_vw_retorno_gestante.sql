-- ============================================================
-- VIEW da tela principal: UMA linha por gestante (o atendimento mais recente).
-- A gestante é identificada pelo CNS; sem CNS, pelo CPF.
-- Sem CNS e sem CPF: aparece de qualquer jeito (todas as linhas).
-- Só LÊ as tabelas stg.*: nada é alterado nelas.
-- ============================================================
USE poc_gestante;
GO

CREATE OR ALTER VIEW dbo.vw_RetornoGestantes AS
WITH gac AS (
    SELECT
        cd_cns,
        dt_ultima_menstruacao,
        in_gestante_alto_risco,
        ROW_NUMBER() OVER (
            PARTITION BY cd_cns
            ORDER BY TRY_CONVERT(date, dt_acolhimento, 103) DESC
        ) AS ordem
    FROM stg.GestantesAcolhimento
),
atend AS (
    SELECT
        t.*,
        NULLIF(LTRIM(RTRIM(t.[Cartão SUS])), '') AS cns_limpo,
        c.cpf_limpo,
        COALESCE(NULLIF(LTRIM(RTRIM(t.[Cartão SUS])), ''), 'CPF ' + c.cpf_limpo) AS chave,
        ROW_NUMBER() OVER (
            PARTITION BY COALESCE(NULLIF(LTRIM(RTRIM(t.[Cartão SUS])), ''), 'CPF ' + c.cpf_limpo)
            ORDER BY TRY_CONVERT(date, t.[Data de Abertura], 101) DESC,
                     t.[Hora de Abertura] DESC
        ) AS ordem_atend
    FROM stg.TotalAtendimentos AS t
    -- CPF só com os números (tira pontos, traço e espaços)
    CROSS APPLY (SELECT NULLIF(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(t.[CPF])),
                        '.', ''), '-', ''), ' ', ''), '') AS cpf_limpo) AS c
),
base AS (
    SELECT
        a.[Profissional que abriu atendimento]          AS enfermeira,
        a.cns_limpo                                     AS cns,
        a.cpf_limpo                                     AS cpf,
        a.[Nome]                                        AS gestante,
        TRY_CONVERT(date, a.[Data de Abertura], 101)    AS data_contato,
        TRY_CONVERT(date, g.dt_ultima_menstruacao, 103) AS dum,
        g.in_gestante_alto_risco                        AS alto_risco
    FROM atend AS a
    LEFT JOIN gac AS g
           ON g.cd_cns = a.cns_limpo
          AND g.ordem = 1
    WHERE a.ordem_atend = 1          -- só o atendimento mais recente de cada gestante
       OR a.chave IS NULL            -- sem CNS e sem CPF: aparece de qualquer jeito
),
calc AS (
    SELECT *, DATEDIFF(day, dum, data_contato) AS ig_dias
    FROM base
)
SELECT
    enfermeira,
    cns,
    gestante,
    data_contato,
    ig_dias / 7 AS ig_semanas,
    ig_dias % 7 AS ig_dias_resto,
    CASE
        WHEN ig_dias IS NULL THEN NULL
        WHEN ig_dias < 196   THEN DATEADD(day, 28, data_contato)
        WHEN ig_dias < 238   THEN DATEADD(day, 14, data_contato)
        WHEN ig_dias < 273   THEN DATEADD(day,  7, data_contato)
        WHEN ig_dias < 287   THEN DATEADD(day,  3, data_contato)
        ELSE                      DATEADD(day,  1, data_contato)
    END AS data_retorno,
    CASE WHEN alto_risco = 'S' THEN 1 ELSE 0 END AS alto_risco,
    cpf                                          -- coluna nova (no fim)
FROM calc;
GO

-- Conferência: tem que dar 0 (nenhum CNS repetido)
SELECT COUNT(*) AS cns_repetidos
FROM (SELECT cns FROM dbo.vw_RetornoGestantes
      WHERE cns IS NOT NULL
      GROUP BY cns HAVING COUNT(*) > 1) AS x;
GO
