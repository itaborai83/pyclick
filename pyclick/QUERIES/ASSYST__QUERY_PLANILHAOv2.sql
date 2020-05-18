WITH PARAMS AS (
		SELECT 	CONVERT(DATETIME, '2020-05-04 00:00:00', 120) AS START_DT
		,		CONVERT(DATETIME, '2020-05-04 23:59:59', 120) AS END_DT
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
	AND 	INCIDENT.TYPE_ENUM 		IN (1, 4, 7) -- INCIDENTES, REQUISIÇÕES E TAREFAS
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
	AND 	INCIDENT.TYPE_ENUM 		IN (1, 4, 7) -- INCIDENTES, REQUISIÇÕES E TAREFAS
	AND		INCIDENT.DATE_LOGGED	< (SELECT END_DT FROM PARAMS)
	AND		( 	(1=1 AND INCIDENT.STATUS_ENUM = 2 AND INCIDENT.INC_CLOSE_DATE  BETWEEN (SELECT START_DT FROM PARAMS) AND (SELECT END_DT FROM PARAMS) ) OR -- ENCERRADOS 
				(1=1 AND INCIDENT.STATUS_ENUM = 3 AND INCIDENT.INC_RESOLVE_ACT BETWEEN (SELECT START_DT FROM PARAMS) AND (SELECT END_DT FROM PARAMS) ) )  -- RESOLVIDOS
),
ACTION_TYPES AS (
	SELECT	ACT_TYPE_ID 
	FROM 	ACT_TYPE
	WHERE	ACT_TYPE_ID IN (
		1,	 /* ATRIBUIÇÃO INTERNA                */ 4,	  /* RESOLVER                       */	
		5,	 /* ENCERRAR                          */ 6,	  /* REABRIR                        */	
		11,	 /* ATRIBUIR AO FORNECEDOR            */ 13,  /* RESPOSTA DO FORNECEDOR         */	
		14,	 /* RESOLVER FORNECEDOR - EXECUTAR ANTES DO "RESOLVER"!	*/	
		15,	 /* REABERTO PELO FORNECEDOR          */	
		18,	 /* CANCELADO                         */ 31,  /* CAMPO DO FORMULÁRIO ALTERADO   */	
		51,	 /* ALTERADO                          */ 52,  /* CATEGORIA ALTERADA             */	
		70,	 /* CAMPOS ALTERADOS                  */ 119, /* PENDÊNCIA SANADA               */	
		120, /* INICIAR RELÓGIO                   */ 121, /* PARAR RELÓGIO                  */	
		122, /* AGUARDANDO CLIENTE                */ 140, /* ATENDIMENTO PROGRAMADO         */	
		141, /* INICIAR ATENDIMENTO               */ 142, /* ATENDIMENTO AGENDADO           */	
		146, /* PENDENCIA DE FORNECEDOR           */ 147, /* PENDÊNCIA DE TIC               */	
		148, /* PENDÊNCIA SANADA FERIADO LOCAL    */ 149, /* PENDÊNCIA FERIADO LOCAL        */	
		150, /* PENDÊNCIA SANADA - FORNECEDOR/TIC */ 151, /* CANCELAR                       */	
		152, /* RETORNO DO USUÁRIO                */ 153, /* AGUARDANDO CLIENTE - APROVAÇÃO */	
		154, /* AGUARDANDO CLIENTE - FORNECEDOR   */ 155  /* PENDÊNCIA SANADA - APROVAÇÃO   */
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
	AND 	ACT_REG.ACT_TYPE_ID 	IN ( SELECT ACT_TYPE_ID FROM ACTION_TYPES ) --AÇÕES PRESENTES NO RELATORIO
	
),
CHANGE_FIELDS_ACTIONS AS (
			SELECT	ACT_TYPE_ID 
			FROM 	ACT_TYPE
			WHERE	ACT_TYPE_ID IN (
				1,		 /* Campo do formulário alterado   */	50,		 /* Usuário alterado               */	
				51,		 /* Item alterado                  */	52,		 /* Categoria alterada             */	
				53,		 /* Impacto alterado               */	54,		 /* Urgência alterada              */	
				55,		 /* Campo Indicador de inatividade alterado */	
				56,		 /* Data de registro alterada      */	58,		 /* Descrição alterada             */	
				59,		 /* Localidade alterada            */	60,		 /* Departamento de seção alterado */	
				61,		 /* Observação de Retorno Alterada */	62,		 /* Campo Cobrável Alterado        */	
				63,		 /* CSG Alterado                   */	70,		 /* Campos alterados               */	
				5000010, /* Requerido por                  */	5000011, /* Data de Início Agendada        */	
				5000012, /* Data de Término Agendada       */	5000013, /* SLA                            */	
				5000014, /* Descrição anterior             */	5000015, /* Usuários Vinculados Alterados  */	
				5000027, /* Flag de Retorno req alterada   */	5000028, /* Resumo alterado                */	
				5000029, /* Dep de serv resp alterado      */	5000030, /* Origem do evento alterada      */	
				5000031, /* Custo alterado                 */	5000032, /* Referência de usuário alterada */	
				5000033, /* Detalhes de autorização alter. */	5000034, /* Data de autorizaçao alterada   */	
				5000035, /* Justificativa alterada         */	5000036, /* Requisições adicionais alteradas */	
				5000037, /* Projeto alterado               */	5000038, /* Centro de custo alterado       */	
				5000045, /* Usuário responsável alterado   */	5000046, /* Dep Serviços Técnico alterado  */	
				5000047, /* Usuário técnico alterado       */	5000048, /* Dep de serv resp B alterado    */	
				5000049, /* Usuário responsável B alterado */	5000063	 /* Prioridade alterada			   */	
			) 
)
SELECT 	ACT_REG.act_reg_id
,		INCIDENT.type_enum
,		INCIDENT.incident_id
,		INCIDENT_PAI.incident_id 							AS incident_id_pai
,		(select date_logged 	from incs where incident_id = INCIDENT.incident_id) AS 'Data Abertura Chamado'
,		(select inc_resolve_act from incs where incident_id = INCIDENT.incident_id) AS 'Data Resolução Chamado'
,		CASE	WHEN INCIDENT.type_enum = 1 THEN '' 
				WHEN INCIDENT.type_enum = 2 THEN 'P'
				WHEN INCIDENT.type_enum = 3 THEN 'R'
				WHEN INCIDENT.type_enum = 7 THEN 'S'
				WHEN INCIDENT.type_enum = 5 THEN 'D'
				ELSE 'T' 
		END + CAST(INCIDENT.incident_ref AS varchar(10)) 	AS 'ID Chamado'
,		CASE	WHEN inc_data.u_num2 		= 0 THEN NULL
				WHEN INCIDENT_PAI.type_enum = 1 THEN '' 
				WHEN INCIDENT_PAI.type_enum = 2 THEN 'P'
				WHEN INCIDENT_PAI.type_enum = 3 THEN 'R'
				WHEN INCIDENT_PAI.type_enum = 7 THEN 'S'
				WHEN INCIDENT_PAI.type_enum = 5 THEN 'D'
				ELSE 'T' 
		END + CAST((
			SELECT 	INCIDENT_PAI.incident_ref 
			from 	incident 
			where 	incident_id = inc_data.u_num2 
			AND 	inc_data.u_num2 <> 0) as VARCHAR(10)
		)													AS 'Chamado Pai'
,		CASE
			WHEN inc_data.receive_type = 't' THEN 'Telefone'
			WHEN inc_data.receive_type = 'e' THEN 'Email'
			WHEN inc_data.receive_type = 'l' THEN 'Carta'
			WHEN inc_data.receive_type = 'f' THEN 'Monitoração'
			WHEN inc_data.receive_type = 'n' THEN 'assystNET'
			WHEN inc_data.receive_type = 'o' THEN 'Outro'
			WHEN inc_data.receive_type = 'i' THEN 'Processador de importação'
			WHEN inc_data.receive_type = 'c' THEN 'Chat'
			WHEN inc_data.receive_type = 'a' THEN 'Registro de Cobertura'
		END 												AS 'Origem Chamado'
,		USR_AFFECTED.usr_sc 								AS 'Usuário Afetado'
,		Usr_AFFECTED.usr_n 									AS 'Nome do Usuário Afetado'
,		USR_REPORTING.usr_sc 								AS 'Usuário Informante'
,		USR_REPORTING.usr_n									AS 'Nome do Usuário Informante'
,		DIVISION.division_n 								AS 'Organização Cliente'
,		CASE	WHEN SECTION_DEPT.dept_n IS NULL then SECTION_DEPT.sectn_n
				else SECTION_DEPT.dept_n
		END 												AS 'Departamento Cliente'
,		SITE_AREA.site_area_sc 								AS 'Estado'
,		BUILDING.bldng_n 									AS 'Site'
,		CASE	WHEN (
					select 	count(act_reg_id) 
					from 	act_reg
					where 	act_reg.incident_id = INCIDENT.incident_id 
					and 	act_reg.act_type_id = 1
				) > 1 
				THEN 'NÃO' ELSE 'Sim'
		END 												AS 'FCR'
,		CASE 	WHEN INCIDENT.status_enum = 1 THEN 'Aberto'
				WHEN INCIDENT.status_enum = 2 THEN 'Fechado'
				WHEN INCIDENT.status_enum = 3 THEN 'Resolvido'
				ELSE 'Enviado'
		END 												AS 'Status de evento'
,		INC_MAJOR_REGISTRO.inc_major_n	 					AS 'Categoria Maior'
,		INCIDENT.short_desc 								AS 'Resumo'
	--replace(inc_data.remarks,'<==# ADD','') AS 'Descrição Detalhada',
--	CASE
--		WHEN inc_data.remarks like '%No description entered. No Additional Information available.%' then NULL
--		ELSE inc_data.remarks
--	END 'Descrição Detalhada',
,		CASE	WHEN INCIDENT.type_enum IN (4,6) THEN ( 
					SELECT 	serv_n 
					from 	inc_data
							--
							inner join serv_off WITH(NOLOCK)
							on serv_off.serv_off_id = INC_DATA_PAI.serv_off_id
							--
							inner join serv WITH(NOLOCK) 
							on 	serv.serv_id = serv_off.serv_id
							--
					WHERE 	inc_data.incident_id = INC_DATA_PAI.incident_id
				)
				ELSE SERV.serv_n
		END 												AS 'Serviço Catálogo'
,	CLASSE_PRODUTO_REGISTRO.prod_cls_n 						AS 'Classe de Produto de Serviço'
,	PRODUTO_REGISTRO.product_n 								AS 'Produto de Serviço'
,	ITEM_REGISTRO.item_n 									AS 'Item de Serviço'
,	INC_CAT_REGISTRO.inc_cat_n 								AS 'Categoria'
,	CASE	WHEN INCIDENT.type_enum IN (4,6) THEN ( 
				SELECT 	serv_off_n 
				from 	inc_data
						--
						inner join serv_off WITH(NOLOCK) 
						on serv_off.serv_off_id = INC_DATA_PAI.serv_off_id
						--
						WHERE inc_data.incident_id = INC_DATA_PAI.incident_id
				)
			ELSE SERV_OFF.serv_off_n
	END 													AS 'Oferta Catálogo'
,		CLASSE_GENERICA_B.generic_cls_n 					AS 'Classe Genérica B'
,		CLASSE_PRODUTO_B.prod_cls_n 						AS 'Classe de Produto B'
,		PRODUTO_B.product_n 								AS 'Produto B'
,		SUPPLIER_PRODUCT_B.supplier_n 						AS 'Fabricante B'
,		ITEM_B_MODELO.item_n 								AS 'Item Modelo B'
,		ITEM_B.item_n 										AS 'Item B'
,		INC_CAT_CAUSA.inc_cat_n				 				AS 'Categoria Causa'
,		CLASSE_GENERICA_CAUSA.generic_cls_n 				AS 'Classe Genérica Causa'
,		CLASSE_PRODUTO_CAUSA.prod_cls_n 					AS 'Classe de Produto Causa'
,		PRODUTO_CAUSA.product_n 							AS 'Produto Causa'
,		SUPPLIER_PRODUCT_CAUSA.supplier_n 					AS 'Fabricante Causa'
,		ITEM_CAUSA_MODELO.item_n 							AS 'Item Modelo Causa'
,		ITEM_CAUSA.item_n		 							AS 'Item Causa'
--	CASE
--		WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'PENDING-CLOSURE') THEN ACT_REG.remarks
--		ELSE NULL
--	END 'Resolução',
,		CASE	WHEN ACT_TYPE.act_type_id = 4 THEN ACT_REG.remarks
				ELSE NULL
		END 												AS 'Resolução'
