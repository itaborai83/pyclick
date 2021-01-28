WITH PARAMS AS (
	SELECT 	CONVERT(DATETIME, /*'2021-01-25'*/?, 120) AS START_DT
	,		CONVERT(DATETIME, /*'2021-01-25'*/?, 120) AS END_DT
)
SELECT	A.TYPE_ENUM
,		A.INCIDENT_ID
,		COALESCE(C.INCIDENT_ID, 0)						AS PARENT_INCIDENT_ID
,		CONVERT(VARCHAR(19), A.DATE_LOGGED, 120)		AS DATE_LOGGED
,		CONVERT(VARCHAR(19), A.INC_RESOLVE_ACT, 120)	AS INC_RESOLVE_ACT
,		'' + CASE	
			WHEN A.TYPE_ENUM = 1 THEN '' 
			WHEN A.TYPE_ENUM = 2 THEN 'P'
			WHEN A.TYPE_ENUM = 3 THEN 'R'
			WHEN A.TYPE_ENUM = 7 THEN 'S'
			WHEN A.TYPE_ENUM = 5 THEN 'D'
			ELSE 'T' 
		END
+ 		CAST(A.INCIDENT_REF AS NVARCHAR(30)) 	AS CHAMADO_ID
,		'' + CASE	
			WHEN C.TYPE_ENUM = 1 THEN '' 
			WHEN C.TYPE_ENUM = 2 THEN 'P'
			WHEN C.TYPE_ENUM = 3 THEN 'R'
			WHEN C.TYPE_ENUM = 7 THEN 'S'
			WHEN C.TYPE_ENUM = 5 THEN 'D'
			ELSE 'T' 
		END 
+ 		CAST(C.INCIDENT_REF AS NVARCHAR(30))	AS PARENT_CHAMADO_ID
,		CASE
			WHEN B.RECEIVE_TYPE = 't' THEN 'Telefone'
			WHEN B.RECEIVE_TYPE = 'e' THEN 'Email'
			WHEN B.RECEIVE_TYPE = 'l' THEN 'Carta'
			WHEN B.RECEIVE_TYPE = 'f' THEN 'Monitoracao'
			WHEN B.RECEIVE_TYPE = 'n' THEN 'assystNET'
			WHEN B.RECEIVE_TYPE = 'o' THEN 'Outro'
			WHEN B.RECEIVE_TYPE = 'i' THEN 'Processador de importacao'
			WHEN B.RECEIVE_TYPE = 'c' THEN 'Chat'
			WHEN B.RECEIVE_TYPE = 'a' THEN 'Registro de Cobertura'
		END 									AS SOURCE_INCIDENT
,		A.AFF_USR_ID
,		A.REP_USR_ID
,		CASE 	
			WHEN A.STATUS_ENUM = 1 THEN 'Aberto'
			WHEN A.STATUS_ENUM = 2 THEN 'Fechado'
			WHEN A.STATUS_ENUM = 3 THEN 'Resolvido'
			ELSE 'Enviado'
		END 									AS INCIDENT_STATUS
,		F.INC_MAJOR_N	 						AS MAJOR_CATEGORY
,		A.SHORT_DESC
,		B.REMARKS
,		COALESCE(CASE
			WHEN A.TYPE_ENUM IN (4,6) THEN D.SERV_OFF_ID
			ELSE B.SERV_OFF_ID
		END, 0)									AS SERV_OFF_ID
,		A.ITEM_ID
,		B.ITEM_B_ID
,		A.CAUSE_ITEM_ID
,		E.INC_CAT_N								AS CATEGORY
,		G.INC_CAT_N				 				AS CAUSE_CATEGORY
,		H.PRIORITY_DERIVED_N					-- Prioridade do CA
,		A.TIME_TO_RESOLVE
,		DATEDIFF(
			MINUTE
		, 	A.DATE_LOGGED
		, 	COALESCE(A.INC_RESOLVE_ACT, A.DATE_LOGGED)
		) 										AS INCIDENT_TOTAL_TIME_M
,		COALESCE(
			A.INC_RESOLVE_SLA 					
		,	0
		)										AS INC_RESOLVE_SLA	-- Tempo Util Evento (m)
,		CASE
			WHEN A.MAJOR_INC = 0 THEN 'n'
			WHEN A.MAJOR_INC = 1 THEN 'y'
			ELSE 'n'
		END 									AS MAJOR_INC
FROM	VW_INCIDENT 							AS A
		--
		INNER HASH JOIN INC_DATA 				AS B
		ON	A.INCIDENT_ID						= B.INCIDENT_ID
		AND	B.INCIDENT_ID						<> 0
		--
		LEFT OUTER HASH JOIN VW_INCIDENT 		AS C
		ON	B.U_NUM2							= C.INCIDENT_ID
		AND	C.INCIDENT_ID						<> 0
		--
		LEFT OUTER HASH JOIN INC_DATA 			AS D
		ON	B.U_NUM2							= D.INCIDENT_ID
		AND	D.INCIDENT_ID						<> 0
		--
		LEFT OUTER HASH JOIN INC_CAT			AS E
		ON	A.INC_CAT_ID						= E.INC_CAT_ID
		AND	E.INC_CAT_ID						<> 0
		--
		LEFT OUTER HASH JOIN INC_MAJOR			AS F
		ON	E.INC_MAJOR_ID						= F.INC_MAJOR_ID
		AND	F.INC_MAJOR_ID						<> 0
		--
		LEFT OUTER HASH JOIN INC_CAT			AS G
		ON	A.CAUSE_ID							= G.INC_CAT_ID
		AND	G.INC_CAT_ID						<> 0
		--
		LEFT OUTER HASH JOIN PRIORITY_DERIVED 	AS H
		ON	B.PRIORITY_DERIVED_ID				= H.PRIORITY_DERIVED_ID
		AND	H.PRIORITY_DERIVED_ID				<> 0
		--
WHERE	1=1
AND		A.INCIDENT_ID IN (
			SELECT	INCIDENT_ID
			FROM	VW_INCIDENT
			WHERE	1 = {}
			AND		INCIDENT_ID 	<> 0
			AND 	TYPE_ENUM 		IN (1, 4, 7) -- INCIDENTES, REQUISICOES E TAREFAS
			AND		DATE_LOGGED	< (SELECT END_DT FROM PARAMS)
			AND		( 	(1=1 AND STATUS_ENUM = 1 AND INC_RESOLVE_ACT IS NULL) 								OR 	-- ABERTOS
						(1=1 AND STATUS_ENUM IN (2, 3) AND INC_RESOLVE_ACT  > (SELECT END_DT FROM PARAMS)) ) 	-- ENCERRADOS & RESOLVIDOS 
			--
			UNION ALL
			--
			SELECT	INCIDENT_ID
			FROM 	VW_INCIDENT
			WHERE	1 = {}
			AND		INCIDENT_ID 	<> 0
			AND 	TYPE_ENUM 		IN (1, 4, 7) -- INCIDENTES, REQUISICOES E TAREFAS
			AND		DATE_LOGGED	< (SELECT END_DT FROM PARAMS)
			AND		( 	(1=1 AND STATUS_ENUM IN (2, 3) AND INC_CLOSE_DATE  BETWEEN (SELECT START_DT FROM PARAMS) AND (SELECT END_DT FROM PARAMS) ) OR -- ENCERRADOS 
						(1=1 AND STATUS_ENUM IN (2, 3) AND INC_RESOLVE_ACT BETWEEN (SELECT START_DT FROM PARAMS) AND (SELECT END_DT FROM PARAMS) ) )  -- RESOLVIDOS			
		)
ORDER	BY A.INCIDENT_ID