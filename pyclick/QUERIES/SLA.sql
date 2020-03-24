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

/*
SELECT	data_abertura_chamado
,		data_resolucao_chamado
,		id_chamado
,		chamado_pai
,		origem_chamado
,		usuario_afetado
,		nome_do_usuario_afetado
,		usuario_informante
,		nome_do_usuario_informante
,		organizacao_cliente
,		departamento_cliente
,		estado
,		site
,		fcr
,		status_de_evento
,		categoria_maior
,		resumo
,		servico_catalogo
,		classe_de_produto_de_servico
,		produto_de_servico
,		item_de_servico
,		categoria
,		oferta_catalogo
,		classe_generica_b
,		classe_de_produto_b
,		produto_b
,		fabricante_b
,		item_modelo_b
,		item_b
,		categoria_causa
,		classe_generica_causa
,		classe_de_produto_causa
,		produto_causa
,		fabricante_causa
,		item_modelo_causa
,		item_causa
,		replace(replace(resolucao, CHAR(13), '\r'), CHAR(10), '\n') as resolucao
,		id_acao
,		data_inicio_acao
,		ultima_acao
,		data_fim_acao
,		cast(tempo_total_da_acao_m as integer) as tempo_total_da_acao_m 
,		ultima_acao_nome
,		replace(replace(motivo_pendencia, CHAR(13), '\r'), CHAR(10), '\n') as motivo_pendencia
,		replace(replace(campos_alterados, CHAR(13), '\r'), CHAR(10), '\n') as campos_alterados 
,		replace(replace(itens_alterados, CHAR(13), '\r'), CHAR(10), '\n') as itens_alterados
,		nome_do_ca
,		contrato
,		mesa
,		designado
,		grupo_default
,		prioridade_do_ca
,		descricao_da_prioridade_do_ca
,		cast(prazo_prioridade_ans_m as integer) as prazo_prioridade_ans_m 
,		cast(prazo_prioridade_ano_m as integer) as prazo_prioridade_ano_m 
,		cast(prazo_prioridade_ca_m as integer) as prazo_prioridade_ca_m 
,		cast(tempo_total_evento_m as integer) as tempo_total_evento_m 
,		cast(tempo_util_evento_m as integer) as tempo_util_evento_m 
,		cast(tempo_util_atribuicao_mesa_m as integer) as tempo_util_atribuicao_mesa_m 
,		cast(tempo_util_atribuicao_ca_m as integer) as tempo_util_atribuicao_ca_m
,		vinculo
,		vinculo_com_incidente_grave
,		incidente_grave
,		tipo
,		ultima_mesa
,		peso
,		cast(soma_duracoes_chamado as integer) as soma_duracoes_chamado
,		cast(prazo as integer) as prazo
from	rel_medicao_stg 
order 	by id_chamado
, 		data_inicio_acao
, 		id_acao
*/