-- ============================================================
-- MIGRAÇÃO das tabelas do app (schema "app") para aceitar gestante SEM CNS (só CPF).
-- Mexe SÓ nas tabelas app.* (que são do app). dbo.* e stg.* não são tocadas.
-- Pode rodar mais de uma vez: cada passo confere se já foi feito.
-- Rode DEPOIS do 03_tabelas_app.sql (quem já rodou o 03 antigo precisa deste).
-- ============================================================
USE poc_gestante;
GO

/* 1. Histórico: CNS passa a aceitar vazio e ganha a coluna CPF (nada é apagado) */
IF COL_LENGTH('app.Monitora_Gestante_Adm', 'cpf') IS NULL
    ALTER TABLE app.Monitora_Gestante_Adm ADD cpf varchar(11) NULL;
GO
ALTER TABLE app.Monitora_Gestante_Adm ALTER COLUMN cns varchar(15) NULL;
GO

/* 2. Situação atual: a chave deixa de ser só o CNS.
      A tabela antiga é guardada com outro nome (_v1) e os dados são copiados. */
IF COL_LENGTH('app.Gestante_Atual', 'chave') IS NULL
   AND OBJECT_ID('app.Gestante_Atual_v1', 'U') IS NULL
BEGIN
    EXEC sp_rename 'app.Gestante_Atual', 'Gestante_Atual_v1';
END
GO

IF OBJECT_ID('app.Gestante_Atual', 'U') IS NULL
CREATE TABLE app.Gestante_Atual (
    chave                  varchar(20)    NOT NULL PRIMARY KEY,  -- o CNS; sem CNS: 'CPF ' + CPF
    cns                    varchar(15)    NULL,
    cpf                    varchar(11)    NULL,
    gestante               nvarchar(255)  NULL,
    enfermeira             nvarchar(255)  NULL,
    teleoperador           nvarchar(50)   NULL,
    classificacao          nvarchar(20)   NULL,
    conseguiu_contato      nvarchar(3)    NULL,
    data_contato           date           NOT NULL,
    ig_semanas             tinyint        NULL,
    ig_dias                tinyint        NULL,
    data_retorno           date           NULL,
    alto_risco             bit            NULL,
    caso_critico           nvarchar(3)    NULL,
    qual_caso_critico      nvarchar(1000) NULL,
    ultima_observacao      nvarchar(max)  NULL,
    ultimo_formulario      nvarchar(30)   NOT NULL,
    data_hora_modificacao  datetime2(0)   NOT NULL
);
GO

/* 3. Copia o que já estava na tabela antiga (a chave é o próprio CNS) */
IF OBJECT_ID('app.Gestante_Atual_v1', 'U') IS NOT NULL
   AND NOT EXISTS (SELECT 1 FROM app.Gestante_Atual)
INSERT INTO app.Gestante_Atual
    (chave, cns, cpf, gestante, enfermeira, teleoperador, classificacao, conseguiu_contato,
     data_contato, ig_semanas, ig_dias, data_retorno, alto_risco, caso_critico,
     qual_caso_critico, ultima_observacao, ultimo_formulario, data_hora_modificacao)
SELECT
     cns, cns, NULL, gestante, enfermeira, teleoperador, classificacao, conseguiu_contato,
     data_contato, ig_semanas, ig_dias, data_retorno, alto_risco, caso_critico,
     qual_caso_critico, ultima_observacao, ultimo_formulario, data_hora_modificacao
FROM app.Gestante_Atual_v1;
GO

/* Conferência: as colunas novas têm que aparecer */
SELECT TABLE_NAME, COLUMN_NAME, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'app' AND COLUMN_NAME IN ('chave', 'cns', 'cpf')
ORDER BY TABLE_NAME, COLUMN_NAME;
GO
