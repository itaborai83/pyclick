WITH PARAMS AS (
		SELECT 	CONVERT(DATETIME, ?, 120) AS START_DT
		,		CONVERT(DATETIME, ?, 120) AS END_DT
	),
INCS AS (
	/*	-- USE SINGLE LINE COMMENT AT COLUMN 0 TO TEST THE SUBQUERY
	WITH PARAMS AS (
		SELECT 	CONVERT(DATETIME, '2020-05-04 00:00:00', 120) AS START_DT
		,		CONVERT(DATETIME, '2020-05-04 23:59:59', 120) AS END_DT
	)
	*/ 	-- USE SINGLE LINE COMMENT AT COLUMN 0 TO TEST THE SUBQUERY
	-- INCIDENTES ABERTOS NA DATA
	SELECT	INCIDENT_ID
	,		INCIDENT_REF
	,		TYPE_ENUM
	,		1 AS STATUS_ENUM
	,		DATE_LOGGED
	,		NULL AS INC_RESOLVE_ACT
	,		NULL AS INC_CLOSE_DATE
	,		SHORT_DESC
	,		TIME_TO_RESOLVE
	,		INC_RESOLVE_SLA
	,		MAJOR_INC
	,		INC_CAT_ID
	,		ITEM_ID
	,		CAUSE_ID
	,		CAUSE_ITEM_ID
	,		AFF_USR_ID
	,		REP_USR_ID
	,		SECTN_DEPT_ID
	,		BLDNG_ROOM_ID
	FROM 	INCIDENT INCIDENT WITH(NOLOCK)
	WHERE	1=1
			-- ID DE SISTEMA
	AND		INCIDENT.INCIDENT_ID 	<> 0
	AND 	INCIDENT.TYPE_ENUM 		IN (1, 4, 7) -- INCIDENTES, REQUISICOES E TAREFAS
	AND		INCIDENT.DATE_LOGGED	< (SELECT END_DT FROM PARAMS)
	AND		( 	(1=1 AND INCIDENT.STATUS_ENUM = 1 AND INCIDENT.INC_RESOLVE_ACT IS NULL) 						OR -- ABERTOS
				(1=1 AND INCIDENT.STATUS_ENUM = 2 AND INCIDENT.INC_CLOSE_DATE  > (SELECT END_DT FROM PARAMS)) 	OR -- ENCERRADOS 
				(1=1 AND INCIDENT.STATUS_ENUM = 3 AND INCIDENT.INC_RESOLVE_ACT > (SELECT END_DT FROM PARAMS)) 	)  -- RESOLVIDOS
	--
	UNION
	--
	-- INCIDENTES FECHADOS NA DATA
	SELECT	INCIDENT_ID
	,		INCIDENT_REF
	,		TYPE_ENUM
	,		STATUS_ENUM
	,		DATE_LOGGED
	,		INC_RESOLVE_ACT
	,		INC_CLOSE_DATE
	,		SHORT_DESC
	,		TIME_TO_RESOLVE
	,		INC_RESOLVE_SLA
	,		MAJOR_INC
	,		INC_CAT_ID
	,		ITEM_ID
	,		CAUSE_ID
	,		CAUSE_ITEM_ID
	,		AFF_USR_ID
	,		REP_USR_ID
	,		SECTN_DEPT_ID
	,		BLDNG_ROOM_ID	
	FROM 	INCIDENT INCIDENT WITH(NOLOCK)
	WHERE	1=1
			-- ID DE SISTEMA
	AND		INCIDENT.INCIDENT_ID 	<> 0
	AND 	INCIDENT.TYPE_ENUM 		IN (1, 4, 7) -- INCIDENTES, REQUISICOES E TAREFAS
	AND		INCIDENT.DATE_LOGGED	< (SELECT END_DT FROM PARAMS)
	AND		( 	(1=1 AND INCIDENT.STATUS_ENUM = 2 AND INCIDENT.INC_CLOSE_DATE  BETWEEN (SELECT START_DT FROM PARAMS) AND (SELECT END_DT FROM PARAMS) ) OR -- ENCERRADOS 
				(1=1 AND INCIDENT.STATUS_ENUM = 3 AND INCIDENT.INC_RESOLVE_ACT BETWEEN (SELECT START_DT FROM PARAMS) AND (SELECT END_DT FROM PARAMS) ) )  -- RESOLVIDOS
),
ACTION_TYPES AS (
	SELECT	ACT_TYPE_ID 
	FROM 	ACT_TYPE
	WHERE	ACT_TYPE_ID IN (
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
		154, /* AGUARDANDO CLIENTE - FORNECEDOR   */ 155  /* PENDENCIA SANADA - APROVACAO   */
	)
),
ACTIONS AS (
	SELECT	ACT_REG.ACT_REG_ID
	,		ACT_REG.INCIDENT_ID
	,		ACT_REG.DATE_ACTIONED
	,		ACT_REG.LAST_ACTION
	,		ACT_REG.SUPPLIER_ID
	,		ACT_REG.ASS_SVD_ID
	,		ACT_REG.ASS_USR_ID
	,		ACT_REG.TIME_TO_RESOLVE
	,		ACT_REG.ACT_TYPE_ID 
	,		ACT_REG.ASSIGNMENT_TIME
	,		ACT_REG.REMARKS	
	FROM	ACT_REG
			--
			INNER JOIN INCS
			ON	ACT_REG.INCIDENT_ID	= INCS.INCIDENT_ID
			--
	WHERE	ACT_REG.date_actioned 	<= (SELECT END_DT FROM PARAMS)
	AND 	ACT_REG.ACT_TYPE_ID 	IN ( SELECT ACT_TYPE_ID FROM ACTION_TYPES ) --ACOES PRESENTES NO RELATORIO
	
),
CHANGE_FIELDS_ACTIONS AS (
			SELECT	ACT_TYPE_ID 
			FROM 	ACT_TYPE
			WHERE	ACT_TYPE_ID IN (
				1,		 /* Campo do formulario alterado   */	50,		 /* Usuario alterado               */	
				51,		 /* Item alterado                  */	52,		 /* Categoria alterada             */	
				53,		 /* Impacto alterado               */	54,		 /* Urgencia alterada              */	
				55,		 /* Campo Indicador de inatividade alterado */	
				56,		 /* Data de registro alterada      */	58,		 /* Descricao alterada             */	
				59,		 /* Localidade alterada            */	60,		 /* Departamento de secao alterado */	
				61,		 /* Observacao de Retorno Alterada */	62,		 /* Campo Cobravel Alterado        */	
				63,		 /* CSG Alterado                   */	70,		 /* Campos alterados               */	
				5000010, /* Requerido por                  */	5000011, /* Data de Inicio Agendada        */	
				5000012, /* Data de Termino Agendada       */	5000013, /* SLA                            */	
				5000014, /* Descricao anterior             */	5000015, /* Usuarios Vinculados Alterados  */	
				5000027, /* Flag de Retorno req alterada   */	5000028, /* Resumo alterado                */	
				5000029, /* Dep de serv resp alterado      */	5000030, /* Origem do evento alterada      */	
				5000031, /* Custo alterado                 */	5000032, /* Referencia de usuario alterada */	
				5000033, /* Detalhes de autorizacao alter. */	5000034, /* Data de autorizacao alterada   */	
				5000035, /* Justificativa alterada         */	5000036, /* Requisicoes adicionais alteradas */	
				5000037, /* Projeto alterado               */	5000038, /* Centro de custo alterado       */	
				5000045, /* Usuario responsavel alterado   */	5000046, /* Dep Servicos Tecnico alterado  */	
				5000047, /* Usuario tecnico alterado       */	5000048, /* Dep de serv resp B alterado    */	
				5000049, /* Usuario responsavel B alterado */	5000063	 /* Prioridade alterada			   */	
			) 
),
REPORT AS (
	SELECT 	ACT_REG.ACT_REG_ID
	,		INCIDENT.TYPE_ENUM
	,		INCIDENT.INCIDENT_ID
	,		INCIDENT_PAI.INCIDENT_ID 							AS INCIDENT_ID_PAI
	,		(SELECT DATE_LOGGED 	FROM INCS WHERE INCIDENT_ID = INCIDENT.INCIDENT_ID) AS 'Data Abertura Chamado'
	,		(SELECT INC_RESOLVE_ACT FROM INCS WHERE INCIDENT_ID = INCIDENT.INCIDENT_ID) AS 'Data Resolucao Chamado'
	,		CASE	WHEN INCIDENT.TYPE_ENUM = 1 THEN '' 
					WHEN INCIDENT.TYPE_ENUM = 2 THEN 'P'
					WHEN INCIDENT.TYPE_ENUM = 3 THEN 'R'
					WHEN INCIDENT.TYPE_ENUM = 7 THEN 'S'
					WHEN INCIDENT.TYPE_ENUM = 5 THEN 'D'
					ELSE 'T' 
			END + CAST(INCIDENT.incident_ref AS NVARCHAR(254)) 	AS 'ID Chamado'
	,		CASE	WHEN INC_DATA.U_NUM2 		= 0 THEN NULL
					WHEN INCIDENT_PAI.TYPE_ENUM = 1 THEN '' 
					WHEN INCIDENT_PAI.TYPE_ENUM = 2 THEN 'P'
					WHEN INCIDENT_PAI.TYPE_ENUM = 3 THEN 'R'
					WHEN INCIDENT_PAI.TYPE_ENUM = 7 THEN 'S'
					WHEN INCIDENT_PAI.TYPE_ENUM = 5 THEN 'D'
					ELSE 'T' 
			END + CAST((
				SELECT 	INCIDENT_PAI.incident_ref 
				FROM 	INCIDENT 
				WHERE 	INCIDENT_ID = INC_DATA.U_NUM2 
				AND 	INC_DATA.U_NUM2 <> 0) AS NVARCHAR(254)
			)													AS 'Chamado Pai'
	,		CASE
				WHEN INC_DATA.RECEIVE_TYPE = 't' THEN 'Telefone'
				WHEN INC_DATA.RECEIVE_TYPE = 'e' THEN 'Email'
				WHEN INC_DATA.RECEIVE_TYPE = 'l' THEN 'Carta'
				WHEN INC_DATA.RECEIVE_TYPE = 'f' THEN 'Monitoracao'
				WHEN INC_DATA.RECEIVE_TYPE = 'n' THEN 'assystNET'
				WHEN INC_DATA.RECEIVE_TYPE = 'o' THEN 'Outro'
				WHEN INC_DATA.RECEIVE_TYPE = 'i' THEN 'Processador de importacao'
				WHEN INC_DATA.RECEIVE_TYPE = 'c' THEN 'Chat'
				WHEN INC_DATA.RECEIVE_TYPE = 'a' THEN 'Registro de Cobertura'
			END 												AS 'Origem Chamado'
	,		USR_AFFECTED.USR_SC 								AS 'Usuario Afetado'
	,		USR_AFFECTED.USR_N 									AS 'Nome do Usuario Afetado'
	,		USR_REPORTING.USR_SC 								AS 'Usuario Informante'
	,		USR_REPORTING.USR_N									AS 'Nome do Usuario Informante'
	,		DIVISION.DIVISION_N 								AS 'Organizacao Cliente'
	,		CASE	WHEN SECTION_DEPT.DEPT_N IS NULL THEN SECTION_DEPT.SECTN_N
					ELSE SECTION_DEPT.DEPT_N
			END 												AS 'Departamento Cliente'
	,		SITE_AREA.SITE_AREA_SC 								AS 'Estado'
	,		BUILDING.BLDNG_N 									AS 'Site'
	,		CASE	WHEN (
						SELECT 	COUNT(ACT_REG_ID) 
						FROM 	ACT_REG
						WHERE 	ACT_REG.INCIDENT_ID = INCIDENT.INCIDENT_ID 
						AND 	ACT_REG.ACT_TYPE_ID = 1
					) > 1 
					THEN 'NAO' ELSE 'Sim'
			END 												AS 'FCR'
	,		CASE 	WHEN INCIDENT.STATUS_ENUM = 1 THEN 'Aberto'
					WHEN INCIDENT.STATUS_ENUM = 2 THEN 'Fechado'
					WHEN INCIDENT.STATUS_ENUM = 3 THEN 'Resolvido'
					ELSE 'Enviado'
			END 												AS 'Status de evento'
	,		INC_MAJOR_REGISTRO.INC_MAJOR_N	 					AS 'Categoria Maior'
	,		INCIDENT.SHORT_DESC 								AS 'Resumo'
		--replace(inc_data.remarks,'<==# ADD','') AS 'Descricao Detalhada',
	--	CASE
	--		WHEN inc_data.remarks like '%No description entered. No Additional Information available.%' then NULL
	--		ELSE inc_data.remarks
	--	END 'Descricao Detalhada',
	,		CASE	WHEN INCIDENT.TYPE_ENUM IN (4,6) THEN ( 
						SELECT 	SERV_N 
						from 	INC_DATA
								--
								INNER JOIN SERV_OFF WITH(NOLOCK)
								ON SERV_OFF.SERV_OFF_ID = INC_DATA_PAI.SERV_OFF_ID
								--
								INNER JOIN SERV WITH(NOLOCK) 
								ON 	SERV.SERV_ID = SERV_OFF.SERV_ID
								--
						WHERE 	INC_DATA.INCIDENT_ID = INC_DATA_PAI.INCIDENT_ID
					)
					ELSE SERV.SERV_N
			END 												AS 'Servico Catalogo'
	,	CLASSE_PRODUTO_REGISTRO.PROD_CLS_N 						AS 'Classe de Produto de Servico'
	,	PRODUTO_REGISTRO.PRODUCT_N 								AS 'Produto de Servico'
	,	ITEM_REGISTRO.ITEM_N 									AS 'Item de Servico'
	,	INC_CAT_REGISTRO.INC_CAT_N 								AS 'Categoria'
	,	CASE	WHEN INCIDENT.TYPE_ENUM IN (4,6) THEN ( 
					SELECT 	SERV_OFF_N 
					FROM 	INC_DATA
							--
							INNER JOIN SERV_OFF WITH(NOLOCK) 
							ON SERV_OFF.SERV_OFF_ID = INC_DATA_PAI.SERV_OFF_ID
							--
							WHERE INC_DATA.INCIDENT_ID = INC_DATA_PAI.INCIDENT_ID
					)
				ELSE SERV_OFF.SERV_OFF_N
		END 													AS 'Oferta Catalogo'
	,		CLASSE_GENERICA_B.GENERIC_CLS_N 					AS 'Classe Generica B'
	,		CLASSE_PRODUTO_B.PROD_CLS_N 						AS 'Classe de Produto B'
	,		PRODUTO_B.PRODUCT_N 								AS 'Produto B'
	,		SUPPLIER_PRODUCT_B.SUPPLIER_N 						AS 'Fabricante B'
	,		ITEM_B_MODELO.ITEM_N 								AS 'Item Modelo B'
	,		ITEM_B.ITEM_N 										AS 'Item B'
	,		INC_CAT_CAUSA.INC_CAT_N				 				AS 'Categoria Causa'
	,		CLASSE_GENERICA_CAUSA.GENERIC_CLS_N 				AS 'Classe Generica Causa'
	,		CLASSE_PRODUTO_CAUSA.PROD_CLS_N 					AS 'Classe de Produto Causa'
	,		PRODUTO_CAUSA.PRODUCT_N 							AS 'Produto Causa'
	,		SUPPLIER_PRODUCT_CAUSA.SUPPLIER_N 					AS 'Fabricante Causa'
	,		ITEM_CAUSA_MODELO.ITEM_N 							AS 'Item Modelo Causa'
	,		ITEM_CAUSA.ITEM_N		 							AS 'Item Causa'
	--	CASE
	--		WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'PENDING-CLOSURE') THEN ACT_REG.remarks
	--		ELSE NULL
	--	END 'Resolucao',
	,		CASE	WHEN ACT_TYPE.ACT_TYPE_ID = 4 THEN ACT_REG.REMARKS
					ELSE NULL
			END 												AS 'Resolucao'
	,		ACT_REG.ACT_REG_ID AS 'ID Acao'
			-- Falta Tipo do Movimento
			-- Falta Movimento No
	,		ACT_REG.DATE_ACTIONED 								AS 'Data Inicio Acao'
	,		CASE 	WHEN ACT_REG.ACT_REG_ID = 	MAX(ACT_REG.ACT_REG_ID) -- ACT_REG.LAST_ACTION
												OVER (PARTITION BY ACT_REG.INCIDENT_ID) 
					THEN 'y' ELSE 'n' 
			END 												AS 'Ultima Acao' 
	,		LEAD(ACT_REG.DATE_ACTIONED) OVER (
				PARTITION BY ACT_REG.INCIDENT_ID
				ORDER BY ACT_REG.DATE_ACTIONED
			) 													AS 'Data Fim Acao'
	,		CAST( CAST( (DATEDIFF(	MINUTE, 
									ACT_REG.DATE_ACTIONED, 
									LEAD(ACT_REG.DATE_ACTIONED) OVER (PARTITION BY ACT_REG.INCIDENT_ID ORDER BY ACT_REG.DATE_ACTIONED) -- ACT_REG.NEXT_DATE_ACTIONED
			)) AS INT) AS NVARCHAR) 'Tempo Total da Acao (M)'
	,		ACT_TYPE.act_type_n 								AS 'Ultima Acao Nome'
	--		CASE
	--			WHEN ACT_TYPE.user_status IN (SELECT user_status from act_type WHERE user_status IN ('c','u','l')) THEN ACT_REG.remarks
	--			ELSE NULL
	--		END 'Motivo Pendencia',
	,		CASE	WHEN ACT_TYPE.USER_STATUS IN ('c','u','l') 
					THEN ACT_REG.REMARKS ELSE NULL
			END 												AS 'Motivo Pendencia'
	,		CASE	WHEN ACT_TYPE.ACT_TYPE_ID IN 
					( SELECT ACT_TYPE_ID FROM CHANGE_FIELDS_ACTIONS )
					THEN ACT_REG.REMARKS ELSE NULL
			END 												AS 'Campos alterados'
	,		CASE	WHEN ACT_TYPE.ACT_TYPE_ID = 51 
					-- Acao de mudanca de Item do formulario
					THEN ACT_REG.REMARKS ELSE NULL
			END 												AS 'Itens alterados'
	,		CASE	WHEN ACT_REG.SUPPLIER_ID <> 0 
					THEN (	SELECT 	SLA.SLA_N 
							FROM 	SUPPLIER 
									INNER JOIN SLA 
									ON SLA.SLA_ID = SUPPLIER.DFLT_SLA_ID 
							WHERE 	SUPPLIER_ID = ACT_REG.SUPPLIER_ID )
					ELSE NULL
			END 												AS 'Nome do CA'
	,		CASE	WHEN ACT_REG.SUPPLIER_ID <> 0 		
					THEN (	SELECT 	SUPPLIER_N 
							FROM 	SUPPLIER 
							WHERE 	SUPPLIER_ID = ACT_REG.SUPPLIER_ID )
					ELSE NULL
			END 												AS 'Contrato'
	,		CASE	WHEN ACT_TYPE.ACT_TYPE_ID = 1 
					THEN (	SELECT 	SERV_DEPT_N 
							FROM 	SERV_DEPT 
							WHERE 	SERV_DEPT_ID = ACT_REG.ASS_SVD_ID)
					ELSE NULL
			END 												AS 'Mesa'
	,		CASE	WHEN ACT_TYPE.ACT_TYPE_ID = 1 
					THEN (	SELECT 	ASSYST_USR_N 
							FROM 	ASSYST_USR 
							WHERE 	ASSYST_USR_ID = ACT_REG.ASS_USR_ID)
					ELSE NULL
			END 												AS 'Designado'
	,		CASE	WHEN ACT_TYPE.ACT_TYPE_ID = 1 
					THEN (	SELECT 	SERV_DEPT.SERV_DEPT_N 
							FROM 	ASSYST_USR 
									--
									INNER JOIN SERV_DEPT 
									ON SERV_DEPT.SERV_DEPT_ID = ASSYST_USR.SERV_DEPT_ID 
									--
							WHERE ASSYST_USR_ID = ACT_REG.ASS_USR_ID)
					ELSE NULL
			END 												AS 'Grupo Default'
	,		PRIORITY_DERIVED.priority_derived_n 'Prioridade do CA'
	,		CASE	WHEN ACT_REG.SUPPLIER_ID <> 0 
					THEN (	SELECT 	SLA.SLA_RMK 
							FROM 	SUPPLIER 
									--
									INNER JOIN SLA 
									ON SLA.SLA_ID = SUPPLIER.DFLT_SLA_ID 
									--
							WHERE SUPPLIER_ID = ACT_REG.SUPPLIER_ID )
					ELSE NULL
			END 												AS 'Descricao da Prioridade do CA' -- Remarks do CA aplicado ao fornecedor
	,		INCIDENT.TIME_TO_RESOLVE 							AS 'Prazo Prioridade ANS (m)'	
	,		CASE	WHEN ACT_TYPE.ACT_TYPE_SC = (SELECT ACT_TYPE_SC FROM ACT_TYPE WHERE ACT_TYPE_SC = 'ASSIGN') 
					THEN  ACT_REG.TIME_TO_RESOLVE
					ELSE NULL
			END 												AS 'Prazo Prioridade ANO (m)'
	,		CASE	WHEN ACT_TYPE.act_type_sc = (SELECT ACT_TYPE_SC FROM ACT_TYPE WHERE ACT_TYPE_SC = 'SUPP-ASSIGN') THEN  ACT_REG.time_to_resolve
					ELSE NULL
			END 												AS 'Prazo Prioridade CA (m)'
	,		DATEDIFF(MINUTE, INCIDENT.DATE_LOGGED, INCIDENT.INC_RESOLVE_ACT) AS 'Tempo Total Evento (m)'
	,		INCIDENT.INC_RESOLVE_SLA 							AS 'Tempo Util Evento (m)'
			-- Falta Tempo Total de Atribuicao Mesa (m)
	,		CASE	WHEN ACT_TYPE.ACT_TYPE_SC = (SELECT ACT_TYPE_SC FROM ACT_TYPE WHERE ACT_TYPE_SC = 'ASSIGN') THEN  ACT_REG.ASSIGNMENT_TIME
					ELSE NULL
			END 												AS 'Tempo Util Atribuicao Mesa (m)'
			-- Falta Tempo Total de Atribuicao CA (m)
	,		CASE	WHEN ACT_TYPE.ACT_TYPE_SC = (SELECT ACT_TYPE_SC FROM ACT_TYPE WHERE ACT_TYPE_SC = 'SUPP-ASSIGN') THEN  ACT_REG.ASSIGNMENT_TIME
					ELSE NULL
			END 												AS 'Tempo Util Atribuicao CA (m)'
	,		CASE	WHEN (	SELECT COUNT(LINK_INC_ID) FROM LINK_INC 
							WHERE LINK_INC.INCIDENT_ID = INCIDENT.INCIDENT_ID) > 0 
					THEN 'Sim' ELSE 'Nao'
			END 												AS 'Vinculo'
	,		CASE 	WHEN (
						SELECT 	COUNT(LINK_INC.INCIDENT_ID) 
						FROM 	LINK_INC
								--
					            INNER JOIN LINK_GRP WITH(NOLOCK)
		                    	ON LINK_GRP.LINK_GRP_ID = LINK_INC.LINK_GRP_ID
		                    	--
		             			INNER JOIN LINK_RSN WITH(NOLOCK)
		                    	ON LINK_RSN.LINK_RSN_ID = LINK_GRP.LINK_RSN_ID
		                    	--
	     				WHERE 	link_rsn.link_rsn_n LIKE 'Incidente Grave'  -- CUIDADO COM UPPER CASE!!!
	     				AND 	link_inc.incident_id = INCIDENT.incident_id
	     				) > 0 
	 				THEN 'Sim' ELSE 'Nao'
			END 												AS 'Vinculo com Incidente Grave?'
	,		CASE 	WHEN INCIDENT.MAJOR_INC = 0 
					then 	'Nao' else 'Sim' END 				AS 'Incidente Grave?' 
	FROM 	ACTIONS AS ACT_REG WITH  (NOLOCK)		
			--
			INNER JOIN INCS AS INCIDENT WITH (NOLOCK)
			ON INCIDENT.INCIDENT_ID 										= ACT_REG.INCIDENT_ID
			--
			INNER JOIN INC_DATA  WITH (NOLOCK)
			ON INC_DATA.INCIDENT_ID 										= INCIDENT.INCIDENT_ID 
			--
			INNER JOIN INCIDENT INCIDENT_PAI  WITH (NOLOCK)
			ON INCIDENT_PAI.INCIDENT_ID 									= INC_DATA.U_NUM2 
			--
			INNER JOIN INC_DATA INC_DATA_PAI WITH (NOLOCK)
			ON INC_DATA_PAI.INCIDENT_ID 									= INC_DATA.U_NUM2 		
			--
			INNER JOIN SERV_DEPT SERV_DEPT WITH (NOLOCK)
			ON SERV_DEPT.SERV_DEPT_ID 										= ACT_REG.ASS_SVD_ID
			--
			INNER JOIN SUPPLIER SUPPLIER WITH (NOLOCK)
			ON SUPPLIER.SUPPLIER_ID 										= ACT_REG.SUPPLIER_ID
			--
			INNER JOIN ACT_TYPE ACT_TYPE WITH (NOLOCK)
			ON 	ACT_TYPE.ACT_TYPE_ID 										= ACT_REG.ACT_TYPE_ID
			AND	(INCIDENT.status_enum <> 1  
			-- REMOVER DA LISTAGEM INCIDENTES RESOLVIDOS NA DATA
			OR ACT_REG.ACT_TYPE_ID NOT IN (											 
					4,	-- RESOLVER
					5,	-- ENCERRAR
					14,	-- RESOLVER FORNECEDOR - EXECUTAR ANTES DO "RESOLVER"!
					18,	-- CANCELADO
					151	-- CANCELAR
				))
			--
			INNER JOIN INC_CAT INC_CAT_REGISTRO  WITH (NOLOCK)
			ON INC_CAT_REGISTRO.INC_CAT_ID 									= INCIDENT.INC_CAT_ID 
			--
			INNER JOIN INC_MAJOR INC_MAJOR_REGISTRO  WITH (NOLOCK)
			ON INC_MAJOR_REGISTRO.INC_MAJOR_ID 								= INC_CAT_REGISTRO.INC_MAJOR_ID 
			--
			INNER JOIN SERV_OFF SERV_OFF WITH (NOLOCK)
			ON SERV_OFF.SERV_OFF_ID 										= INC_DATA.SERV_OFF_ID 
			--
			INNER JOIN SERV SERV WITH (NOLOCK)
			ON SERV.SERV_ID 												= SERV_OFF.SERV_ID 
			--
			INNER HASH JOIN ITEM ITEM_REGISTRO  WITH(NOLOCK)
			ON ITEM_REGISTRO.ITEM_ID 										= INCIDENT.ITEM_ID 
			--
			INNER HASH JOIN PRODUCT PRODUTO_REGISTRO WITH(NOLOCK) 
			ON PRODUTO_REGISTRO.PRODUCT_ID 									= ITEM_REGISTRO.PRODUCT_ID 
			--
			INNER HASH JOIN PROD_CLS CLASSE_PRODUTO_REGISTRO WITH(NOLOCK)
			ON CLASSE_PRODUTO_REGISTRO.PROD_CLS_ID 							= PRODUTO_REGISTRO.PROD_CLS_ID 
			--
			INNER HASH JOIN GENERIC_CLS CLASSE_GENERICA_REGISTRO  WITH(NOLOCK)
			ON 	CLASSE_GENERICA_REGISTRO.GENERIC_CLS_ID 						= CLASSE_PRODUTO_REGISTRO.GENERIC_CLS_ID 
			AND CLASSE_GENERICA_REGISTRO.GENERIC_CLS_SC IN ('SERVICOS DE TIC', 'SOFTWARE' )
			--
			INNER JOIN ITEM ITEM_B  WITH(NOLOCK)
			ON ITEM_B.ITEM_ID 												= INC_DATA.ITEM_B_ID
			--
			INNER JOIN PRODUCT PRODUTO_B  WITH(NOLOCK)
			ON PRODUTO_B.PRODUCT_ID 										= ITEM_B.PRODUCT_ID 
			--
			INNER JOIN ITEM ITEM_B_MODELO WITH(NOLOCK)
			ON ITEM_B_MODELO.ITEM_ID 										= PRODUTO_B.MODEL_ITEM_ID 
			--
			INNER JOIN PROD_CLS CLASSE_PRODUTO_B WITH(NOLOCK)
			ON CLASSE_PRODUTO_B.PROD_CLS_ID 								= PRODUTO_B.PROD_CLS_ID 
			--
			INNER JOIN GENERIC_CLS CLASSE_GENERICA_B WITH(NOLOCK)
			ON CLASSE_GENERICA_B.GENERIC_CLS_ID 							= CLASSE_PRODUTO_B.GENERIC_CLS_ID 
			--
			INNER JOIN INC_CAT INC_CAT_CAUSA  WITH(NOLOCK)
			ON INC_CAT_CAUSA.INC_CAT_ID 									= INCIDENT.CAUSE_ID 
			--
			INNER JOIN SUPPLIER SUPPLIER_PRODUCT_B WITH(NOLOCK)
			ON PRODUTO_B.SUPPLIER_ID 										= SUPPLIER_PRODUCT_B.SUPPLIER_ID 
			--
			INNER JOIN ITEM ITEM_CAUSA  WITH(NOLOCK)
			ON ITEM_CAUSA.ITEM_ID 											= INCIDENT.CAUSE_ITEM_ID 
			--
			INNER JOIN SUPPLIER SUPPLIER_CAUSA_ITEM WITH(NOLOCK)
			ON ITEM_CAUSA.INV_SUPP_ID 										= SUPPLIER_CAUSA_ITEM.SUPPLIER_ID 
			--
			INNER JOIN PRODUCT PRODUTO_CAUSA  WITH(NOLOCK)
			ON PRODUTO_CAUSA.PRODUCT_ID 									= ITEM_CAUSA.PRODUCT_ID 
			--
			INNER JOIN PROD_CLS CLASSE_PRODUTO_CAUSA WITH(NOLOCK)
			ON CLASSE_PRODUTO_CAUSA.PROD_CLS_ID 							= PRODUTO_CAUSA.PROD_CLS_ID 
			--
			INNER JOIN ITEM ITEM_CAUSA_MODELO WITH(NOLOCK)
			ON ITEM_CAUSA_MODELO.ITEM_ID 									= PRODUTO_CAUSA.MODEL_ITEM_ID
			--
			INNER JOIN GENERIC_CLS CLASSE_GENERICA_CAUSA  WITH(NOLOCK)
			ON CLASSE_GENERICA_CAUSA.GENERIC_CLS_ID 						= CLASSE_PRODUTO_CAUSA.GENERIC_CLS_ID
			--
			INNER JOIN SUPPLIER SUPPLIER_PRODUCT_CAUSA WITH(NOLOCK)
			ON PRODUTO_CAUSA.SUPPLIER_ID 									= SUPPLIER_PRODUCT_CAUSA.SUPPLIER_ID
			--
			INNER JOIN PRIORITY_DERIVED PRIORITY_DERIVED WITH(NOLOCK)
			ON  PRIORITY_DERIVED.PRIORITY_DERIVED_ID 						= INC_DATA.PRIORITY_DERIVED_ID
			--
			INNER JOIN USR USR_AFFECTED WITH(NOLOCK)
			ON USR_AFFECTED.USR_ID 											= INCIDENT.AFF_USR_ID
			--
			INNER JOIN USR USR_REPORTING WITH(NOLOCK)
			ON USR_REPORTING.USR_ID 										= INCIDENT.REP_USR_ID
			--
			INNER JOIN SECTN_DEPT SECTION_DEPT WITH(NOLOCK)
			ON SECTION_DEPT.SECTN_DEPT_ID 									= INCIDENT.SECTN_DEPT_ID
			--
			INNER JOIN SECTN SECTION WITH(NOLOCK)
			ON SECTION.SECTN_ID 											= SECTION_DEPT.SECTN_ID
			--
			INNER JOIN BRANCH BRANCH WITH(NOLOCK)
			ON BRANCH.BRANCH_ID 											= SECTION.BRANCH_ID
			--
			INNER JOIN DIVISION DIVISION WITH(NOLOCK)
			ON DIVISION.DIVISION_ID 										= BRANCH.DIVISION_ID
			--
			INNER JOIN BLDNG_ROOM BUILDING_ROOM
			ON BUILDING_ROOM.BLDNG_ROOM_ID 									= INCIDENT.BLDNG_ROOM_ID
			--
			INNER JOIN BLDNG BUILDING WITH(NOLOCK)
			ON BUILDING.BLDNG_ID 											= BUILDING_ROOM.BLDNG_ID
			--
			INNER JOIN SITE SITE WITH(NOLOCK)
			ON SITE.SITE_ID 												= BUILDING.SITE_ID
			--
			INNER JOIN SITE_AREA SITE_AREA WITH(NOLOCK)
			ON SITE_AREA.SITE_AREA_ID 										= SITE.SITE_AREA_ID
)
SELECT 	REPORT."Data Abertura Chamado" 				AS "Data Abertura Chamado"
,		REPORT."Data Resolucao Chamado" 			AS "Data Resolução Chamado"
,		REPORT."ID Chamado" 						AS "ID Chamado"
,		REPORT."Chamado Pai" 						AS "Chamado Pai"
,		REPORT."Origem Chamado" 					AS "Origem Chamado"
,		TRANSLATE(CAST(REPORT."Usuario Afetado" 								AS NVARCHAR(254)), 	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Usuário Afetado"
,		TRANSLATE(CAST(REPORT."Nome do Usuario Afetado" 						AS NVARCHAR(254)), 	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Nome do Usuário Afetado" 
,		TRANSLATE(CAST(REPORT."Usuario Informante" 								AS NVARCHAR(254)), 	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Usuário Informante"
,		TRANSLATE(CAST(REPORT."Nome do Usuario Informante" 						AS NVARCHAR(254)), 	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Nome do Usuário Informante"
,		TRANSLATE(CAST(REPORT."Organizacao Cliente" 							AS NVARCHAR(254)), 	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Organização Cliente"
,		TRANSLATE(CAST(REPORT."Departamento Cliente" 							AS NVARCHAR(254)), 	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Departamento Cliente"
,		REPORT."Estado" 							AS "Estado"
,		REPORT."Site" 								AS "Site"
,		REPORT."FCR" 								AS "FCR"
,		REPORT."Status de evento" 					AS "Status de evento"
,		REPORT."Categoria Maior" 					AS "Categoria Maior"
,		TRANSLATE(REPORT."Resumo", 																	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Resumo"
,		TRANSLATE(CAST(REPORT."Servico Catalogo" 								AS NVARCHAR(254)), 	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Serviço Catálogo"
,		REPORT."Classe de Produto de Servico" 		AS "Classe de Produto de Serviço"
,		REPORT."Produto de Servico" 				AS "Produto de Serviço"
,		REPORT."Item de Servico" 					AS "Item de Serviço"
,		REPORT."Categoria" 							AS "Categoria"
,		REPORT."Oferta Catalogo" 					AS "Oferta Catálogo"
,		REPORT."Classe Generica B" 					AS "Classe Genérica B"
,		REPORT."Classe de Produto B" 				AS "Classe de Produto B"
,		REPORT."Produto B" 							AS "Produto B"
,		REPORT."Fabricante B" 						AS "Fabricante B"
,		REPORT."Item Modelo B" 						AS "Item Modelo B"
,		REPORT."Item B" 							AS "Item B"
,		REPORT."Categoria Causa" 					AS "Categoria Causa"
,		REPORT."Classe Generica Causa" 				AS "Classe Genérica Causa"
,		REPORT."Classe de Produto Causa" 			AS "Classe de Produto Causa"
,		REPORT."Produto Causa" 						AS "Produto Causa"
,		REPORT."Fabricante Causa" 					AS "Fabricante Causa"
,		REPORT."Item Modelo Causa" 					AS "Item Modelo Causa"
,		REPORT."Item Causa" 						AS "Item Causa"
,		TRANSLATE(CAST(REPORT."Resolucao" 										AS NVARCHAR(254)),	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Resolução"
,		REPORT."ID Acao" 							AS "ID Ação"
,		REPORT."Data Inicio Acao" 					AS "Data Inicio Ação"
,		REPORT."Ultima Acao" 						AS "Ultima Ação"
,		REPORT."Data Fim Acao" 						AS "Data Fim Ação"
-->>-------------------------------------------------------------------------------------------------------------------
,		CAST(            CAST((REPORT."Tempo Total da Acao (M)") 						AS int) / 60 AS NVARCHAR(254)) + ':'  
+ 		RIGHT('0' + CAST(CAST((REPORT."Tempo Total da Acao (M)") 						AS int) % 60 AS NVARCHAR(254)), 2)
													AS "Tempo Total da Ação (h)"
--<<-------------------------------------------------------------------------------------------------------------------
,		REPORT."Tempo Total da Acao (M)"			AS "Tempo Total da Ação (M)"
,		REPORT."Ultima Acao Nome" 					AS "Ultima Ação Nome"
,		TRANSLATE(CAST(REPORT."Motivo Pendencia" 								AS NVARCHAR(254)),	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Motivo Pendencia"
,		TRANSLATE(CAST(REPORT."Campos alterados" 								AS NVARCHAR(254)), 	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Campos alterados"
,		TRANSLATE(CAST(REPORT."Itens alterados" 								AS NVARCHAR(254)),	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Itens alterados"
,		REPORT."Nome do CA" 						AS "Nome do CA"
,		REPORT."Contrato" 							AS "Contrato"
,		REPORT."Mesa" 								AS "Mesa"
,		REPORT."Designado" 							AS "Designado"
,		REPORT."Grupo Default" 						AS "Grupo Default"
,		REPORT."Prioridade do CA" 					AS "Prioridade do CA"
,		TRANSLATE(CAST(REPORT."Descricao da Prioridade do CA" 					AS NVARCHAR(254)), 	'"'+CHAR(9)+CHAR(10)+CHAR(13), '    ')
													AS "Descrição da Prioridade do CA"
,		REPORT."Prazo Prioridade ANS (m)" 			AS "Prazo Prioridade ANS (m)"
-->>-------------------------------------------------------------------------------------------------------------------
,		CAST(            CAST((REPORT."Prazo Prioridade ANS (m)") 						AS int) / 60 AS NVARCHAR(254)) + ':'  
+ 		RIGHT('0' + CAST(CAST((REPORT."Prazo Prioridade ANS (m)") 						AS int) % 60 AS NVARCHAR(254)), 2)
													AS "Prazo Prioridade ANS (h)"
--<<-------------------------------------------------------------------------------------------------------------------
,		REPORT."Prazo Prioridade ANO (m)" 			AS "Prazo Prioridade ANO (m)"
-->>-------------------------------------------------------------------------------------------------------------------
,		CAST(            CAST((REPORT."Prazo Prioridade ANO (m)") 						AS int) / 60 AS NVARCHAR(254)) + ':'  
+ 		RIGHT('0' + CAST(CAST((REPORT."Prazo Prioridade ANO (m)") 						AS int) % 60 AS NVARCHAR(254)), 2)
													AS "Prazo Prioridade ANO (h)"
--<<-------------------------------------------------------------------------------------------------------------------
,		REPORT."Prazo Prioridade CA (m)" 			AS "Prazo Prioridade CA (m)"
-->>-------------------------------------------------------------------------------------------------------------------
,		CAST(            CAST((REPORT."Prazo Prioridade CA (m)") 						AS int) / 60 AS NVARCHAR(254)) + ':'  
+ 		RIGHT('0' + CAST(CAST((REPORT."Prazo Prioridade CA (m)") 						AS int) % 60 AS NVARCHAR(254)), 2)													
													AS "Prazo Prioridade CA (h)"
--<<-------------------------------------------------------------------------------------------------------------------
,		REPORT."Tempo Total Evento (m)" 			AS "Tempo Total Evento (m)"
-->>-------------------------------------------------------------------------------------------------------------------
,		CAST(            CAST((REPORT."Tempo Total Evento (m)") 						AS int) / 60 AS NVARCHAR(254)) + ':'  
+ 		RIGHT('0' + CAST(CAST((REPORT."Tempo Total Evento (m)") 						AS int) % 60 AS NVARCHAR(254)), 2)													
													AS "Tempo Total Evento (h)"
--<<-------------------------------------------------------------------------------------------------------------------
,		REPORT."Tempo Util Evento (m)" 				AS "Tempo Util Evento (m)"
-->>-------------------------------------------------------------------------------------------------------------------
,		CAST(            CAST((REPORT."Tempo Util Evento (m)") 							AS int) / 60 AS NVARCHAR(254)) + ':'  
+ 		RIGHT('0' + CAST(CAST((REPORT."Tempo Util Evento (m)") 							AS int) % 60 AS NVARCHAR(254)), 2)													
													AS "Tempo Util Evento (h)"
--<<-------------------------------------------------------------------------------------------------------------------
,		REPORT."Tempo Util Atribuicao Mesa (m)" 	AS "Tempo Util Atribuição Mesa (m)"
-->>-------------------------------------------------------------------------------------------------------------------
,		CAST( 		     CAST((REPORT."Tempo Util Atribuicao Mesa (m)") 				AS int) / 60 AS NVARCHAR(254)) + ':'  
+ 		RIGHT('0' + CAST(CAST((REPORT."Tempo Util Atribuicao Mesa (m)") 				AS int) % 60 AS NVARCHAR(254)), 2)
													AS "Tempo Util Atribuição Mesa (h)"
--<<-------------------------------------------------------------------------------------------------------------------
,		REPORT."Tempo Util Atribuicao CA (m)" 		AS "Tempo Util Atribuição CA (m)"
-->>-------------------------------------------------------------------------------------------------------------------
,		CAST(            CAST((REPORT."Tempo Util Atribuicao CA (m)") 					AS int) / 60 AS NVARCHAR(254)) + ':'  
+ 		RIGHT('0' + CAST(CAST((REPORT."Tempo Util Atribuicao CA (m)") 					AS int) % 60 AS NVARCHAR(254)), 2)													
													AS "Tempo Util Atribuição CA (h)"
--<<-------------------------------------------------------------------------------------------------------------------													
,		REPORT."Vinculo" 							AS "Vinculo"
,		REPORT."Vinculo com Incidente Grave?" 		AS "Vinculo com Incidente Grave?"
,		REPORT."Incidente Grave?" 					AS "Incidente Grave?"
FROM	REPORT WITH (NOLOCK)
WHERE	1=1
ORDER	BY REPORT.INCIDENT_ID
,		REPORT.ACT_REG_ID
OPTION 	(EXPAND VIEWS, MAXDOP 8)