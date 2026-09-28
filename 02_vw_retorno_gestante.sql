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
base AS (
    SELECT
        t.[Profissional que abriu atendimento]          AS enfermeira,
        t.[Cartão SUS]                                  AS cns,
        t.[Nome]                                        AS gestante,
        TRY_CONVERT(date, t.[Data de Abertura], 101)    AS data_contato,
        TRY_CONVERT(date, g.dt_ultima_menstruacao, 103) AS dum,
        g.in_gestante_alto_risco                        AS alto_risco
    FROM stg.TotalAtendimentos AS t
    LEFT JOIN gac AS g
           ON g.cd_cns = t.[Cartão SUS]
          AND g.ordem = 1
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
    CASE WHEN alto_risco = 'S' THEN 1 ELSE 0 END AS alto_risco
FROM calc;
GO