,		ACT_REG.act_reg_id AS 'ID Ação'
		-- Falta Tipo do Movimento
		-- Falta Movimento Nº
,		ACT_REG.date_actioned 								AS 'Data Inicio Ação'
,		CASE 	WHEN ACT_REG.act_reg_id = 	MAX(ACT_REG.act_reg_id) -- ACT_REG.last_action
											OVER (PARTITION BY ACT_REG.INCIDENT_ID) 
				THEN 'y' ELSE 'n' 
		END 												AS 'Ultima Ação' 
,		LEAD(ACT_REG.date_actioned) OVER (
			PARTITION BY ACT_REG.INCIDENT_ID
			ORDER BY ACT_REG.DATE_ACTIONED
		) 													AS 'Data Fim Ação'
,		CAST( CAST( (DATEDIFF(	minute, 
								ACT_REG.date_actioned, 
								LEAD(ACT_REG.date_actioned) OVER (PARTITION BY ACT_REG.INCIDENT_ID ORDER BY ACT_REG.DATE_ACTIONED) -- ACT_REG.next_date_actioned								
		)) AS int) AS varchar) 'Tempo Total da Ação (M)'
,		ACT_TYPE.act_type_n 								AS 'Ultima Ação Nome'
--		CASE
--			WHEN ACT_TYPE.user_status IN (SELECT user_status from act_type WHERE user_status IN ('c','u','l')) THEN ACT_REG.remarks
--			ELSE NULL
--		END 'Motivo Pendencia',
,		CASE	WHEN ACT_TYPE.user_status IN ('c','u','l') 
				THEN ACT_REG.remarks ELSE NULL
		END 												AS 'Motivo Pendencia'
