-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- INCIDENTES
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
WITH INCS AS (
	SELECT	DISTINCT ULTIMA_MESA AS MESA
	,		TIPO
	,		PESO
	,		ID_CHAMADO
	,		CHAMADO_PAI
	,		PRAZO
	,		SOMA_DURACOES_CHAMADO
	FROM	REL_MEDICAO_STG AS R
	WHERE	TIPO IN ('ORIENTAR', 'CORRIGIR', 'REALIZAR')
)
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- TAREFAS
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
, TASKS AS (
	SELECT	CHAMADO_PAI
	,		SUM(SOMA_DURACOES_CHAMADO) AS SOMA_DURACOES_CHAMADO
	FROM (
		SELECT	DISTINCT CHAMADO_PAI, SOMA_DURACOES_CHAMADO
		FROM	REL_MEDICAO_STG
		WHERE	TIPO = 'REALIZAR - TAREFA'
		AND		CHAMADO_PAI IS NOT NULL
		AND		PESO > 0
		ORDER	BY 1, 2
	) AS T
	GROUP	BY CHAMADO_PAI
),
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- DADOS AGREGADOS
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
DATA AS (
	SELECT	MESA
	,		TIPO
	,		PESO
	,		ID_CHAMADO
	,		PRAZO
	,		COALESCE((SELECT SUM(SOMA_DURACOES_CHAMADO) FROM TASKS WHERE CHAMADO_PAI = I.ID_CHAMADO), SOMA_DURACOES_CHAMADO) AS SOMA_DURACOES_CHAMADO
	,		CASE 	WHEN PESO = 0
					THEN 'N/A'
					WHEN COALESCE((SELECT SUM(SOMA_DURACOES_CHAMADO) FROM TASKS WHERE CHAMADO_PAI = I.ID_CHAMADO), SOMA_DURACOES_CHAMADO) >= PRAZO
					THEN 'S'
					ELSE 'N'
			END AS VIOLACAO_SLA
	FROM	INCS AS I
	ORDER	BY 1, 2, 3, 4
)
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- INDICADOR TRATADOS
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
SELECT	'INDICADOR TRATADOS' TIPO
,		NULL AS MESA
,		TIPO AS CATEGORIA
,		CASE WHEN PESO = 35 THEN 'S' ELSE 'N' END AS PESO_35
,		SUM(CASE WHEN PESO > 0 THEN 1 ELSE 0 END) AS TRATADOS
,		SUM(CASE WHEN PESO > 0 AND VIOLACAO_SLA = 'S' THEN 1 ELSE 0 END) AS VIOLACOES_SLA
,		100 - SUM(CASE WHEN PESO > 0 AND VIOLACAO_SLA = 'S' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN PESO > 0 THEN 1 ELSE 0 END)  AS INDICADOR
,		SUM(CASE WHEN PESO = 0 THEN 1 ELSE 0 END) AS ENCAMINHADOS
FROM	DATA
WHERE	MESA IN ( 
	'N4-SAP-SUSTENTACAO-ABAST_GE',
    'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',
    'N4-SAP-SUSTENTACAO-CORPORATIVO',
    'N4-SAP-SUSTENTACAO-ESCALADOS',
    'N4-SAP-SUSTENTACAO-FINANCAS',
    'N4-SAP-SUSTENTACAO-PRIORIDADE',
    'N4-SAP-SUSTENTACAO-SERVICOS',
    'N4-SAP-SUSTENTACAO-GRC',
    'N4-SAP-SUSTENTACAO-PORTAL'
)
GROUP	BY TIPO
, 		CASE WHEN PESO = 35 THEN 'S' ELSE 'N' END
--
UNION ALL
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- DETALHAMENTO MESA TRATADOS
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
SELECT	'DETALHAMENTO TRATADOS'
,		MESA
,		TIPO AS CATEGORIA
,		CASE WHEN PESO = 35 THEN 'S' ELSE 'N' END AS PESO_35
,		SUM(CASE WHEN PESO > 0 THEN 1 ELSE 0 END) AS TRATADOS
,		SUM(CASE WHEN PESO > 0 AND VIOLACAO_SLA = 'S' THEN 1 ELSE 0 END) AS VIOLACOES_SLA
,		100 - SUM(CASE WHEN PESO > 0 AND VIOLACAO_SLA = 'S' THEN 1 ELSE 0 END) * 100.0 / SUM(CASE WHEN PESO > 0 THEN 1 ELSE 0 END)  AS INDICADOR
,		SUM(CASE WHEN PESO = 0 THEN 1 ELSE 0 END) AS ENCAMINHADOS
FROM	DATA
WHERE	MESA IN ( 
	'N4-SAP-SUSTENTACAO-ABAST_GE',
    'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',
    'N4-SAP-SUSTENTACAO-CORPORATIVO',
    'N4-SAP-SUSTENTACAO-ESCALADOS',
    'N4-SAP-SUSTENTACAO-FINANCAS',
    'N4-SAP-SUSTENTACAO-PRIORIDADE',
    'N4-SAP-SUSTENTACAO-SERVICOS',
    'N4-SAP-SUSTENTACAO-GRC',
    'N4-SAP-SUSTENTACAO-PORTAL'
)
GROUP	BY MESA 
,		TIPO
, 		CASE WHEN PESO = 35 THEN 'S' ELSE 'N' END
--
UNION ALL
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- DETALHAMENTO MESA ENCAMINHADOS
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
SELECT	'DETALHAMENTO ENCAMINHADOS'
,		MESA
,		TIPO AS CATEGORIA
,		CASE WHEN PESO = 35 THEN 'S' ELSE 'N' END AS PESO_35
,		0
,		0
,		NULL  AS INDICADOR
,		SUM(CASE WHEN PESO = 0 THEN 1 ELSE 0 END) AS ENCAMINHADOS
FROM	DATA
WHERE	MESA NOT IN ( 
	'N4-SAP-SUSTENTACAO-ABAST_GE',
    'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',
    'N4-SAP-SUSTENTACAO-CORPORATIVO',
    'N4-SAP-SUSTENTACAO-ESCALADOS',
    'N4-SAP-SUSTENTACAO-FINANCAS',
    'N4-SAP-SUSTENTACAO-PRIORIDADE',
    'N4-SAP-SUSTENTACAO-SERVICOS',
    'N4-SAP-SUSTENTACAO-GRC',
    'N4-SAP-SUSTENTACAO-PORTAL'
)
GROUP	BY MESA 
,		TIPO
, 		CASE WHEN PESO = 35 THEN 'S' ELSE 'N' END


