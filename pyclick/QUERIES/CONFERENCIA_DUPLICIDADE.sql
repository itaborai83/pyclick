-- CONFERÊNCIA DUPLICIDADE DE INCIDENTES
WITH DADOS AS (
	SELECT	DISTINCT ID_CHAMADO
	,		DATA_ABERTURA_CHAMADO
	,		DATA_RESOLUCAO_CHAMADO
	,		CHAMADO_PAI
	,		FCR
	,		STATUS_DE_EVENTO
	,		CATEGORIA_MAIOR
	,		CATEGORIA
	,		SERVICO_CATALOGO
	,		OFERTA_CATALOGO
	,		PRAZO_OFERTA_M
	,		RESUMO
	,		PRAZO_PRIORIDADE_ANS_M
	,		TEMPO_TOTAL_EVENTO_M
	,		TEMPO_UTIL_EVENTO_M
	,		VINCULO
	,		VINCULO_COM_INCIDENTE_GRAVE
	,		INCIDENTE_GRAVE
	FROM	REL_MEDICAO
)
SELECT	ID_CHAMADO
FROM	DADOS
GROUP	BY ID_CHAMADO 	
HAVING	COUNT(*) > 1;

-- CONFERÊNCIA DUPLICIDADE USUÁRIO AFETADO
WITH DADOS AS (
	SELECT	DISTINCT ID_CHAMADO
	,		ORIGEM_CHAMADO
	,		USUARIO_AFETADO
	,		NOME_DO_USUARIO_AFETADO
	,		USUARIO_INFORMANTE
	,		NOME_DO_USUARIO_INFORMANTE
	,		ORGANIZACAO_CLIENTE
	,		DEPARTAMENTO_CLIENTE
	,		ESTADO
	,		SITE
	FROM	REL_MEDICAO
)
SELECT	ID_CHAMADO
FROM	DADOS
GROUP	BY ID_CHAMADO
HAVING	COUNT(*) > 1;

-- CONFERÊNCIA DUPLICIDADE ITENS SERVIÇO
WITH DADOS AS (
	SELECT	DISTINCT ID_CHAMADO
	,		CLASSE_DE_PRODUTO_DE_SERVICO
	,		PRODUTO_DE_SERVICO
	,		ITEM_DE_SERVICO
	FROM	REL_MEDICAO
)
SELECT	ID_CHAMADO
FROM	DADOS
GROUP	BY ID_CHAMADO
HAVING	COUNT(*) > 1;


-- CONFERÊNCIA DUPLICIDADE DE ITEM B
WITH DADOS AS (
	SELECT	DISTINCT ID_CHAMADO
	,		CLASSE_GENERICA_B
	,		CLASSE_DE_PRODUTO_B
	,		PRODUTO_B
	,		FABRICANTE_B
	,		ITEM_MODELO_B
	,		ITEM_B
	FROM	REL_MEDICAO
)
SELECT	ID_CHAMADO
FROM	DADOS
GROUP	BY ID_CHAMADO
HAVING	COUNT(*) > 1;

-- CONFERÊNCIA DUPLICIDADE DE ITEM CAUSA
WITH DADOS AS (
	SELECT	DISTINCT ID_CHAMADO
	,		CATEGORIA_CAUSA
	,		CLASSE_GENERICA_CAUSA
	,		CLASSE_DE_PRODUTO_CAUSA
	,		PRODUTO_CAUSA
	,		FABRICANTE_CAUSA
	,		ITEM_MODELO_CAUSA
	,		ITEM_CAUSA
	FROM	REL_MEDICAO
)
SELECT	ID_CHAMADO
FROM	DADOS
GROUP	BY ID_CHAMADO
HAVING	COUNT(*) > 1;

-- CONFERÊNCIA DUPLICIDADE AÇÕES
WITH DADOS AS (
	SELECT	DISTINCT ID_CHAMADO
	,		ID_ACAO
	,		RESOLUCAO
	,		ULTIMA_ACAO_NOME
	,		DATA_INICIO_ACAO
	,		DATA_FIM_ACAO
	,		ULTIMA_ACAO
	,		TEMPO_TOTAL_DA_ACAO_M
	,		MOTIVO_PENDENCIA
	,		CAMPOS_ALTERADOS
	,		ITENS_ALTERADOS
	,		NOME_DO_CA
	,		DESCRICAO_DA_PRIORIDADE_DO_CA
	,		PRIORIDADE_DO_CA
	,		CONTRATO
	,		MESA
	,		DESIGNADO
	,		GRUPO_DEFAULT
	,		PRAZO_PRIORIDADE_ANO_M
	,		PRAZO_PRIORIDADE_CA_M
	,		TEMPO_UTIL_ATRIBUICAO_MESA_M
	,		TEMPO_UTIL_ATRIBUICAO_CA_M
	FROM	REL_MEDICAO
)
SELECT	ID_CHAMADO
,		ID_ACAO
FROM	DADOS
GROUP	BY ID_CHAMADO
,		ID_ACAO
HAVING	COUNT(*) > 1;