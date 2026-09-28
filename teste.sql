SELECT
    COUNT(*)                                              AS total,
    SUM(CASE WHEN data_retorno IS NULL THEN 1 ELSE 0 END) AS sem_cadastro_gac12,
    SUM(alto_risco)                                       AS alto_risco,
    SUM(CASE WHEN DATEDIFF(day, data_contato, data_retorno) = 28 THEN 1 ELSE 0 END) AS retorno_28d,
    SUM(CASE WHEN DATEDIFF(day, data_contato, data_retorno) = 14 THEN 1 ELSE 0 END) AS retorno_14d,
    SUM(CASE WHEN DATEDIFF(day, data_contato, data_retorno) = 7  THEN 1 ELSE 0 END) AS retorno_7d
FROM dbo.vw_RetornoGestantes;