,		CASE	WHEN ACT_TYPE.act_type_id IN 
				( SELECT ACT_TYPE_ID FROM CHANGE_FIELDS_ACTIONS )
				THEN ACT_REG.remarks ELSE NULL
		END 												AS 'Campos alterados'
,		CASE	WHEN ACT_TYPE.act_type_id = 51 
				-- Acao de mudanca de Item do formulario
				THEN ACT_REG.remarks ELSE NULL
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
,		CASE	WHEN ACT_TYPE.act_type_id = 1 
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
		END 												AS 'Descrição da Prioridade do CA' -- Remarks do CA aplicado ao fornecedor
,		INCIDENT.time_to_resolve 							AS 'Prazo Prioridade ANS (m)',	
		CASE	WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'ASSIGN') 
				THEN  ACT_REG.time_to_resolve
				ELSE NULL
		END 												AS 'Prazo Prioridade ANO (m)'
,		CASE	WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'SUPP-ASSIGN') THEN  ACT_REG.time_to_resolve
				ELSE NULL
		END 												AS 'Prazo Prioridade CA (m)'
,		DATEDIFF(minute, INCIDENT.date_logged, INCIDENT.inc_resolve_act) AS 'Tempo Total Evento (m)',
		INCIDENT.inc_resolve_sla 'Tempo Util Evento (m)'
		-- Falta Tempo Total de Atribuição Mesa (m)
