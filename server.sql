-- 1. Banco e schema (já criados; descomente só para recriar do zero)
-- CREATE DATABASE poc_gestante;
-- GO
USE poc_gestante;
GO
-- CREATE SCHEMA stg;
-- GO

/* ------------------------------------------------------------
   2. stg.TotalAtendimentos  (45 colunas | CSV vírgula, UTF-8, cabeçalho em 2 linhas)
   ------------------------------------------------------------ */
CREATE TABLE stg.TotalAtendimentos (
    [Código do Atendimento]                    varchar(250),
    [Nome]                                     varchar(250),
    [Data de Nascimento]                       varchar(250),
    [Idade]                                    varchar(250),
    [Nome da Mãe]                              varchar(250),
    [Raça]                                     varchar(250),
    [Sexo]                                     varchar(250),
    [Cartão SUS]                               varchar(250),
    [CPF]                                      varchar(250),
    [Unidade de Referência]                    varchar(250),
    [STS - Unidade de Referência]              varchar(250),
    [CRS - Unidade de Referência]              varchar(250),
    [Tipo do Atendimento]                      varchar(250),
    [Status]                                   varchar(250),
    [Motivo Encerramento]                      varchar(250),
    [Data de Abertura]                         varchar(250),
    [Unidade de Atendimento (Solicitante)]     varchar(250),
    [STS Solicitante]                          varchar(250),
    [CRS Solicitante]                          varchar(250),
    [Unidade de Encerramento]                  varchar(250),
    [Unidade ou Estabelecimento Encerramento]  varchar(250),
    [Unidade de Atendimento (Executante)]      varchar(250),
    [STS Executante]                           varchar(250),
    [CRS Executante]                           varchar(250),
    [Hora de Abertura]                         varchar(250),
    [Profissional que abriu atendimento]       varchar(250),
    [Conselho Abertura]                        varchar(250),
    [Número do Conselho Abertura]              varchar(250),
    [Especialidade Abertura]                   varchar(250),
    [Encaminhado para Teleinterconsulta]       varchar(250),
    [Data de Encerramento]                     varchar(250),
    [Hora de Encerramento]                     varchar(250),
    [Profissional que encerrou atendimento]    varchar(250),
    [Conselho Encerramento]                    varchar(250),
    [Número do Conselho Encerramento]          varchar(250),
    [Especialidade Encerramento]               varchar(250),
    [Profissional que assumiu atendimento]     varchar(250),
    [Conselho Edição]                          varchar(250),
    [Número do Conselho Edição]                varchar(250),
    [Especialidade Edição]                     varchar(250),
    [Código CIAP2]                             varchar(250),
    [Descrição CIAP2]                          varchar(250),
    [Código CID10]                             varchar(250),
    [Descrição CID10]                          varchar(250),
    [Nome da Unidade de Execução]              varchar(250)
);
GO

BULK INSERT stg.TotalAtendimentos
FROM 'C:\dados\total_atendimentos.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR   = '0x0d0a',
    CODEPAGE        = '65001',
    FIRSTROW        = 3,          -- linhas 1 e 2 são cabeçalho
    MAXERRORS       = 10,
    ERRORFILE       = 'C:\dados\erros_total.txt'
);
GO

/* ------------------------------------------------------------
   3. stg.Efetividade  (29 colunas | CSV vírgula com aspas, UTF-8)
   ------------------------------------------------------------ */
CREATE TABLE stg.Efetividade (
    [Carimbo de data/hora]                        varchar(250),
    [Classificação]                               varchar(250),
    [Nome]                                        varchar(250),
    [Conseguiu contato]                           varchar(250),
    [CNS]                                         varchar(250),
    [Número do contato]                           varchar(250),
    [Classificação Paciente]                      varchar(250),
    [Nasceu Vivo?]                                varchar(250),
    [Local do parto]                              varchar(250),
    [É um bebe de risco?]                         varchar(250),
    [Óbito neonatal]                              varchar(250),
    [Houve óbito materno?]                        varchar(250),
    [Sim/Não]                                     varchar(250),
    [Qual violência?]                             varchar(250),
    [Qual tipo de parto?]                         varchar(250),
    [É considerada uma gestante de alto risco?]   varchar(250),
    [Acompanhamento pré natal?]                   varchar(250),
    [Tratamento de sífilis?]                      varchar(250),
    [CNS Não Efetivo]                             varchar(250),
    [Número do contato Não Efetivo]               varchar(250),
    [Qual o motivo?]                              varchar(250),
    [Nome do tele operador]                       varchar(250),
    [Conseguiu contato? Tele]                     varchar(250),
    [CNS Tele Não Efetivo]                        varchar(250),
    [Número do telefone para contato]             varchar(250),
    [Motivo do não efetivo?]                      varchar(250),
    [CNS Tele Efetivo]                            varchar(250),
    [Número do telefone que conseguiu contato]    varchar(250),
    [Transferiu para qual enfermeira(o)]          varchar(250)
);
GO

