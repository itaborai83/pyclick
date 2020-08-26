SELECT	A.ID_CHAMADO 		AS ID_CHAMADO_A
,		A.ID_ACAO 			AS ID_ACAO_A
,		A.ULTIMA_ACAO_NOME	AS ACAO_A
,		A.MESA_ATUAL		AS MESA_A
,		B.ID_CHAMADO		AS ID_CHAMADO_B
,		B.ID_ACAO 			AS ID_ACAO_B
,		B.ULTIMA_ACAO_NOME	AS ACAO_B
,		B.MESA_ATUAL		AS MESA_B
,		A.DATA_INICIO_ACAO 	AS DATA_INICIO_ACOES
FROM	INCIDENTE_ACOES AS A
		--
		INNER JOIN INCIDENTE_ACOES AS B
		ON	A.ID_CHAMADO = B.ID_CHAMADO
		AND	A.ID_ACAO < B.ID_ACAO
		AND	A.DATA_INICIO_ACAO = B.DATA_INICIO_ACAO 
		AND A.ULTIMA_ACAO_NOME = 'Resolver'
		AND B.ULTIMA_ACAO_NOME = 'Atribuição interna'
		--
GROUP 	BY 1
ORDER	BY 2 DESC