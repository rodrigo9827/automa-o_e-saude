-- ============================================================
-- Horas da Busca Ativa no histórico do app (schema "app").
--   busca_hora_inicio : hora em que a enfermeira clicou em "Registrar Busca Ativa"
--   busca_hora_envio  : hora em que clicou em "Enviar"
-- Mexe SÓ na tabela app.Monitora_Gestante_Adm (nada é apagado; as linhas antigas ficam com NULL).
-- Pode rodar mais de uma vez: cada passo confere se já foi feito.
-- Rode DEPOIS do 03 e do 04.
-- ============================================================
USE poc_gestante;
GO

IF COL_LENGTH('app.Monitora_Gestante_Adm', 'busca_hora_inicio') IS NULL
    ALTER TABLE app.Monitora_Gestante_Adm ADD busca_hora_inicio datetime2(0) NULL;
GO
IF COL_LENGTH('app.Monitora_Gestante_Adm', 'busca_hora_envio') IS NULL
    ALTER TABLE app.Monitora_Gestante_Adm ADD busca_hora_envio datetime2(0) NULL;
GO

-- Conferência: as duas colunas novas têm que aparecer
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'app' AND TABLE_NAME = 'Monitora_Gestante_Adm'
  AND COLUMN_NAME IN ('busca_hora_inicio', 'busca_hora_envio');
GO
