-- DROP TABLE PARAMS
CREATE TABLE PARAMS(
	PARAM							TEXT
,	VALOR							TEXT
,	OBS								TEXT
,	PRIMARY KEY(PARAM ASC)
);

-- DROP TABLE INCIDENTES
CREATE TABLE INCIDENTES(
	ID_CHAMADO						TEXT
,	DATA_ABERTURA_CHAMADO			TEXT
,	DATA_RESOLUCAO_CHAMADO			TEXT
,	CHAMADO_PAI						TEXT
,	FCR								TEXT
,	STATUS_DE_EVENTO				TEXT
,	CATEGORIA_MAIOR					TEXT
,	CATEGORIA						TEXT
,	SERVICO_CATALOGO				TEXT
,	OFERTA_CATALOGO					TEXT
,	PRAZO_OFERTA_M					INTEGER
,	RESUMO							TEXT
,	PRAZO_PRIORIDADE_ANS_M			INTEGER
,	TEMPO_TOTAL_EVENTO_M			INTEGER
,	TEMPO_UTIL_EVENTO_M				INTEGER
,	VINCULO							TEXT
,	VINCULO_COM_INCIDENTE_GRAVE		TEXT
,	INCIDENTE_GRAVE					TEXT
,	PRIMARY KEY(ID_CHAMADO ASC)
);

-- DROP TABLE INCIDENTE_SOLICITANTES 
CREATE TABLE INCIDENTE_SOLICITANTES (
	ID_CHAMADO						TEXT
,	ORIGEM_CHAMADO					TEXT
,	USUARIO_AFETADO					TEXT
,	NOME_DO_USUARIO_AFETADO			TEXT
,	USUARIO_INFORMANTE				TEXT
,	NOME_DO_USUARIO_INFORMANTE		TEXT
,	ORGANIZACAO_CLIENTE				TEXT
,	DEPARTAMENTO_CLIENTE			TEXT
,	ESTADO							TEXT
,	SITE							TEXT
,	PRIMARY KEY(ID_CHAMADO ASC)
);

-- DROP TABLE INCIDENTE_ITENS_SERVICO
CREATE TABLE INCIDENTE_ITENS_SERVICO(
	ID_CHAMADO						TEXT
,	CLASSE_DE_PRODUTO_DE_SERVICO	TEXT
,	PRODUTO_DE_SERVICO				TEXT
,	ITEM_DE_SERVICO					TEXT
,	PRIMARY KEY(ID_CHAMADO ASC)
);

-- DROP TABLE INCIDENTE_ITENS_B
CREATE TABLE INCIDENTE_ITENS_B(
	ID_CHAMADO						TEXT
,	CLASSE_GENERICA_B				TEXT
,	CLASSE_DE_PRODUTO_B				TEXT
,	PRODUTO_B						TEXT
,	FABRICANTE_B					TEXT
,	ITEM_MODELO_B					TEXT
,	ITEM_B							TEXT
,	PRIMARY KEY(ID_CHAMADO ASC)
);

-- DROP TABLE INCIDENTE_ITENS_CAUSA
CREATE TABLE INCIDENTE_ITENS_CAUSA(
	ID_CHAMADO						TEXT
,	CATEGORIA_CAUSA					TEXT
,	CLASSE_GENERICA_CAUSA			TEXT
,	CLASSE_DE_PRODUTO_CAUSA			TEXT
,	PRODUTO_CAUSA					TEXT
,	FABRICANTE_CAUSA				TEXT
,	ITEM_MODELO_CAUSA				TEXT
,	ITEM_CAUSA						TEXT
,	PRIMARY KEY(ID_CHAMADO ASC)
);

-- DROP TABLE INCIDENTE_ACOES
CREATE TABLE INCIDENTE_ACOES(
	ID_CHAMADO						TEXT
,	ID_ACAO							INTEGER
,	RESOLUCAO						TEXT
,	ULTIMA_ACAO_NOME				TEXT
,	USER_STATUS						TEXT
,	PENDENCIA						TEXT
,	DATA_INICIO_ACAO				TEXT
,	DATA_FIM_ACAO					TEXT
,	DURACAO_M						INTEGER
,	ULTIMA_ACAO						TEXT
,	TEMPO_TOTAL_DA_ACAO_M			INTEGER
,	MOTIVO_PENDENCIA				TEXT
,	CAMPOS_ALTERADOS				TEXT
,	ITENS_ALTERADOS					TEXT
,	NOME_DO_CA						TEXT
,	DESCRICAO_DA_PRIORIDADE_DO_CA	TEXT
,	PRIORIDADE_DO_CA				TEXT
,	CONTRATO						TEXT
,	MESA							TEXT
,	MESA_ATUAL						TEXT
,	DESIGNADO						TEXT
,	GRUPO_DEFAULT					TEXT
,	PRAZO_PRIORIDADE_ANO_M			INTEGER
,	PRAZO_PRIORIDADE_CA_M			INTEGER
,	TEMPO_UTIL_ATRIBUICAO_MESA_M	INTEGER
,	TEMPO_UTIL_ATRIBUICAO_CA_M		INTEGER
,	PRIMARY KEY(ID_CHAMADO ASC, ID_ACAO ASC)
);

