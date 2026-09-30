SELECT
    COUNT(*)                                                  AS total,
    SUM(CASE WHEN cns IS NOT NULL THEN 1 ELSE 0 END)          AS com_cns,
    SUM(CASE WHEN cns IS NULL AND cpf IS NOT NULL THEN 1 ELSE 0 END) AS so_cpf,
    SUM(CASE WHEN cns IS NULL AND cpf IS NULL THEN 1 ELSE 0 END)     AS sem_nada
FROM dbo.vw_RetornoGestantes;