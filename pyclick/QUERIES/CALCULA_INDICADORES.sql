-- SELECT * FROM INDICADORES ORDER BY ORDEM
DELETE FROM INDICADORES;

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO) 
SELECT	'PRP' AS INDICADOR, 1 AS ORDEM, PRP AS VALOR
,		'Violações ' 					|| VIOLACOES  || 
		' / Incidentes '				|| INCIDENTES ||
		' > Encerrados: ' 				|| ENCERRADOS || 
		' | Resolvidos: ' 				|| RESOLVIDOS || 
		' | Cancelados: ' 				|| CANCELADOS AS OBSERVACAO
FROM 	VW_KPI_PRP AS A;

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO)  
SELECT	'PRO' AS INDICADOR, 2 AS ORDEM, PRO AS VALOR
,		'Violações ' 					|| VIOLACOES  || 
		' / Incidentes '				|| INCIDENTES ||
		' > Encerrados: ' 				|| ENCERRADOS || 
		' | Resolvidos: ' 				|| RESOLVIDOS || 
		' | Cancelados: ' 				|| CANCELADOS AS OBSERVACAO
FROM 	VW_KPI_PRO AS A;

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO)  
SELECT	'PRC' AS INDICADOR, 3 AS ORDEM, PRC AS VALOR
,		'Violações ' 					|| VIOLACOES  || 
		' / Incidentes '				|| INCIDENTES ||
		' > Encerrados: ' 				|| ENCERRADOS || 
		' | Resolvidos: ' 				|| RESOLVIDOS || 
		' | Cancelados: ' 				|| CANCELADOS AS OBSERVACAO
FROM 	VW_KPI_PRC AS A;

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO)  
SELECT	'PRS' AS INDICADOR, 4 AS ORDEM, PRS AS VALOR
,		'Violações '		 			|| VIOLACOES  || 
		' / Incidentes '				|| INCIDENTES ||
		' > Encerrados: ' 				|| ENCERRADOS || 
		' | Resolvidos: ' 				|| RESOLVIDOS || 
		' | Cancelados: ' 				|| CANCELADOS AS OBSERVACAO
FROM 	VW_KPI_PRS AS A;

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO)  
SELECT	'PRS - Simples' AS INDICADOR, 5 AS ORDEM, PRS_SIMPLES AS VALOR
,		'Violações ' 					|| VIOLACOES  || 
		' / Incidentes '				|| INCIDENTES ||
		' > Encerrados: ' 				|| ENCERRADOS || 
		' | Resolvidos: ' 				|| RESOLVIDOS || 
		' | Cancelados: ' 				|| CANCELADOS AS OBSERVACAO
FROM 	VW_KPI_PRS_SIMPLES AS A;

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO)  
SELECT	'PRS - Médio' AS INDICADOR, 6 AS ORDEM, PRS_MEDIO AS VALOR
,		'Violações ' 					|| VIOLACOES  || 
		' / Incidentes '				|| INCIDENTES ||
		' > Encerrados: ' 				|| ENCERRADOS || 
		' | Resolvidos: '		 		|| RESOLVIDOS || 
		' | Cancelados: ' 				|| CANCELADOS AS OBSERVACAO
FROM 	VW_KPI_PRS_MEDIO AS A;

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO)  
SELECT	'PRS - Complexo' AS INDICADOR, 7 AS ORDEM, PRS_COMPLEXO AS VALOR
,		'Violações ' 					|| VIOLACOES  || 
		' / Incidentes '				|| INCIDENTES ||
		' > Encerrados: ' 				|| ENCERRADOS || 
		' | Resolvidos: '		 		|| RESOLVIDOS || 
		' | Cancelados: ' 				|| CANCELADOS AS OBSERVACAO
FROM 	VW_KPI_PRS_COMPLEXO AS A;

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO)  
SELECT	'CRI' AS INDICADOR, 8 AS ORDEM, CRI AS VALOR
,		'Tratados ' 					|| TRATADOS  || 
		' / (Tratados + Recebidos) '	|| (TRATADOS + RECEBIDOS) AS OBSERVACAO
FROM 	VW_KPI_CRI AS A;

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO)  
SELECT	'SIT' AS INDICADOR, 9 AS ORDEM, SIT AS VALOR
,		'Incidentes ' 					|| INCIDENTES || 
		' / (Méd. Incs. Recebidos) '	|| MEDIA_INCS_RECEBIDOS AS OBSERVACAO
FROM 	VW_KPI_SIT AS A;

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO)
SELECT	'NUM_ESTORNOS' AS INDICADOR, 10 AS ORDEM, COUNT(*) AS VALOR
,		'Número de estornos cadastrados na tabela INCIDENTES_OVERRIDE'
FROM 	INCIDENTES_OVERRIDE WHERE ESTORNO = 'S';

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO)
SELECT	'NUM_AJUSTES' AS INDICADOR, 11 AS ORDEM, COUNT(*) AS VALOR
,		'Número de estornos cadastrados na tabela INCIDENTES_OVERRIDE'
FROM 	INCIDENTES_OVERRIDE WHERE COALESCE(ESTORNO, 'N') <> 'S';

INSERT OR REPLACE INTO INDICADORES(INDICADOR, ORDEM, VALOR, OBSERVACAO)
SELECT	'DADOS_FALTANDO' AS INDICADOR, 12 AS ORDEM, COUNT(*) AS VALOR
,		'Número incidentes com dados faltando não tratados conforme view VW_DADOS_FALTANDO'
FROM 	VW_DADOS_MEDICAO_FALTANDO;