-- DROP TABLE IF EXISTS HORAS_UTEIS;
CREATE TABLE HORAS_UTEIS(
	MESA							TEXT
,	HORA_INICIO						TEXT
,	HORA_FIM						TEXT
,	PRIMARY KEY(MESA ASC, HORA_INICIO ASC, HORA_FIM ASC)
);

INSERT INTO INCIDENTES(
	ID_CHAMADO
,	DATA_ABERTURA_CHAMADO
,	DATA_RESOLUCAO_CHAMADO
,	CHAMADO_PAI
,	FCR
,	STATUS_DE_EVENTO
,	CATEGORIA_MAIOR
,	CATEGORIA
,	SERVICO_CATALOGO
,	OFERTA_CATALOGO
,	PRAZO_OFERTA_M
,	RESUMO
,	PRAZO_PRIORIDADE_ANS_M
,	TEMPO_TOTAL_EVENTO_M
,	TEMPO_UTIL_EVENTO_M
,	VINCULO
,	VINCULO_COM_INCIDENTE_GRAVE
,	INCIDENTE_GRAVE
)
SELECT	ID_CHAMADO
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
WHERE	ID_ACAO IN (
			SELECT 	MAX(ID_ACAO)
			FROM	REL_MEDICAO
			GROUP	BY ID_CHAMADO
);

INSERT INTO INCIDENTE_SOLICITANTES (
	ID_CHAMADO
,	ORIGEM_CHAMADO
,	USUARIO_AFETADO
,	NOME_DO_USUARIO_AFETADO
,	USUARIO_INFORMANTE
,	NOME_DO_USUARIO_INFORMANTE
,	ORGANIZACAO_CLIENTE
,	DEPARTAMENTO_CLIENTE
,	ESTADO
,	SITE
)
SELECT	ID_CHAMADO
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
WHERE	ID_ACAO IN (
			SELECT 	MAX(ID_ACAO)
			FROM	REL_MEDICAO
			GROUP	BY ID_CHAMADO
);

INSERT INTO INCIDENTE_ITENS_SERVICO(
	ID_CHAMADO
,	CLASSE_DE_PRODUTO_DE_SERVICO
,	PRODUTO_DE_SERVICO
,	ITEM_DE_SERVICO
)
SELECT	ID_CHAMADO
,		CLASSE_DE_PRODUTO_DE_SERVICO
,		PRODUTO_DE_SERVICO
,		ITEM_DE_SERVICO
FROM	REL_MEDICAO
WHERE	ID_ACAO IN (
			SELECT 	MAX(ID_ACAO)
			FROM	REL_MEDICAO
			GROUP	BY ID_CHAMADO
);

INSERT INTO INCIDENTE_ITENS_B(
	ID_CHAMADO
,	CLASSE_GENERICA_B
,	CLASSE_DE_PRODUTO_B
,	PRODUTO_B
,	FABRICANTE_B
,	ITEM_MODELO_B
,	ITEM_B
)
SELECT	ID_CHAMADO
,		CLASSE_GENERICA_B
,		CLASSE_DE_PRODUTO_B
,		PRODUTO_B
,		FABRICANTE_B
,		ITEM_MODELO_B
,		ITEM_B
FROM	REL_MEDICAO
WHERE	ID_ACAO IN (
			SELECT 	MAX(ID_ACAO)
			FROM	REL_MEDICAO
			GROUP	BY ID_CHAMADO
);

INSERT INTO INCIDENTE_ITENS_CAUSA(
	ID_CHAMADO
,	CATEGORIA_CAUSA
,	CLASSE_GENERICA_CAUSA
,	CLASSE_DE_PRODUTO_CAUSA
,	PRODUTO_CAUSA
,	FABRICANTE_CAUSA
,	ITEM_MODELO_CAUSA
,	ITEM_CAUSA
)
SELECT	ID_CHAMADO
,		CATEGORIA_CAUSA
,		CLASSE_GENERICA_CAUSA
,		CLASSE_DE_PRODUTO_CAUSA
,		PRODUTO_CAUSA
,		FABRICANTE_CAUSA
,		ITEM_MODELO_CAUSA
,		ITEM_CAUSA
FROM	REL_MEDICAO
WHERE	ID_ACAO IN (
			SELECT 	MAX(ID_ACAO)
			FROM	REL_MEDICAO
			GROUP	BY ID_CHAMADO
);