SELECT	DATA_ABERTURA_CHAMADO
,       DATA_RESOLUCAO_CHAMADO
,       ID_CHAMADO
,       CHAMADO_PAI
,       STATUS_DE_EVENTO
,       CATEGORIA_MAIOR
,       SERVICO_CATALOGO
,       CLASSE_DE_PRODUTO_DE_SERVICO
,       CATEGORIA
,       OFERTA_CATALOGO
,       PRODUTO_B
,       ITEM_B
,       CATEGORIA_CAUSA
,       PRODUTO_CAUSA
,       ID_ACAO
,       DATA_INICIO_ACAO
,       ULTIMA_ACAO
,       DATA_FIM_ACAO
,       ULTIMA_ACAO_NOME
,       NOME_DO_CA
,       CONTRATO
,       MESA
,       DESIGNADO
,       PRIORIDADE_DO_CA
,       CAST(PRAZO_PRIORIDADE_ANS_M AS INTEGER) AS PRAZO_PRIORIDADE_ANS_M 
,       CAST(PRAZO_PRIORIDADE_ANO_M AS INTEGER) AS PRAZO_PRIORIDADE_ANO_M 
,       CAST(PRAZO_PRIORIDADE_CA_M AS INTEGER) AS PRAZO_PRIORIDADE_CA_M 
,       CAST(TEMPO_TOTAL_EVENTO_M AS INTEGER) AS TEMPO_TOTAL_EVENTO_M 
,       CAST(TEMPO_UTIL_EVENTO_M AS INTEGER) AS TEMPO_UTIL_EVENTO_M 
,       CAST(TEMPO_UTIL_ATRIBUICAO_MESA_M AS INTEGER) AS TEMPO_UTIL_ATRIBUICAO_MESA_M 
,       CAST(TEMPO_UTIL_ATRIBUICAO_CA_M AS INTEGER) AS TEMPO_UTIL_ATRIBUICAO_CA_M 
,       VINCULO
,       VINCULO_COM_INCIDENTE_GRAVE
,       INCIDENTE_GRAVE
,       TIPO
,       ULTIMA_MESA
,       PESO
,       CAST(SOMA_DURACOES_CHAMADO AS INTEGER) AS SOMA_DURACOES_CHAMADO
,       PRAZO
FROM	REL_MEDICAO_STG 
ORDER 	BY ID_CHAMADO
, 		DATA_INICIO_ACAO
, 		ID_ACAO