BULK INSERT stg.Efetividade
FROM 'C:\dados\efetividade.csv'
WITH (
    FORMAT          = 'CSV',
    FIELDQUOTE      = '"',
    FIELDTERMINATOR = ',',
    ROWTERMINATOR   = '0x0d0a',
    CODEPAGE        = '65001',
    FIRSTROW        = 2,
    MAXERRORS       = 10,
    ERRORFILE       = 'C:\dados\erros_efetividade.txt'
);
GO

/* ------------------------------------------------------------
   4. stg.GestantesAcolhimento  (64 colunas | GAC12, ponto e vírgula, UTF-8)
      Arquivo preparado: 4 linhas de relatório removidas do topo.
   ------------------------------------------------------------ */
CREATE TABLE stg.GestantesAcolhimento (
    cd_cns varchar(250), nm_pessoa varchar(250), nm_mae varchar(250), nm_pai varchar(250),
    dt_nascimento varchar(250), idade_gestante varchar(250), nm_logradouro varchar(250),
    nr_logradouro varchar(250), dc_complemento varchar(250), cd_cep varchar(250),
    nm_bairro varchar(250), nr_telefone varchar(250), nr_celular varchar(250),
    dc_email varchar(250), cd_documento_identidade varchar(250), cd_municipio varchar(250),
    dc_municipio varchar(250), dc_ocupacao varchar(250), dc_raca varchar(250),
    dc_situacao_familiar varchar(250), dc_escolaridade varchar(250),
    cd_cmes_acolhimento varchar(250), cd_cnes_acolhimento varchar(250),
    nm_municipio_acolhimento varchar(250), cep_acolhimento varchar(250),
    nm_coordenadoria_regional_acolhimento varchar(250),
    nm_supervisao_tecnica_acolhimento varchar(250), nm_estabelecimento_acolhimento varchar(250),
    in_realiza_prenatal varchar(250), cd_cmes_acompanhamento varchar(250),
    cd_cnes_acompanhamento varchar(250), nm_municipio_acompanhamento varchar(250),
    cd_cep_acompanhamento varchar(250), nm_coordenadoria_regional_acompanhamento varchar(250),
    nm_supervisao_tecnica_acompanhamento varchar(250),
    nm_estabelecimento_acompanhamento varchar(250), cd_sisprenatal varchar(250),
    qt_gestacao varchar(250), qt_filho_nascido_vivo varchar(250), qt_filho_natimorto varchar(250),
    qt_parto_vaginal varchar(250), qt_parto_cesarea varchar(250), qt_aborto varchar(250),
    dt_inicio_acompanhamento varchar(250), dt_inclusao_origem varchar(250),
    in_interrupcao_gravidez varchar(250), dt_ultima_menstruacao varchar(250),
    dt_previsao_parto varchar(250), in_gestante_alto_risco varchar(250),
    nr_semana_decorrido_ingresso varchar(250), dc_condicao_saude varchar(250),
    dt_acolhimento varchar(250), dt_retorno_puerperal varchar(250), dt_parto varchar(250),
    in_primeira_dose_tetano varchar(250), in_segunda_dose_tetano varchar(250),
    in_reforco_vacina_tetano varchar(250), in_imune_tetano varchar(250),
    in_trabalha_fora_casa varchar(250), in_necessita_transporte_publico varchar(250),
    tp_bilhete_unico varchar(250), nr_bilhete_unico varchar(250),
    dt_entrega_bilhete varchar(250), in_situacao_usuaria varchar(250)
);
GO

BULK INSERT stg.GestantesAcolhimento
FROM 'C:\dados\GAC12.csv'
WITH (
    FORMAT          = 'CSV',       -- 3 linhas têm nm_pai entre aspas
    FIELDQUOTE      = '"',
    FIELDTERMINATOR = ';',
    ROWTERMINATOR   = '0x0d0a',
    CODEPAGE        = '65001',
    FIRSTROW        = 2,
    LASTROW         = 25055,       -- ignora a linha vazia no fim do arquivo
    MAXERRORS       = 10,
    ERRORFILE       = 'C:\dados\erros_gac12.txt'
);
GO

/* ------------------------------------------------------------
   5. Conferência
   ------------------------------------------------------------ */
SELECT 'TotalAtendimentos'    AS tabela, COUNT(*) AS linhas FROM stg.TotalAtendimentos
UNION ALL
SELECT 'Efetividade',                    COUNT(*)           FROM stg.Efetividade
UNION ALL
SELECT 'GestantesAcolhimento',           COUNT(*)           FROM stg.GestantesAcolhimento;
GO