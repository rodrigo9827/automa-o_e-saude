-- ============================================================
-- TABELAS NOVAS DO APP (schema "app")
-- Não altera NENHUMA tabela existente (dbo.* e stg.* continuam iguais).
-- Pode rodar mais de uma vez: só cria o que ainda não existe.
--
-- app.Monitora_Gestante_Adm : histórico (ADM). Cada envio vira UMA linha nova,
--                              com data e hora. Nunca é alterada nem apagada.
-- app.Gestante_Atual        : tabela do usuário final. UMA linha por gestante (CNS ou CPF),
--                              sempre com a informação mais recente.
-- ============================================================
USE poc_gestante;
GO

IF SCHEMA_ID('app') IS NULL
    EXEC('CREATE SCHEMA app');
GO

/* ------------------------------------------------------------
   1. Histórico administrativo (mesmas colunas do stg.Monitora_Gestante_Adm.csv)
   ------------------------------------------------------------ */
IF OBJECT_ID('app.Monitora_Gestante_Adm', 'U') IS NULL
CREATE TABLE app.Monitora_Gestante_Adm (
    id                     bigint IDENTITY(1,1) PRIMARY KEY,
    data_hora_modificacao  datetime2(0)   NOT NULL,
    formulario             nvarchar(30)   NOT NULL,   -- 'Finalizar Atendimento' ou 'Busca Ativa'
    enfermeira             nvarchar(255)  NULL,
    teleoperador           nvarchar(50)   NULL,
    gestante               nvarchar(255)  NULL,
    cns                    varchar(15)    NULL,       -- vazio quando a gestante não tem CNS
    data_contato           date           NULL,
    numero                 nvarchar(50)   NULL,
    conseguiu_contato      nvarchar(3)    NULL,
    motivo_sem_contato     nvarchar(100)  NULL,
    classificacao          nvarchar(20)   NULL,
    tratamento_sifilis     nvarchar(3)    NULL,
    gestante_risco         nvarchar(3)    NULL,
    pre_natal              nvarchar(3)    NULL,
    nasceu_vivo            nvarchar(3)    NULL,
    local_parto            nvarchar(255)  NULL,
    outro_local            nvarchar(500)  NULL,
    bebe_risco             nvarchar(3)    NULL,
    obito_neonatal         nvarchar(3)    NULL,
    obito_materno          nvarchar(3)    NULL,
    houve_violencia        nvarchar(3)    NULL,
    tipo_violencia         nvarchar(50)   NULL,
    tipo_parto             nvarchar(50)   NULL,
    risco_gestacional      nvarchar(3)    NULL,
    qual_risco             nvarchar(500)  NULL,
    ig_semanas             nvarchar(10)   NULL,       -- formato ss+dd, igual ao CSV
    data_retorno           date           NULL,
    alto_risco             nvarchar(3)    NULL,
    caso_critico           nvarchar(3)    NULL,
    qual_caso_critico      nvarchar(1000) NULL,
    observacoes            nvarchar(max)  NULL,
    gestante_puerpera      nvarchar(3)    NULL,
    gestante_aborto        nvarchar(3)    NULL,
    gestante_gestante      nvarchar(3)    NULL,
    cpf                    varchar(11)    NULL
);
GO

/* ------------------------------------------------------------
   2. Tabela do usuário final: situação ATUAL de cada gestante
   ------------------------------------------------------------ */
IF OBJECT_ID('app.Gestante_Atual', 'U') IS NULL
CREATE TABLE app.Gestante_Atual (
    chave                  varchar(20)    NOT NULL PRIMARY KEY,  -- o CNS; sem CNS: 'CPF ' + CPF
    cns                    varchar(15)    NULL,
    cpf                    varchar(11)    NULL,
    gestante               nvarchar(255)  NULL,
    enfermeira             nvarchar(255)  NULL,
    teleoperador           nvarchar(50)   NULL,
    classificacao          nvarchar(20)   NULL,       -- Gestante / Puérpera / Aborto
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

-- Conferência: as duas tabelas têm que aparecer
SELECT s.name AS [schema], t.name AS tabela
FROM sys.tables AS t
JOIN sys.schemas AS s ON s.schema_id = t.schema_id
WHERE s.name = 'app';
GO
