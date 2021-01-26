WITH PARAMS AS (
	SELECT 	CONVERT(DATETIME, /*'2021-01-25'*/? + ' 00:00:00', 120) AS START_DT
	,		CONVERT(DATETIME, /*'2021-01-25'*/? + ' 23:59:59', 120) AS END_DT
)
SELECT	A.ACT_REG_ID
,		A.INCIDENT_ID
,		CONVERT(VARCHAR(19), A.DATE_ACTIONED, 120)	AS DATE_ACTIONED
,		B.ACT_TYPE_N
,		A.SUPPLIER_ID
,		COALESCE(C.SERV_DEPT_ID, 0) 				AS ASS_SVD_ID
,		C.SERV_DEPT_N
,		COALESCE(A.ASSYST_USR_ID, 0)				AS ASS_USR_ID
,		COALESCE(A.TIME_TO_RESOLVE, 0)				AS TIME_TO_RESOLVE
,		A.ACT_TYPE_ID 
,		COALESCE(A.ASSIGNMENT_TIME, 0)				AS ASSIGNMENT_TIME	
,		CASE
			WHEN A.ACT_TYPE_ID = 4 /* PENDING-CLOSURE / Resolver */ THEN 'y'
			else 'n'
		END											AS IS_RESOLUTION		
,		CASE
			WHEN B.USER_STATUS = 'y' THEN 'User Status'
			WHEN B.USER_STATUS = 'n' THEN NULL
			WHEN B.USER_STATUS = 's' THEN 'Stage Action'
			WHEN B.USER_STATUS = 'e' THEN 'Both Stage and User Status'
			WHEN B.USER_STATUS = 'c' THEN 'Internal Stop Clock'
			WHEN B.USER_STATUS = 'l' THEN 'User Status and Int. Stop Clock '
			WHEN B.USER_STATUS = 't' THEN 'Internal Start Clock'
			WHEN B.USER_STATUS = 'u' THEN 'Supplier Stop Clock'
			WHEN B.USER_STATUS = 'p' THEN 'Supplier Start Clock'
			WHEN B.USER_STATUS = 'a' THEN 'User Status and Int. Start Clock' 
			ELSE NULL
		END											AS USER_STATUS
,		A.REMARKS		
FROM 	VW_ACT_REG 									AS A
		--
		LEFT OUTER HASH JOIN ACT_TYPE  				AS B
		ON 	A.ACT_TYPE_ID 							= B.ACT_TYPE_ID
		--
		LEFT OUTER HASH JOIN SERV_DEPT				AS C
		ON	A.SERV_DEPT_ID							= C.SERV_DEPT_ID
		AND	A.ACT_TYPE_ID 							= 1 
		--
WHERE	1=1
AND		A.ACT_TYPE_ID IN (
			1,	 /* ATRIBUICAO INTERNA                */ 4,	  /* RESOLVER                       */	
			5,	 /* ENCERRAR                          */ 6,	  /* REABRIR                        */	
			11,	 /* ATRIBUIR AO FORNECEDOR            */ 13,  /* RESPOSTA DO FORNECEDOR         */	
			14,	 /* RESOLVER FORNECEDOR - EXECUTAR ANTES DO "RESOLVER"!	*/	
			15,	 /* REABERTO PELO FORNECEDOR          */	
			18,	 /* CANCELADO                         */ 31,  /* CAMPO DO FORMULARIO ALTERADO   */	
			51,	 /* ALTERADO                          */ 52,  /* CATEGORIA ALTERADA             */	
			70,	 /* CAMPOS ALTERADOS                  */ 119, /* PENDENCIA SANADA               */	
			120, /* INICIAR RELOGIO                   */ 121, /* PARAR RELOGIO                  */	
			122, /* AGUARDANDO CLIENTE                */ 140, /* ATENDIMENTO PROGRAMADO         */	
			141, /* INICIAR ATENDIMENTO               */ 142, /* ATENDIMENTO AGENDADO           */	
			146, /* PENDENCIA DE FORNECEDOR           */ 147, /* PENDENCIA DE TIC               */	
			148, /* PENDENCIA SANADA FERIADO LOCAL    */ 149, /* PENDENCIA FERIADO LOCAL        */	
			150, /* PENDENCIA SANADA - FORNECEDOR/TIC */ 151, /* CANCELAR                       */	
			152, /* RETORNO DO USUARIO                */ 153, /* AGUARDANDO CLIENTE - APROVACAO */	
			154, /* AGUARDANDO CLIENTE - FORNECEDOR   */ 155, /* PENDENCIA SANADA - APROVACAO   */
			42,	 /* Adicionar Informação (Pública) */ /* adicionado para fins de cálculo de última ação */
			102	 /* Adicionar Informação (Técnica) */ /* adicionado para fins de cálculo de última ação */
		)
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
			UNION
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
,		A.ACT_REG_ID