,		CASE	WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'ASSIGN') THEN  ACT_REG.assignment_time
				ELSE NULL
		END 												AS 'Tempo Util Atribuição Mesa (m)'
		-- Falta Tempo Total de Atribuição CA (m)
,		CASE	WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'SUPP-ASSIGN') THEN  ACT_REG.assignment_time
				ELSE NULL
		END 												AS 'Tempo Util Atribuição CA (m)'
,		CASE	WHEN (	select count(link_inc_id) from link_inc 
						where link_inc.incident_id = INCIDENT.incident_id) > 0 
				THEN 'Sim' ELSE 'Não'
		END 												AS 'Vinculo'
,		CASE 	WHEN (
					select 	count(link_inc.incident_id) 
					from 	link_inc
							--
				            INNER JOIN link_grp WITH(NOLOCK)
	                    	ON link_grp.link_grp_id = link_inc.link_grp_id
	                    	--
	             			INNER JOIN link_rsn WITH(NOLOCK)
	                    	ON link_rsn.link_rsn_id = link_grp.link_rsn_id
	                    	--
     				WHERE 	link_rsn.link_rsn_n LIKE 'Incidente Grave' 
     				AND 	link_inc.incident_id = INCIDENT.incident_id
     				) > 0 
 				then 'Sim' ELSE 'Não'
		END 												AS 'Vinculo com Incidente Grave?'
,		CASE 	WHEN incident.major_inc = 0 
				then 	'Não' else 'Sim' END 				AS 'Incidente Grave?' 
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
		--
WHERE	1=1
ORDER	BY ACT_REG.INCIDENT_ID
,		ACT_REG.ACT_REG_ID
OPTION 	(MAXDOP 8)