INSERT INTO INCIDENTE_ACOES(
	ID_CHAMADO
,	ID_ACAO
,	RESOLUCAO
,	ULTIMA_ACAO_NOME
,	USER_STATUS
,	PENDENCIA
,	DATA_INICIO_ACAO
,	DATA_FIM_ACAO
,	DURACAO_M
,	ULTIMA_ACAO
,	TEMPO_TOTAL_DA_ACAO_M
,	MOTIVO_PENDENCIA
,	CAMPOS_ALTERADOS
,	ITENS_ALTERADOS
,	NOME_DO_CA
,	DESCRICAO_DA_PRIORIDADE_DO_CA
,	PRIORIDADE_DO_CA
,	CONTRATO
,	MESA
,	MESA_ATUAL
,	DESIGNADO
,	GRUPO_DEFAULT
,	PRAZO_PRIORIDADE_ANO_M
,	PRAZO_PRIORIDADE_CA_M
,	TEMPO_UTIL_ATRIBUICAO_MESA_M
,	TEMPO_UTIL_ATRIBUICAO_CA_M
)
SELECT	ID_CHAMADO
,		ID_ACAO
,		RESOLUCAO
,		ULTIMA_ACAO_NOME
,		USER_STATUS
,		PENDENCIA
,		DATA_INICIO_ACAO
,		DATA_FIM_ACAO
,		DURACAO_M
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
,		MESA_ATUAL
,		DESIGNADO
,		GRUPO_DEFAULT
,		PRAZO_PRIORIDADE_ANO_M
,		PRAZO_PRIORIDADE_CA_M
,		TEMPO_UTIL_ATRIBUICAO_MESA_M
,		TEMPO_UTIL_ATRIBUICAO_CA_M
FROM	REL_MEDICAO
ORDER	BY ID_CHAMADO
,		ID_ACAO;

-- QUERY CONFERÊNCIA
-- DROP VIEW VW_REL_MEDICAO
CREATE VIEW VW_REL_MEDICAO AS 
	SELECT	A.ID_CHAMADO
	,		A.DATA_ABERTURA_CHAMADO
	,		A.DATA_RESOLUCAO_CHAMADO
	,		A.CHAMADO_PAI
	,		B.ORIGEM_CHAMADO
	,		B.USUARIO_AFETADO
	,		B.NOME_DO_USUARIO_AFETADO
	,		B.USUARIO_INFORMANTE
	,		B.NOME_DO_USUARIO_INFORMANTE
	,		B.ORGANIZACAO_CLIENTE
	,		B.DEPARTAMENTO_CLIENTE
	,		B.ESTADO
	,		B.SITE
	,		A.FCR
	,		A.STATUS_DE_EVENTO
	,		A.CATEGORIA_MAIOR
	,		A.RESUMO
	,		A.SERVICO_CATALOGO
	,		C.CLASSE_DE_PRODUTO_DE_SERVICO
	,		C.PRODUTO_DE_SERVICO
	,		C.ITEM_DE_SERVICO
	,		A.CATEGORIA
	,		A.OFERTA_CATALOGO
	,		A.PRAZO_OFERTA_M
	,		D.CLASSE_GENERICA_B
	,		D.CLASSE_DE_PRODUTO_B
	,		D.PRODUTO_B
	,		D.FABRICANTE_B
	,		D.ITEM_MODELO_B
	,		D.ITEM_B
	,		E.CATEGORIA_CAUSA
	,		E.CLASSE_GENERICA_CAUSA
	,		E.CLASSE_DE_PRODUTO_CAUSA
	,		E.PRODUTO_CAUSA
	,		E.FABRICANTE_CAUSA
	,		E.ITEM_MODELO_CAUSA
	,		E.ITEM_CAUSA
	,		F.RESOLUCAO
	,		F.ID_ACAO
	,		F.DATA_INICIO_ACAO
	,		F.ULTIMA_ACAO
	,		F.DATA_FIM_ACAO
	,		F.DURACAO_M
	,		F.TEMPO_TOTAL_DA_ACAO_M
	,		F.ULTIMA_ACAO_NOME
	,		F.USER_STATUS
	,		F.PENDENCIA
	,		F.MOTIVO_PENDENCIA
	,		F.CAMPOS_ALTERADOS
	,		F.ITENS_ALTERADOS
	,		F.NOME_DO_CA
	,		F.CONTRATO
	,		F.MESA
	,		F.MESA_ATUAL
	,		F.DESIGNADO
	,		F.GRUPO_DEFAULT
	,		F.PRIORIDADE_DO_CA
	,		F.DESCRICAO_DA_PRIORIDADE_DO_CA
	,		A.PRAZO_PRIORIDADE_ANS_M
	,		F.PRAZO_PRIORIDADE_ANO_M
	,		F.PRAZO_PRIORIDADE_CA_M
	,		A.TEMPO_TOTAL_EVENTO_M
	,		A.TEMPO_UTIL_EVENTO_M
	,		F.TEMPO_UTIL_ATRIBUICAO_MESA_M
	,		F.TEMPO_UTIL_ATRIBUICAO_CA_M
	,		A.VINCULO
	,		A.VINCULO_COM_INCIDENTE_GRAVE
	,		A.INCIDENTE_GRAVE
	FROM	INCIDENTES AS A
			--
			INNER JOIN INCIDENTE_SOLICITANTES AS B
			ON A.ID_CHAMADO = B.ID_CHAMADO
			--
			INNER JOIN INCIDENTE_ITENS_SERVICO AS C
			ON A.ID_CHAMADO = C.ID_CHAMADO
			--
			INNER JOIN INCIDENTE_ITENS_B AS D
			ON A.ID_CHAMADO = D.ID_CHAMADO
			--
			INNER JOIN INCIDENTE_ITENS_CAUSA E
			ON A.ID_CHAMADO = E.ID_CHAMADO
			--
			INNER JOIN INCIDENTE_ACOES AS F
			ON A.ID_CHAMADO = F.ID_CHAMADO
			--
	ORDER	BY A.ID_CHAMADO
	,		A.CHAMADO_PAI
	,		F.DATA_INICIO_ACAO
	,		F.ID_ACAO
	,		A.STATUS_DE_EVENTO;

