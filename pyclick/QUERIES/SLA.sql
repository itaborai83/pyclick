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
	AND		DATA_RESOLUCAO_CHAMADO IS NOT NULL
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
		AND		DATA_RESOLUCAO_CHAMADO IS NOT NULL
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