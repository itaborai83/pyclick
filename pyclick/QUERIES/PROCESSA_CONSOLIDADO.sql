DROP TABLE IF EXISTS INCIDENTES_OVERRIDE;
CREATE TABLE INCIDENTES_OVERRIDE(
	ID_CHAMADO						TEXT
,	STATUS							TEXT
,	CATEGORIA						TEXT
,	MESA							TEXT
,	PESO							INTEGER
,	PRAZO							INTEGER
,	DURACAO							INTEGER
,	ESTORNO							TEXT
,	OBSERVACAO						TEXT
,	PRIMARY KEY(ID_CHAMADO ASC)
);

DROP TABLE IF EXISTS INDICADORES;
CREATE TABLE INDICADORES(
	INDICADOR						TEXT
,	ORDEM							INTEGER
,	VALOR							REAL
,	OBSERVACAO						TEXT
,	PRIMARY KEY(INDICADOR ASC)
);

DROP TABLE IF EXISTS MESAS_N4_SAP;
CREATE TABLE MESAS_N4_SAP(
	MESA							TEXT
,	ABREV							TEXT
,	PESO_DEFAULT					INTEGER
,	CONSIDERA_ULTIMA				TEXT
,	PRIMARY KEY(MESA ASC)
);

INSERT INTO MESAS_N4_SAP(MESA, ABREV, PESO_DEFAULT, CONSIDERA_ULTIMA) VALUES ('N4-SAP-SUSTENTACAO-ABAST_GE', 		'ABGE',  1, 'S');
INSERT INTO MESAS_N4_SAP(MESA, ABREV, PESO_DEFAULT, CONSIDERA_ULTIMA) VALUES ('N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	'APOP',  1, 'S');
INSERT INTO MESAS_N4_SAP(MESA, ABREV, PESO_DEFAULT, CONSIDERA_ULTIMA) VALUES ('N4-SAP-SUSTENTACAO-CORPORATIVO',  	'CORP',  1, 'S');
INSERT INTO MESAS_N4_SAP(MESA, ABREV, PESO_DEFAULT, CONSIDERA_ULTIMA) VALUES ('N4-SAP-SUSTENTACAO-FINANCAS', 		'FIN',   1, 'S');
INSERT INTO MESAS_N4_SAP(MESA, ABREV, PESO_DEFAULT, CONSIDERA_ULTIMA) VALUES ('N4-SAP-SUSTENTACAO-GRC', 			'GRC',   1, 'S');
INSERT INTO MESAS_N4_SAP(MESA, ABREV, PESO_DEFAULT, CONSIDERA_ULTIMA) VALUES ('N4-SAP-SUSTENTACAO-PORTAL', 			'PORT',  1, 'S');
INSERT INTO MESAS_N4_SAP(MESA, ABREV, PESO_DEFAULT, CONSIDERA_ULTIMA) VALUES ('N4-SAP-SUSTENTACAO-SERVICOS', 		'SERV',  1, 'S');
INSERT INTO MESAS_N4_SAP(MESA, ABREV, PESO_DEFAULT, CONSIDERA_ULTIMA) VALUES ('N4-SAP-SUSTENTACAO-ESCALADOS', 		'ESCL', 30, 'N');
INSERT INTO MESAS_N4_SAP(MESA, ABREV, PESO_DEFAULT, CONSIDERA_ULTIMA) VALUES ('N4-SAP-SUSTENTACAO-PRIORIDADE', 		'PRIO', 35, 'N');

DROP VIEW IF EXISTS VW_ULTIMAS_MESAS;
CREATE VIEW VW_ULTIMAS_MESAS AS 
	WITH ULTIMAS_ATRIBUICOES AS (
		SELECT	ID_CHAMADO
		,		MAX(ID_ACAO+0) as MAX_ID_ACAO
		FROM	INCIDENTE_ACOES ia 
		WHERE	ULTIMA_ACAO_NOME = 'Atribuição interna'
		AND		ID_CHAMADO NOT LIKE 'T%'
		AND		MESA NOT IN ('A DEFINIR', 'Atendimento de RH', 'Mesa Padrão', 'SVD Manager Template', 'Usuários Finais')
		GROUP	BY ID_CHAMADO
	)
	SELECT	A.ID_CHAMADO
	,		COALESCE(D.MESA, C.MESA) AS MESA
	,		CASE WHEN E.MESA IS NOT NULL THEN 'S' ELSE 'N' END AS MESA_CONTRATO
	FROM	INCIDENTES AS A
			--
			LEFT OUTER JOIN ULTIMAS_ATRIBUICOES AS B
			ON 	A.ID_CHAMADO = B.ID_CHAMADO
			--
			LEFT OUTER JOIN INCIDENTE_ACOES AS C
			ON	B.ID_CHAMADO = C.ID_CHAMADO
			AND	B.MAX_ID_ACAO = C.ID_ACAO
			--
			LEFT OUTER JOIN INCIDENTES_OVERRIDE AS D
			ON	A.ID_CHAMADO = D.ID_CHAMADO
			--
			LEFT OUTER JOIN MESAS_N4_SAP AS E
			ON	COALESCE(D.MESA, C.MESA) = E.MESA
			--
	WHERE	A.CATEGORIA_MAIOR <> 'Demandas Internas'
	AND		A.ID_CHAMADO NOT LIKE 'T%'
	AND		(D.ID_CHAMADO IS NULL OR (D.ID_CHAMADO IS NOT NULL AND COALESCE(D.ESTORNO, 'N') <> 'S' ))
	ORDER	BY A.ID_CHAMADO;

DROP VIEW IF EXISTS VW_STATUS_CHAMADO;
CREATE VIEW VW_STATUS_CHAMADO AS
	SELECT	A.ID_CHAMADO 
	,		COALESCE(D.STATUS, 
				CASE	WHEN C.MESA NOT IN (SELECT MESA FROM MESAS_N4_SAP) THEN 'ENCAMINHADO'
						WHEN B.DATA_RESOLUCAO_CHAMADO IS NULL THEN 'EM ABERTO'
						WHEN A.ULTIMA_ACAO_NOME IN ('Encerrado', 'Encerrar') THEN 'ENCERRADO'
						WHEN A.ULTIMA_ACAO_NOME IN ('Cancelado', 'Cancelar') THEN 'CANCELADO'
						WHEN A.ULTIMA_ACAO_NOME IN ('Resolver') THEN 'RESOLVIDO'
						ELSE NULL
				END 
			)AS STATUS		
	FROM	INCIDENTE_ACOES AS A
			--
			INNER JOIN INCIDENTES AS B
			ON	A.ID_CHAMADO = B.ID_CHAMADO
			--
			LEFT OUTER JOIN VW_ULTIMAS_MESAS AS C
			ON	A.ID_CHAMADO = C.ID_CHAMADO
			--
			LEFT OUTER JOIN INCIDENTES_OVERRIDE AS D
			ON 	B.ID_CHAMADO = D.ID_CHAMADO
			AND	(D.ESTORNO IS NULL OR D.ESTORNO <> 'S')
			--
	WHERE	A.ID_ACAO IN ( SELECT MAX(ID_ACAO+0) AS MAX_ID_ACAO FROM INCIDENTE_ACOES GROUP BY ID_CHAMADO )
	AND		B.CATEGORIA_MAIOR <> 'Demandas Internas'
	AND		B.ID_CHAMADO NOT LIKE 'T%'
	ORDER 	BY A.ID_CHAMADO;
		
DROP VIEW IF EXISTS VW_PESOS;
CREATE VIEW VW_PESOS AS
	SELECT	A.ID_CHAMADO
	,		B.MESA
	,		CASE	WHEN B.MESA IS NULL THEN NULL
					ELSE COALESCE(C.PESO, D.PESO_DEFAULT, 0)
			END AS PESO
	FROM	INCIDENTES AS A
			--
			LEFT OUTER JOIN VW_ULTIMAS_MESAS AS B
			ON 	A.ID_CHAMADO = B.ID_CHAMADO
			--
			LEFT OUTER JOIN INCIDENTES_OVERRIDE AS C
			ON	A.ID_CHAMADO = C.ID_CHAMADO
			--
			LEFT OUTER JOIN MESAS_N4_SAP AS D
			ON	COALESCE(C.MESA, B.MESA) = D.MESA
			--
	WHERE	A.CATEGORIA_MAIOR <> 'Demandas Internas'
	AND		A.ID_CHAMADO NOT LIKE 'T%'
	AND		(C.ID_CHAMADO IS NULL OR (C.ID_CHAMADO IS NOT NULL AND COALESCE(C.ESTORNO, 'N') <> 'S' ))
	ORDER	BY A.ID_CHAMADO;
	
DROP VIEW IF EXISTS VW_CATEGORIAS;
CREATE VIEW VW_CATEGORIAS AS
	SELECT	DISTINCT A.ID_CHAMADO
	,		COALESCE(B.CATEGORIA, 
				CASE	WHEN A.CATEGORIA_MAIOR = 'Solicitações de Serviço'
						THEN 'REALIZAR'
						WHEN A.CATEGORIA_MAIOR = 'Incidentes' AND A.CATEGORIA LIKE '%CORRIGIR%'
						THEN 'CORRIGIR'
						WHEN A.CATEGORIA_MAIOR = 'Incidentes'
						THEN 'ORIENTAR'
						ELSE NULL
		 		END 
		 	) AS CATEGORIA
	FROM	INCIDENTES AS A
			--
			LEFT OUTER JOIN INCIDENTES_OVERRIDE AS B
			ON	A.ID_CHAMADO = B.ID_CHAMADO
			--
	WHERE	A.CATEGORIA_MAIOR NOT IN ('Tarefa', 'Demandas Internas')
	AND		(B.ID_CHAMADO IS NULL OR (B.ID_CHAMADO IS NOT NULL AND COALESCE(B.ESTORNO, 'N') <> 'S' ))
	ORDER	BY A.ID_CHAMADO;

DROP VIEW IF EXISTS VW_PRAZOS;
CREATE VIEW VW_PRAZOS AS 
	SELECT	A.ID_CHAMADO
	,		C.CATEGORIA
	,		B.PESO
	,		COALESCE(D.PRAZO, 
				CASE 	WHEN COALESCE(D.PESO, B.PESO) IS NULL THEN NULL
						WHEN COALESCE(D.CATEGORIA, C.CATEGORIA) IS NULL THEN NULL
						WHEN COALESCE(D.PESO, B.PESO) = 0 THEN -999999
						WHEN COALESCE(D.PESO, B.PESO) IN (1, 30) AND COALESCE(C.CATEGORIA, D.CATEGORIA) = 'ORIENTAR' THEN 27 * 60
						WHEN COALESCE(D.PESO, B.PESO) IN (1, 30) AND COALESCE(C.CATEGORIA, D.CATEGORIA) = 'CORRIGIR' THEN 135 * 60
						WHEN COALESCE(D.PESO, B.PESO) = 35 THEN 9 * 60
						WHEN COALESCE(D.CATEGORIA, C.CATEGORIA) = 'REALIZAR' THEN A.PRAZO_OFERTA_M
				END
			)AS PRAZO
	,		A.OFERTA_CATALOGO 
	FROM	INCIDENTES AS A
			--
			LEFT OUTER JOIN VW_PESOS AS B
			ON	A.ID_CHAMADO = B.ID_CHAMADO
			--
			LEFT OUTER JOIN VW_CATEGORIAS AS C
			ON A.ID_CHAMADO = C.ID_CHAMADO 
			--
			LEFT OUTER JOIN INCIDENTES_OVERRIDE AS D
			ON	A.ID_CHAMADO = D.ID_CHAMADO
			--
	WHERE	A.CATEGORIA_MAIOR <> 'Demandas Internas'
	AND		A.ID_CHAMADO NOT LIKE 'T%'
	AND		(D.ID_CHAMADO IS NULL OR (D.ID_CHAMADO IS NOT NULL AND COALESCE(D.ESTORNO, 'N') <> 'S' ))
	ORDER 	BY A.ID_CHAMADO;
	
DROP VIEW IF EXISTS VW_DURACOES;
CREATE VIEW VW_DURACOES AS 
	WITH SOMAS AS (
		SELECT	A.ID_CHAMADO
		,		A.CHAMADO_PAI 
		,		SUM(CASE	WHEN B.MESA = 'N4-SAP-SUSTENTACAO-PRIORIDADE'
							THEN (CASE WHEN C.MESA = 'N4-SAP-SUSTENTACAO-PRIORIDADE' THEN C.TEMPO_UTIL_ATRIBUICAO_MESA_M ELSE 0 END)
							WHEN (B.MESA IN (SELECT MESA FROM MESAS_N4_SAP) OR B.MESA IS NULL)  
							THEN C.TEMPO_UTIL_ATRIBUICAO_MESA_M 
							ELSE 0 
				END) AS DURACAO
		,		SUM(CASE	WHEN B.MESA = 'N4-SAP-SUSTENTACAO-PRIORIDADE'
							THEN (CASE WHEN C.MESA = 'N4-SAP-SUSTENTACAO-PRIORIDADE' THEN 1 ELSE 0 END)
							WHEN (B.MESA IN (SELECT MESA FROM MESAS_N4_SAP) OR B.MESA IS NULL) THEN 1 
							ELSE 0 
				END) AS QTD				
		FROM	INCIDENTES AS A
				--
				INNER JOIN VW_ULTIMAS_MESAS AS B
				ON 	A.ID_CHAMADO = B.ID_CHAMADO 
				AND (B.MESA_CONTRATO = 'S' OR B.MESA IS NULL)
				--
				INNER JOIN INCIDENTE_ACOES AS C
				ON	A.ID_CHAMADO = C.ID_CHAMADO
				--
		WHERE	C.MESA IN (SELECT MESA FROM MESAS_N4_SAP)
		AND 	C.ULTIMA_ACAO_NOME = 'Atribuição interna'
		AND		C.TEMPO_UTIL_ATRIBUICAO_MESA_M IS NOT NULL
		AND		A.CATEGORIA_MAIOR <> 'Demandas Internas'
		GROUP	BY A.ID_CHAMADO
		,		A.CHAMADO_PAI
	),
	SOMAS_TAREFAS AS (
		SELECT 	CHAMADO_PAI AS ID_CHAMADO
		,		SUM(DURACAO) AS DURACAO
		FROM 	SOMAS 
		WHERE 	CHAMADO_PAI IS NOT NULL
		AND		ID_CHAMADO LIKE 'T%'
		GROUP	BY CHAMADO_PAI
	),
	DURACOES AS (
		SELECT	A.ID_CHAMADO
		--,		SUM(B.DURACAO + COALESCE( (SELECT DURACAO FROM SOMAS_TAREFAS WHERE ID_CHAMADO = A.ID_CHAMADO), 0)) AS DURACAO
		,		SUM(COALESCE( 
						(SELECT DURACAO FROM SOMAS_TAREFAS WHERE ID_CHAMADO = A.ID_CHAMADO),  -- SOMA AS TAREFAS SE EXISTIREM
						B.DURACAO)) AS DURACAO -- CASO NÃO, SOMA OS TEMPOS DO PRÓPRIO INCIDENTE
		FROM	INCIDENTES AS A
				--
				LEFT OUTER JOIN SOMAS AS B
				ON	A.ID_cHAMADO = B.ID_CHAMADO
				--
		WHERE	A.CATEGORIA_MAIOR NOT IN ('Demandas Internas', 'Tarefa')
		GROUP	BY A.ID_CHAMADO
		ORDER	BY A.ID_CHAMADO
	)
	SELECT	A.ID_CHAMADO
	,		COALESCE(B.DURACAO, A.DURACAO) AS DURACAO
	FROM	
			DURACOES AS A
			--
			LEFT OUTER JOIN INCIDENTES_OVERRIDE AS B
			ON 	A.ID_CHAMADO = B.ID_CHAMADO
			--
	WHERE	A.ID_CHAMADO NOT LIKE 'T%'
	AND		(B.ID_CHAMADO IS NULL OR (B.ID_CHAMADO IS NOT NULL AND COALESCE(B.ESTORNO, 'N') <> 'S' ))
	ORDER	BY A.ID_CHAMADO;
	
DROP VIEW IF EXISTS VW_DADOS_MEDICAO; 
CREATE VIEW VW_DADOS_MEDICAO AS 
	SELECT	A.ID_CHAMADO
	,		B.STATUS
	,		C.CATEGORIA 
	,		D.MESA
	,		E.PESO
	,		F.PRAZO
	,		G.DURACAO
	,		H.OBSERVACAO AS OBS_OVERRIDE
	FROM	INCIDENTES AS A
			--
			LEFT OUTER JOIN VW_STATUS_CHAMADO AS B NOT INDEXED
			ON 	A.ID_CHAMADO = B.ID_CHAMADO
			--
			LEFT OUTER JOIN VW_CATEGORIAS AS C NOT INDEXED
			ON	A.ID_CHAMADO = C.ID_CHAMADO
			--
			LEFT OUTER JOIN VW_ULTIMAS_MESAS AS D NOT INDEXED
			ON 	A.ID_CHAMADO = D.ID_CHAMADO
			--
			LEFT OUTER JOIN VW_PESOS AS E NOT INDEXED
			ON	A.ID_CHAMADO = E.ID_CHAMADO
			--
			LEFT OUTER JOIN VW_PRAZOS AS F NOT INDEXED
			ON	A.ID_CHAMADO = F.ID_CHAMADO
			--
			LEFT OUTER JOIN VW_DURACOES AS G NOT INDEXED
			ON	A.ID_CHAMADO = G.ID_CHAMADO
			--
			LEFT OUTER JOIN INCIDENTES_OVERRIDE AS H
			ON A.ID_CHAMADO = H.ID_CHAMADO
			--
	WHERE	A.ID_CHAMADO NOT LIKE 'T%'
	AND		A.ID_CHAMADO NOT IN (SELECT ID_CHAMADO FROM INCIDENTES_OVERRIDE WHERE ESTORNO = 'S');
	
DROP VIEW IF EXISTS VW_DADOS_MEDICAO_FALTANDO;
CREATE VIEW VW_DADOS_MEDICAO_FALTANDO AS 
	SELECT	*
	FROM	VW_DADOS_MEDICAO AS A
	WHERE	A.ID_CHAMADO NOT IN (SELECT ID_CHAMADO FROM INCIDENTES_OVERRIDE WHERE ESTORNO = 'S')	
	-- OS PREDICADOS 1=1 SÃO USADOS PARA PERMITIR DESLIGAR OS PREDICADOS MANUALMENTE SETANDO-OS COMO 1=0 PARA ANÁLISE
	AND		((1=1 AND A.MESA IS NULL)
	OR		    ((1=1 AND A.MESA IN (SELECT MESA FROM MESAS_N4_SAP) 
	AND		        ((1=1 AND A.STATUS IS NULL)
	OR		         (1=1 AND A.PESO IS NULL)
	OR		         (1=1 AND A.CATEGORIA IS NULL)
	OR		         (1=1 AND A.PESO IS NULL)
	OR		         (1=1 AND A.STATUS <> 'EM ABERTO' AND PRAZO IS NULL)
	OR		         (1=1 AND A.STATUS NOT IN ('EM ABERTO', 'CANCELADO') AND DURACAO IS NULL)))))
	ORDER	BY A.ID_CHAMADO;
	
DROP VIEW IF EXISTS VW_KPI_PRP_DETALHES;
CREATE VIEW VW_KPI_PRP_DETALHES AS
	SELECT 	*
	FROM	VW_DADOS_MEDICAO
	WHERE	MESA IN (SELECT MESA FROM MESAS_N4_SAP)
	AND		STATUS IN ('ENCERRADO', 'RESOLVIDO', 'CANCELADO')
	AND		PESO = 35
	AND		DURACAO IS NOT NULL
	AND		PRAZO IS NOT NULL;

DROP VIEW IF EXISTS VW_KPI_PRP;
CREATE VIEW VW_KPI_PRP AS
	SELECT	COUNT(*) AS INCIDENTES
	,		SUM(CASE WHEN STATUS = 'ENCERRADO' THEN 1 ELSE 0 END) AS ENCERRADOS
	,		SUM(CASE WHEN STATUS = 'RESOLVIDO' THEN 1 ELSE 0 END) AS RESOLVIDOS
	,		SUM(CASE WHEN STATUS = 'CANCELADO' THEN 1 ELSE 0 END) AS CANCELADOS
	,		SUM(CASE WHEN DURACAO > PRAZO THEN 1.0 ELSE 0.0 END) AS VIOLACOES
	,		(SUM(CASE WHEN DURACAO > PRAZO THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100.0 AS PRP 
	FROM	VW_KPI_PRP_DETALHES;
	
DROP VIEW IF EXISTS VW_KPI_PRO_DETALHES;
CREATE VIEW VW_KPI_PRO_DETALHES AS
	WITH DADOS_MEDICAO AS (
		SELECT	*
		FROM	VW_DADOS_MEDICAO
		WHERE	CATEGORIA = 'ORIENTAR'
		AND		PESO < 35
		AND		STATUS IS NOT NULL
		AND		STATUS <> 'EM ABERTO'
	),
	DADOS_MEDICAO_PESO35 AS (
		SELECT	*
		FROM	VW_DADOS_MEDICAO
		WHERE	CATEGORIA = 'ORIENTAR'
		AND		PESO = 35
		AND		STATUS IS NOT NULL
		AND		STATUS <> 'EM ABERTO'
	)
	SELECT	A.*
	,		CASE WHEN DURACAO > PRAZO THEN 1 ELSE 0 END AS VIOLACAO
	,		CASE WHEN STATUS = 'ENCERRADO' THEN 1 ELSE 0 END AS ENCERRADO
	,		CASE WHEN STATUS = 'RESOLVIDO' THEN 1 ELSE 0 END  AS RESOLVIDO
	,		CASE WHEN STATUS = 'CANCELADO' THEN 1 ELSE 0 END  AS CANCELADO
	,		0 AS ENCAMINHADO
	,		0 AS PRIORIZADO
	FROM	DADOS_MEDICAO AS A
	WHERE	1=1
	AND		A.STATUS IN ('ENCERRADO', 'RESOLVIDO', 'CANCELADO')
	AND		A.PRAZO IS NOT NULL
	AND		A.DURACAO IS NOT NULL
	--
	UNION	
	--
	SELECT	A.*
	,		0 AS VIOLACAO
	,		CASE WHEN STATUS = 'ENCERRADO' THEN 1 ELSE 0 END AS ENCERRADO
	,		CASE WHEN STATUS = 'RESOLVIDO' THEN 1 ELSE 0 END  AS RESOLVIDO
	,		CASE WHEN STATUS = 'CANCELADO' THEN 1 ELSE 0 END  AS CANCELADO
	,		0 AS ENCAMINHADO
	,		0 AS PRIORIZADO
	FROM	DADOS_MEDICAO AS A
	WHERE	1=1
	AND		A.STATUS IN ('ENCERRADO', 'RESOLVIDO', 'CANCELADO')
	AND		(A.PRAZO IS NULL OR A.DURACAO IS NULL) -- cálculo impossível
	--
	UNION	
	--
	SELECT	A.*
	,		0 AS VIOLACAO
	,		0 AS ENCERRADO
	,		0 AS RESOLVIDO
	,		0 AS CANCELADO
	,		1 AS ENCAMINHADO
	,		0 AS PRIORIZADO
	FROM	DADOS_MEDICAO AS A
	WHERE	1=1
	AND		A.STATUS = 'ENCAMINHADO'
	--
	UNION	
	--
	SELECT	A.*
	,		0 AS VIOLACAO
	,		0 AS ENCERRADO
	,		0 AS RESOLVIDO
	,		0 AS CANCELADO
	,		0 AS ENCAMINHADO
	,		1 AS PRIORIZADO
	FROM	DADOS_MEDICAO_PESO35 AS A
	WHERE	1=1
	--
	ORDER	BY ID_CHAMADO;

DROP VIEW IF EXISTS VW_KPI_PRO;
CREATE VIEW VW_KPI_PRO AS
	SELECT	COUNT(*) AS INCIDENTES
	,		SUM(ENCERRADO) AS ENCERRADOS
	,		SUM(RESOLVIDO) AS RESOLVIDOS
	,		SUM(CANCELADO) AS CANCELADOS
	,		SUM(ENCAMINHADO) AS ENCAMINHADOS
	,		SUM(PRIORIZADO) AS PRIORIZADOS
	,		SUM(VIOLACAO) AS VIOLACOES
	,		100.0 * (SUM(VIOLACAO) / COUNT(*))  AS PRO
	FROM	VW_KPI_PRO_DETALHES;
	
DROP VIEW IF EXISTS VW_KPI_PRC_DETALHES;
CREATE VIEW VW_KPI_PRC_DETALHES AS
	WITH DADOS_MEDICAO AS (
		SELECT	*
		FROM	VW_DADOS_MEDICAO
		WHERE	CATEGORIA = 'CORRIGIR'
		AND		PESO < 35
		AND		STATUS IS NOT NULL
		AND		STATUS <> 'EM ABERTO'
	),
	DADOS_MEDICAO_PESO35 AS (
		SELECT	*
		FROM	VW_DADOS_MEDICAO
		WHERE	CATEGORIA = 'CORRIGIR'
		AND		PESO = 35
		AND		STATUS IS NOT NULL
		AND		STATUS <> 'EM ABERTO'
	)
	SELECT	A.*
	,		CASE WHEN DURACAO > PRAZO THEN 1 ELSE 0 END AS VIOLACAO
	,		CASE WHEN STATUS = 'ENCERRADO' THEN 1 ELSE 0 END AS ENCERRADO
	,		CASE WHEN STATUS = 'RESOLVIDO' THEN 1 ELSE 0 END  AS RESOLVIDO
	,		CASE WHEN STATUS = 'CANCELADO' THEN 1 ELSE 0 END  AS CANCELADO
	,		0 AS ENCAMINHADO
	,		0 AS PRIORIZADO
	FROM	DADOS_MEDICAO AS A
	WHERE	1=1
	AND		A.STATUS IN ('ENCERRADO', 'RESOLVIDO', 'CANCELADO')
	AND		A.PRAZO IS NOT NULL
	AND		A.DURACAO IS NOT NULL
	--
	UNION	
	--
	SELECT	A.*
	,		0 AS VIOLACAO
	,		CASE WHEN STATUS = 'ENCERRADO' THEN 1 ELSE 0 END AS ENCERRADO
	,		CASE WHEN STATUS = 'RESOLVIDO' THEN 1 ELSE 0 END  AS RESOLVIDO
	,		CASE WHEN STATUS = 'CANCELADO' THEN 1 ELSE 0 END  AS CANCELADO
	,		0 AS ENCAMINHADO
	,		0 AS PRIORIZADO
	FROM	DADOS_MEDICAO AS A
	WHERE	1=1
	AND		A.STATUS IN ('ENCERRADO', 'RESOLVIDO', 'CANCELADO')
	AND		(A.PRAZO IS NULL OR A.DURACAO IS NULL) -- cálculo impossível
	--
	UNION	
	--
	SELECT	A.*
	,		0 AS VIOLACAO
	,		0 AS ENCERRADO
	,		0 AS RESOLVIDO
	,		0 AS CANCELADO
	,		1 AS ENCAMINHADO
	,		0 AS PRIORIZADO
	FROM	DADOS_MEDICAO AS A
	WHERE	1=1
	AND		A.STATUS = 'ENCAMINHADO'
	--
	UNION	
	--
	SELECT	A.*
	,		0 AS VIOLACAO
	,		0 AS ENCERRADO
	,		0 AS RESOLVIDO
	,		0 AS CANCELADO
	,		0 AS ENCAMINHADO
	,		1 AS PRIORIZADO
	FROM	DADOS_MEDICAO_PESO35 AS A
	WHERE	1=1
	--
	ORDER	BY ID_CHAMADO;

DROP VIEW IF EXISTS VW_KPI_PRC;
CREATE VIEW VW_KPI_PRC AS
	SELECT	COUNT(*) AS INCIDENTES
	,		SUM(ENCERRADO) AS ENCERRADOS
	,		SUM(RESOLVIDO) AS RESOLVIDOS
	,		SUM(CANCELADO) AS CANCELADOS
	,		SUM(ENCAMINHADO) AS ENCAMINHADOS
	,		SUM(PRIORIZADO) AS PRIORIZADOS
	,		SUM(VIOLACAO) AS VIOLACOES
	,		100.0 * (SUM(VIOLACAO) / COUNT(*))  AS PRC
	FROM	VW_KPI_PRC_DETALHES;

DROP VIEW IF EXISTS VW_KPI_PRS_DETALHES;
CREATE VIEW VW_KPI_PRS_DETALHES AS
	WITH DADOS_MEDICAO AS (
		SELECT	A.*
		,		CASE	WHEN MESA NOT IN (SELECT MESA FROM MESAS_N4_SAP) THEN 'OUTROS'
						WHEN PRAZO < 0 OR PRAZO IS NULL THEN 'OUTROS'
						WHEN PRAZO <= 45 * 60 THEN 'SIMPLES'
						WHEN PRAZO <= 90 * 60 THEN 'MEDIO'
						WHEN PRAZO <= 180 * 60 THEN 'COMPLEXO'
						ELSE 'OUTROS'
				END AS COMPLEXIDADE
		FROM	VW_DADOS_MEDICAO AS A
		WHERE	A.CATEGORIA = 'REALIZAR'
		AND		A.PESO < 35
		AND		A.STATUS IS NOT NULL
		AND		A.STATUS <> 'EM ABERTO'
	),
	DADOS_MEDICAO_PESO35 AS (
		SELECT	A.*
		,		'OUTROS' AS COMPLEXIDADE
		FROM	VW_DADOS_MEDICAO AS a
		WHERE	A.CATEGORIA = 'REALIZAR'
		AND		A.PESO = 35
		AND		A.STATUS IS NOT NULL
		AND		A.STATUS <> 'EM ABERTO'
	)
	SELECT	A.*
	,		CASE WHEN DURACAO > PRAZO THEN 1 ELSE 0 END AS VIOLACAO
	,		CASE WHEN STATUS = 'ENCERRADO' THEN 1 ELSE 0 END AS ENCERRADO
	,		CASE WHEN STATUS = 'RESOLVIDO' THEN 1 ELSE 0 END  AS RESOLVIDO
	,		CASE WHEN STATUS = 'CANCELADO' THEN 1 ELSE 0 END  AS CANCELADO
	,		0 AS ENCAMINHADO
	,		0 AS PRIORIZADO
	FROM	DADOS_MEDICAO AS A
	WHERE	1=1
	AND		A.STATUS IN ('ENCERRADO', 'RESOLVIDO', 'CANCELADO')
	AND		A.PRAZO IS NOT NULL
	AND		A.DURACAO IS NOT NULL
	--
	UNION	
	--
	SELECT	A.*
	,		0 AS VIOLACAO
	,		CASE WHEN STATUS = 'ENCERRADO' THEN 1 ELSE 0 END AS ENCERRADO
	,		CASE WHEN STATUS = 'RESOLVIDO' THEN 1 ELSE 0 END  AS RESOLVIDO
	,		CASE WHEN STATUS = 'CANCELADO' THEN 1 ELSE 0 END  AS CANCELADO
	,		0 AS ENCAMINHADO
	,		0 AS PRIORIZADO
	FROM	DADOS_MEDICAO AS A
	WHERE	1=1
	AND		A.STATUS IN ('ENCERRADO', 'RESOLVIDO', 'CANCELADO')
	AND		(A.PRAZO IS NULL OR A.DURACAO IS NULL) -- cálculo impossível
	--
	UNION	
	--
	SELECT	A.*
	,		0 AS VIOLACAO
	,		0 AS ENCERRADO
	,		0 AS RESOLVIDO
	,		0 AS CANCELADO
	,		1 AS ENCAMINHADO
	,		0 AS PRIORIZADO
	FROM	DADOS_MEDICAO AS A
	WHERE	1=1
	AND		A.STATUS = 'ENCAMINHADO'
	--
	UNION	
	--
	SELECT	A.*
	,		0 AS VIOLACAO
	,		0 AS ENCERRADO
	,		0 AS RESOLVIDO
	,		0 AS CANCELADO
	,		0 AS ENCAMINHADO
	,		1 AS PRIORIZADO
	FROM	DADOS_MEDICAO_PESO35 AS A
	WHERE	1=1
	--
	ORDER	BY ID_CHAMADO;

DROP VIEW IF EXISTS VW_KPI_PRS;
CREATE VIEW VW_KPI_PRS AS
	SELECT	COUNT(*) AS INCIDENTES
	,		SUM(ENCERRADO) AS ENCERRADOS
	,		SUM(RESOLVIDO) AS RESOLVIDOS
	,		SUM(CANCELADO) AS CANCELADOS
	,		SUM(ENCAMINHADO) AS ENCAMINHADOS
	,		SUM(PRIORIZADO) AS PRIORIZADOS
	,		SUM(VIOLACAO) AS VIOLACOES
	,		100.0 * (SUM(VIOLACAO) / COUNT(*))  AS PRS
	FROM	VW_KPI_PRS_DETALHES;
	
DROP VIEW IF EXISTS VW_KPI_PRS_SIMPLES;
CREATE VIEW VW_KPI_PRS_SIMPLES AS
	SELECT	COUNT(*) AS INCIDENTES
	,		SUM(ENCERRADO) AS ENCERRADOS
	,		SUM(RESOLVIDO) AS RESOLVIDOS
	,		SUM(CANCELADO) AS CANCELADOS
	,		SUM(ENCAMINHADO) AS ENCAMINHADOS
	,		SUM(PRIORIZADO) AS PRIORIZADOS
	,		SUM(VIOLACAO) AS VIOLACOES
	,		100.0 * (SUM(VIOLACAO) / COUNT(*))  AS PRS_SIMPLES
	FROM	VW_KPI_PRS_DETALHES
	WHERE	COMPLEXIDADE = 'SIMPLES';

DROP VIEW IF EXISTS VW_KPI_PRS_MEDIO;
CREATE VIEW VW_KPI_PRS_MEDIO AS
	SELECT	COUNT(*) AS INCIDENTES
	,		SUM(ENCERRADO) AS ENCERRADOS
	,		SUM(RESOLVIDO) AS RESOLVIDOS
	,		SUM(CANCELADO) AS CANCELADOS
	,		SUM(ENCAMINHADO) AS ENCAMINHADOS
	,		SUM(PRIORIZADO) AS PRIORIZADOS
	,		SUM(VIOLACAO) AS VIOLACOES
	,		100.0 * (SUM(VIOLACAO) / COUNT(*))  AS PRS_MEDIO
	FROM	VW_KPI_PRS_DETALHES
	WHERE	COMPLEXIDADE = 'MEDIO';


DROP VIEW IF EXISTS VW_KPI_PRS_COMPLEXO;
CREATE VIEW VW_KPI_PRS_COMPLEXO AS
	SELECT	COUNT(*) AS INCIDENTES
	,		SUM(ENCERRADO) AS ENCERRADOS
	,		SUM(RESOLVIDO) AS RESOLVIDOS
	,		SUM(CANCELADO) AS CANCELADOS
	,		SUM(ENCAMINHADO) AS ENCAMINHADOS
	,		SUM(PRIORIZADO) AS PRIORIZADOS
	,		SUM(VIOLACAO) AS VIOLACOES
	,		100.0 * (SUM(VIOLACAO) / COUNT(*))  AS PRS_COMPLEXO
	FROM	VW_KPI_PRS_DETALHES
	WHERE	COMPLEXIDADE = 'COMPLEXO';

DROP VIEW IF EXISTS VW_KPI_CRI_DETALHES;
CREATE VIEW VW_KPI_CRI_DETALHES AS
	WITH MESAS AS (
		SELECT 	*
		FROM	(
					SELECT	A.ID_CHAMADO
					,		A.ID_ACAO
					,		A.DATA_INICIO_ACAO AS DATA_ACAO
					,		A.MESA_ATUAL AS MESA
					,		LEAD(A.MESA_ATUAL, 1) OVER (
								PARTITION BY A.ID_CHAMADO
								ORDER BY A.ID_ACAO
							) AS PROX_MESA
					FROM	INCIDENTE_ACOES AS A
							--
							LEFT OUTER JOIN MESAS_N4_SAP AS B
							ON 	A.MESA_ATUAL = B.MESA
					ORDER	BY A.ID_CHAMADO 
					,		A.ID_ACAO
				) AS A
		WHERE	A.DATA_ACAO 
		BETWEEN (SELECT VALOR FROM PARAMS WHERE PARAM = 'HORA_INICIO_APURACAO') 
		AND 	(SELECT VALOR FROM PARAMS WHERE PARAM = 'HORA_FIM_APURACAO')
		--AND		MESA IN (SELECT MESA FROM MESAS_N4_SAP)
		--AND		PROX_MESA NOT IN (SELECT MESA FROM MESAS_N4_SAP)
	),
	DADOS AS (
		SELECT	A.*
		,		CASE 	WHEN	B.MESA IS NULL 			AND	C.MESA IS NULL 			THEN 'IGNORAR'
						WHEN 	B.MESA IS NULL 			AND C.MESA IS NOT NULL 		THEN 'RECEBIDO - FORA CONTRATO -> CONTRATO'
						WHEN 	B.MESA IS NOT NULL 		AND C.MESA IS NULL 			THEN 'TRATADO - CONTRATO -> FORA DO CONTRATO'
						WHEN 	B.MESA IS NOT NULL		AND C.MESA IS NOT NULL 		THEN 'IGNORAR - CONTRATO -> CONTRATO'
						--				
				END AS TIPO_REGISTRO
		FROM	MESAS AS A
				--
				LEFT OUTER JOIN MESAS_N4_SAP AS B
				ON	A.MESA = B.MESA
				--
				LEFT OUTER JOIN MESAS_N4_SAP AS C
				ON	A.PROX_MESA = C.MESA
				--
		WHERE	1=1
		AND		(B.MESA IS NOT NULL OR C.MESA IS NOT NULL) -- ALGUMA MOVIMENTAÇÃO DENTRO DO CONTRATO
		AND		A.PROX_MESA IS NOT NULL -- NÃO PROCESSAR ÚLTIMA AÇÃO
		AND		((B.MESA IS NULL OR C.MESA IS NULL) -- PARA PERMITIR ENCAMINHAMENTOS DE/PARA FORA DO CONTRATO. CORREÇÃO DE BUG
		OR		(NOT (B.MESA IS NOT NULL AND C.MESA IS NOT NULL AND B.ABREV = 'PRIO' AND C.ABREV = 'PRIO' )) -- MOVIMENTO DENTRO DO CONTRATO SEM MUDANÇA DE PRIORIZAÇÃO		
		OR		(NOT (B.MESA IS NOT NULL AND C.MESA IS NOT NULL AND B.ABREV <> 'PRIO' AND C.ABREV <> 'PRIO' ))) -- MOVIMENTO DENTRO DO CONTRATO SEM MUDANÇA DE PRIORIZAÇÃO
		--
		UNION	ALL
		--
		SELECT	A.*
		,		'TRATADO - ' || C.STATUS AS TIPO_REGISTRO
		FROM	MESAS AS A
				--
				INNER JOIN MESAS_N4_SAP AS B
				ON	A.MESA = B.MESA
				--
				INNER JOIN VW_STATUS_CHAMADO AS C
				ON	A.ID_CHAMADO  = C.ID_CHAMADO
		WHERE	1=1
		AND		A.PROX_MESA IS NULL
		AND		C.STATUS IN ('RESOLVIDO', 'ENCERRADO', 'CANCELADO')
		--
		ORDER	BY A.ID_CHAMADO
		,		A.ID_ACAO
	)
	SELECT	A.ID_CHAMADO
	,		B.ID_ACAO
	,		B.MESA
	,		B.PROX_MESA
	,		B.TIPO_REGISTRO
	,		ROW_NUMBER() OVER(
				PARTITION BY B.ID_CHAMADO, B.TIPO_REGISTRO
				ORDER BY B.ID_ACAO
			) AS SEQ_TIPO_REGISTRO
	FROM	VW_DADOS_MEDICAO AS A
			--
			INNER JOIN DADOS AS B
			ON	A.ID_CHAMADO = B.ID_CHAMADO
			--
	WHERE	TIPO_REGISTRO IS NOT NULL
	AND		TIPO_REGISTRO NOT LIKE 'IGNORAR%'
	ORDER	BY A.ID_CHAMADO
	,		B.ID_ACAO;


DROP VIEW IF EXISTS VW_KPI_CRI;
CREATE VIEW VW_KPI_CRI AS 
	SELECT	COUNT(*) AS INCIDENTES
	,		SUM(CASE WHEN TIPO_REGISTRO = 'RECEBIDO - FORA CONTRATO -> CONTRATO' 	THEN 1 ELSE 0 END) AS RECEBIDOS_FORA_CONTRATO
	,		SUM(CASE WHEN TIPO_REGISTRO = 'TRATADO - ENCERRADO' 					THEN 1 ELSE 0 END) AS TRATADOS_ENCERRADOS
	,		SUM(CASE WHEN TIPO_REGISTRO = 'TRATADO - CANCELADO' 					THEN 1 ELSE 0 END) AS TRATADOS_CANCELADOS
	,		SUM(CASE WHEN TIPO_REGISTRO = 'TRATADO - RESOLVIDO' 					THEN 1 ELSE 0 END) AS TRATADOS_RESOLVIDOS
	,		SUM(CASE WHEN TIPO_REGISTRO = 'TRATADO - CONTRATO -> FORA DO CONTRATO' 	THEN 1 ELSE 0 END) AS TRATADOS_ENCAMINHADOS
	,		100.0 
	* 		(SUM(CASE WHEN TIPO_REGISTRO LIKE 'TRATADO %' THEN 1.0 ELSE 0.0 END) 
	/ 		SUM(CASE WHEN TIPO_REGISTRO LIKE 'RECEBIDO %' THEN 1.0 ELSE 0.0 END))  AS CRI
	FROM	VW_KPI_CRI_DETALHES
	WHERE	SEQ_TIPO_REGISTRO = 1;
	
DROP VIEW IF EXISTS VW_KPI_SIT_DETALHES;
CREATE VIEW VW_KPI_SIT_DETALHES AS
	SELECT	A.*
	FROM	VW_DADOS_MEDICAO AS A
			--
			INNER JOIN MESAS_N4_SAP AS B
			ON A.MESA = B.MESA
			--
	WHERE	A.STATUS = 'EM ABERTO';

DROP VIEW IF EXISTS VW_KPI_SIT;
CREATE VIEW VW_KPI_SIT AS
	SELECT	COUNT(*) AS INCIDENTES
	,		(SELECT CAST(VALOR AS REAL) FROM PARAMS WHERE PARAM = 'MEDIA_INCS_RECEBIDOS') AS MEDIA_INCS_RECEBIDOS
	,		(COUNT(*) / (SELECT CAST(VALOR AS REAL) FROM PARAMS WHERE PARAM = 'MEDIA_INCS_RECEBIDOS')) * 100.0 AS SIT
	FROM	VW_KPI_SIT_DETALHES AS A;