-- DROP VIEW VW_HORAS_UTEIS_ACOES;	
CREATE VIEW VW_HORAS_UTEIS_ACOES AS
	WITH ACOES AS (
		SELECT	A.ID_CHAMADO
		,		A.ID_ACAO
		,		A.MESA_ATUAL
		,		A.PENDENCIA
		,		A.DATA_INICIO_ACAO AS DATA_ACAO
		,		COALESCE(
					LEAD(A.DATA_INICIO_ACAO) OVER (PARTITION BY A.ID_CHAMADO ORDER BY A.ID_ACAO)
				,	B.VALOR
				) AS PROX_DATA_ACAO
		FROM	INCIDENTE_ACOES AS A
				--
				INNER JOIN PARAMS AS B
				ON	B.PARAM = 'HORA_FIM_APURACAO'
				--
		ORDER	BY A.ID_CHAMADO
		,		A.ID_ACAO
	)
	SELECT	B.ID_CHAMADO
	,		B.ID_ACAO
	,		B.DATA_ACAO
	,		B.PROX_DATA_ACAO
	,		ROW_NUMBER() OVER (
				PARTITION BY B.ID_CHAMADO, B.ID_ACAO
				ORDER BY MAX(A.HORA_INICIO, B.DATA_ACAO)
			) AS ORDEM	
	,		B.MESA_ATUAL AS MESA
	,		B.PENDENCIA
	,		MAX(A.HORA_INICIO, B.DATA_ACAO) AS INICIO
	,		MIN(A.HORA_FIM, B.PROX_DATA_ACAO) AS FIM
	,		ROUND( 24.0 * 60 * (JULIANDAY( MIN( A.HORA_FIM, B.PROX_DATA_ACAO)) - JULIANDAY(MAX( A.HORA_INICIO, B.DATA_ACAO )) )) AS DURACAO_M
	FROM	HORAS_UTEIS AS A
			--
			INNER JOIN ACOES AS B
			-- HTTPS://STACKOVERFLOW.COM/QUESTIONS/325933/DETERMINE-WHETHER-TWO-DATE-RANGES-OVERLAP
			-- (STARTA <= ENDB) AND (ENDA >= STARTB)
			ON	A.MESA = B.MESA_ATUAL
			AND	B.DATA_ACAO <> B.PROX_DATA_ACAO
			AND	A.HORA_INICIO <= B.PROX_DATA_ACAO
			AND	A.HORA_FIM >= B.DATA_ACAO
			--
	ORDER	BY B.ID_CHAMADO
	,		B.ID_ACAO;
