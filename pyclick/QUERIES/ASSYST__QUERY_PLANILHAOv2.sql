WITH OPEN_INCS AS (
/*	
	SELECT	INCIDENT.INCIDENT_ID
	FROM 	INCIDENT INCIDENT WITH(NOLOCK)
	WHERE	1=2
			-- ID DE SISTEMA
	AND		INCIDENT.INCIDENT_ID 	<> 0
	AND 	INCIDENT.TYPE_ENUM 		IN (1,4,7) -- INCIDENTES, REQUISIÇÕES E TAREFAS
	AND		INCIDENT.DATE_LOGGED	 < CONVERT(DATETIME, '2020-03-01 23:59:59', 120)
	AND		( 	(1=1 AND INCIDENT.STATUS_ENUM = 1 AND INCIDENT.INC_RESOLVE_ACT IS NULL) 										OR -- ABERTOS
				(1=1 AND INCIDENT.STATUS_ENUM = 2 AND INCIDENT.INC_CLOSE_DATE  > CONVERT(DATETIME, '2020-03-01 23:59:59', 120)) OR -- ENCERRADOS 
				(1=1 AND INCIDENT.STATUS_ENUM = 3 AND INCIDENT.INC_RESOLVE_ACT > CONVERT(DATETIME, '2020-03-01 23:59:59', 120)) )  -- RESOLVIDOS 				
*/
	SELECT 	INCIDENT_ID 
	FROM 	INCIDENT 
	WHERE 	INCIDENT_REF in (				
		'110322', '114881',  '11540', '116109', '11718', '117232', '117300', '118217', '119773', '125087',
		'127610', '129120', '130521', '13134', '132180', '132620', '132740', '136216', '138902', '139132',
		'13960', '141377', '14459', '144814', '144921', '145367', '146435', '146620', '1473 ', '150117', 
		'150363', '1508 ', '15211', '155606', '155725', '155877', '156625', '157353', '157786', '163659',
		'168345', '168484', '169438', '173599', '174792', '176534', '176688', '177895', '178928', '183049',
		'189776', '197490', '201942', '21030', '213150', '21342', '225713', '23017', '231241', '23448', 
		'2346', '235649', '243764', '251022', '256558', '268241', '27865', '27881', '279621', '279939', 
		'28481', '290501', '290888', '292171', '297144', '301946', '303332', '303648', '304842', '305097',
		'30576', '307555', '307645', '309816', '310299', '310880', '311059', '312607', '314502', '315451',
		'317886', '317978', '321329', '321773', '322255', '323659', '323808', '324110', '32428', '324825'
	)				
),
ACTION_TYPES AS (
	SELECT	ACT_TYPE_ID 
	FROM 	ACT_TYPE
	WHERE	ACT_TYPE_ID IN (
				1,		--	ASSIGN	ATRIBUIÇÃO INTERNA
				4,		--	PENDING-CLOSURE	RESOLVER
				5,		--	CLOSURE	ENCERRAR
				6,		--	RE-OPEN	REABRIR
				11,		--	SUPP-ASSIGN	ATRIBUIR AO FORNECEDOR
				13,		--	SUPP-RESPONSE	RESPOSTA DO FORNECEDOR
				14,		--	SUPP-RESOLVE	RESOLVER FORNECEDOR - EXECUTAR ANTES DO "RESOLVER"!
				15,		--	SUPP-REOPEN	REABERTO PELO FORNECEDOR
				18,		--	CANCELLED	CANCELADO
				31,		--	CHGWEBPROPERTY	CAMPO DO FORMULÁRIO ALTERADO
				51,		--	CHGITEM	ITEM ALTERADO
				52,		--	CHGCATEGORY	CATEGORIA ALTERADA
				70,		--	CHGFIELDS	CAMPOS ALTERADOS
				119,	--	PEN SAN	PENDÊNCIA SANADA
				120,	--	START.CLOCK	INICIAR RELÓGIO
				121,	--	STOP.CLOCK	PARAR RELÓGIO
				122,	--	WAIT ON CUST	AGUARDANDO CLIENTE
				140,	--	ATEND-PROGRAMADO	ATENDIMENTO PROGRAMADO
				141,	--	INICIAR-ATENDIMENTO	INICIAR ATENDIMENTO
				142,	--	ATEND-AGENDADO	ATENDIMENTO AGENDADO
				146,	--	PENDENCIA FORNECEDOR	PENDENCIA DE FORNECEDOR
				147,	--	PENDENCIA TAREFA TIC	PENDÊNCIA DE TIC
				148,	--	PENDENCIA SANADA FERIADO LOCAL	PENDÊNCIA SANADA FERIADO LOCAL
				149,	--	PENDENCIA FERIADO LOCAL	PENDÊNCIA FERIADO LOCAL
				150,	--	PENDENCIA SANADA DO FORNECEDOR	PENDÊNCIA SANADA - FORNECEDOR/TIC
				151,	--	CANCELAR	CANCELAR
				152,	--	RETORNO USUARIO	RETORNO DO USUÁRIO
				153,	--	AGUARDANDO USUARIO_APROVACAO	AGUARDANDO CLIENTE - APROVAÇÃO
				154,	--	AGUARDANDO USUARIO _FORNECEDOR	AGUARDANDO CLIENTE - FORNECEDOR
				155		--	RETOMAR RELOGIO_APROVACAO	PENDÊNCIA SANADA - APROVAÇÃO
	)
),
CHANGE_FIELDS_ACTIONS AS (
	SELECT	ACT_TYPE_ID 
	FROM 	ACT_TYPE
	WHERE	ACT_TYPE_ID IN (
				31,			-- CHGWEBPROPERTY	Campo do formulário alterado
				50,			-- CHGUSER			Usuário alterado
				51,			-- CHGITEM			Item alterado
				52,			-- CHGCATEGORY		Categoria alterada
				53,			-- CHGIMPACT		Impacto alterado
				54,			-- CHGURGENCY		Urgência alterada
				55,			-- CHGDOWNFLAG		Campo Indicador de inatividade alterado
				56,			-- CHGLOGDATE		Data de registro alterada
				58,			-- CHGDESC			Descrição alterada
				59,			-- CHGLOCATION		Localidade alterada
				60,			-- CHGSECTDEPT		Departamento de seção alterado
				61,			-- CHGREMARKS		Observação de Retorno Alterada
				62,			-- CHGCHARGEFLAG	Campo Cobrável Alterado
				63,			-- CHGCSG			CSG Alterado
				70,			-- CHGFIELDS		Campos alterados
				5000010,	-- CHGREQDBYDATE	Requerido por
				5000011,	-- CHGSCHDSTADATE	Data de Início Agendada
				5000012,	-- CHGSCHDENDDATE	Data de Término Agendada
				5000013,	-- CHGSLA			SLA
				5000014,	-- CHGPREVDESC		Descrição anterior
				5000015,	-- CHGADDITIONLUSR	Usuários Vinculados Alterados
				5000027,	-- CHGCALLBACKFLAG	Flag de Retorno req alterada
				5000028,	-- CHGSUMMARY		Resumo alterado
				5000029,	-- CHGRESPSERVDEPT	Dep de serv resp alterado
				5000030,	-- CHGEVENTSRC		Origem do evento alterada
				5000031,	-- CHGCOST			Custo alterado
				5000032,	-- CHGUSERREF		Referência de usuário alterada
				5000033,	-- CHGAUTHDETAILS	Detalhes de autorização alter.
				5000034,	-- CHGAUTHDATE		Data de autorizaçao alterada
				5000035,	-- CHGJUSTIFICATN	Justificativa alterada
				5000036,	-- CHGADDREQ		Requisições adicionais alteradas
				5000037,	-- CHGPROJECT		Projeto alterado
				5000038,	-- CHGCOSTCENTER	Centro de custo alterado
				5000045,	-- CHGRESPUSER		Usuário responsável alterado
				5000046,	-- CHGTECHSVD		Dep Serviços Técnico alterado
				5000047,	-- CHGTECHUSER		Usuário técnico alterado
				5000048,	-- CHGRESPSVDB		Dep de serv resp B alterado
				5000049,	-- CHGRESPUSERB		Usuário responsável B alterado
				5000063		-- CHGPRIORITY		Prioridade alterada			
			) 
)
SELECT 	ACT_REG.act_reg_id
,		INCIDENT.type_enum
,		INCIDENT.incident_id
,		INCIDENT_PAI.incident_id 							AS incident_id_pai
,		INCIDENT.date_logged 								AS 'Data Abertura Chamado'
,		INCIDENT.inc_resolve_act 							AS 'Data Resolução Chamado'
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
				then 'NÃO'
				ELSE 'Sim'
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
,		ACT_REG.last_action 								AS 'Ultima Ação'
,		ACT_REG.next_date_actioned 							AS 'Data Fim Ação'
,		CAST( CAST((DATEDIFF(minute, ACT_REG.date_actioned, ACT_REG.next_date_actioned)) AS int) AS varchar) 'Tempo Total da Ação (M)'
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
		then 'Não' else 'Sim' END 							AS 'Incidente Grave?' 
from 	(
			SELECT act_reg.*, LEAD(date_actioned) OVER (PARTITION BY incident_id ORDER BY date_actioned) as next_date_actioned FROM act_reg
		) AS ACT_REG
		--
		INNER JOIN incident INCIDENT WITH(NOLOCK)
		ON INCIDENT.incident_id 										= ACT_REG.incident_id 
		--
		INNER JOIN serv_dept SERV_DEPT WITH(NOLOCK)
		ON SERV_DEPT.serv_dept_id 										= ACT_REG.ass_svd_id
		--
		INNER JOIN supplier SUPPLIER WITH(NOLOCK)
		ON SUPPLIER.supplier_id 										= ACT_REG.supplier_id
		--
		INNER JOIN act_type ACT_TYPE WITH(NOLOCK)
		ON ACT_TYPE.act_type_id 										= ACT_REG.act_type_id 
		--
		INNER JOIN inc_data  WITH(NOLOCK)
		ON inc_data.incident_id 										= INCIDENT.incident_id 
		--
		INNER JOIN incident INCIDENT_PAI  WITH(NOLOCK)
		ON INCIDENT_PAI.incident_id 									= inc_data.u_num2 
		--
		INNER JOIN inc_data INC_DATA_PAI WITH(NOLOCK)
		ON INC_DATA_PAI.incident_id 									= inc_data.u_num2 
		--
		INNER JOIN inc_cat INC_CAT_REGISTRO  WITH(NOLOCK)
		ON INC_CAT_REGISTRO.inc_cat_id 									= INCIDENT.inc_cat_id 
		--
		INNER JOIN inc_major INC_MAJOR_REGISTRO  WITH(NOLOCK)
		ON INC_MAJOR_REGISTRO.inc_major_id 								= INC_CAT_REGISTRO.inc_major_id 
		--
		INNER JOIN serv_off SERV_OFF WITH(NOLOCK)
		ON SERV_OFF.serv_off_id 										= inc_data.serv_off_id 
		--
		INNER JOIN serv SERV WITH(NOLOCK)
		ON SERV.serv_id 												= SERV_OFF.serv_id 
		--
		INNER JOIN item ITEM_REGISTRO  WITH(NOLOCK)
		ON ITEM_REGISTRO.item_id 										= INCIDENT.item_id 
		--
		INNER JOIN product PRODUTO_REGISTRO WITH(NOLOCK) 
		ON PRODUTO_REGISTRO.product_id 									= ITEM_REGISTRO.product_id 
		--
		INNER JOIN prod_cls CLASSE_PRODUTO_REGISTRO WITH(NOLOCK)
		ON CLASSE_PRODUTO_REGISTRO.prod_cls_id 							= PRODUTO_REGISTRO.prod_cls_id 
		--
		INNER JOIN generic_cls CLASSE_GENERICA_REGISTRO  WITH(NOLOCK)
		ON CLASSE_GENERICA_REGISTRO.generic_cls_id 						= CLASSE_PRODUTO_REGISTRO.generic_cls_id 
		--
		INNER JOIN item ITEM_B  WITH(NOLOCK)
		ON ITEM_B.item_id 												= inc_data.item_b_id
		--
		INNER JOIN product PRODUTO_B  WITH(NOLOCK)
		ON PRODUTO_B.product_id 										= ITEM_B.product_id 
		--
		INNER JOIN item ITEM_B_MODELO WITH(NOLOCK)
		ON ITEM_B_MODELO.item_id 										= PRODUTO_B.model_item_id 
		--
		INNER JOIN prod_cls CLASSE_PRODUTO_B WITH(NOLOCK)
		ON CLASSE_PRODUTO_B.prod_cls_id 								= PRODUTO_B.prod_cls_id 
		--
		INNER JOIN generic_cls CLASSE_GENERICA_B WITH(NOLOCK)
		ON CLASSE_GENERICA_B.generic_cls_id 							= CLASSE_PRODUTO_B.generic_cls_id 
		--
		INNER JOIN inc_cat INC_CAT_CAUSA  WITH(NOLOCK)
		ON INC_CAT_CAUSA.inc_cat_id 									= INCIDENT.cause_id 
		--
		INNER JOIN supplier SUPPLIER_PRODUCT_B WITH(NOLOCK)
		ON PRODUTO_B.supplier_id 										= SUPPLIER_PRODUCT_B.supplier_id 
		--
		INNER JOIN item ITEM_CAUSA  WITH(NOLOCK)
		ON ITEM_CAUSA.item_id 											= incident.cause_item_id 
		--
		INNER JOIN supplier SUPPLIER_CAUSA_ITEM WITH(NOLOCK)
		ON ITEM_CAUSA.inv_supp_id 										= SUPPLIER_CAUSA_ITEM.supplier_id 
		--
		INNER JOIN product PRODUTO_CAUSA  WITH(NOLOCK)
		ON PRODUTO_CAUSA.product_id 									= ITEM_CAUSA.product_id 
		--
		INNER JOIN prod_cls CLASSE_PRODUTO_CAUSA WITH(NOLOCK)
		ON CLASSE_PRODUTO_CAUSA.prod_cls_id 							= PRODUTO_CAUSA.prod_cls_id 
		--
		INNER JOIN item ITEM_CAUSA_MODELO WITH(NOLOCK)
		ON ITEM_CAUSA_MODELO.item_id 									= PRODUTO_CAUSA.model_item_id
		--
		INNER JOIN generic_cls CLASSE_GENERICA_CAUSA  WITH(NOLOCK)
		ON CLASSE_GENERICA_CAUSA.generic_cls_id 						= CLASSE_PRODUTO_CAUSA.generic_cls_id
		--
		INNER JOIN supplier SUPPLIER_PRODUCT_CAUSA WITH(NOLOCK)
		ON PRODUTO_CAUSA.supplier_id 									= SUPPLIER_PRODUCT_CAUSA.supplier_id
		--
		INNER JOIN priority_derived PRIORITY_DERIVED WITH(NOLOCK)
		ON  PRIORITY_DERIVED.priority_derived_id 						= inc_data.priority_derived_id
		--
		INNER JOIN usr USR_AFFECTED WITH(NOLOCK)
		ON USR_AFFECTED.usr_id 											= INCIDENT.aff_usr_id
		--
		INNER JOIN usr USR_REPORTING WITH(NOLOCK)
		ON USR_REPORTING.usr_id 										= INCIDENT.rep_usr_id
		--
		INNER JOIN sectn_dept SECTION_DEPT WITH(NOLOCK)
		ON SECTION_DEPT.sectn_dept_id 									= INCIDENT.sectn_dept_id
		--
		INNER JOIN sectn SECTION WITH(NOLOCK)
		ON SECTION.sectn_id 											= SECTION_DEPT.sectn_id
		--
		INNER JOIN branch BRANCH WITH(NOLOCK)
		ON BRANCH.branch_id 											= SECTION.branch_id
		--
		INNER JOIN division DIVISION WITH(NOLOCK)
		ON DIVISION.division_id 										= BRANCH.division_id
		--
		INNER JOIN bldng_room BUILDING_ROOM
		ON BUILDING_ROOM.bldng_room_id 									= INCIDENT.bldng_room_id
		--
		INNER JOIN bldng BUILDING WITH(NOLOCK)
		ON BUILDING.bldng_id 											= BUILDING_ROOM.bldng_id
		--
		INNER JOIN site SITE WITH(NOLOCK)
		ON SITE.site_id 												= BUILDING.site_id
		--
		INNER JOIN site_area SITE_AREA WITH(NOLOCK)
		ON SITE_AREA.site_area_id 										= SITE.site_area_id
		--
WHERE	1=1 
AND		INCIDENT.incident_id 					> 0 -- Id de sistema
AND 	INCIDENT.type_enum 						IN ( 1, 4, 7 ) -- Incidentes, requisições e tarefas
AND 	ACT_REG.act_type_id 					IN ( SELECT ACT_TYPE_ID FROM ACTION_TYPES ) --ações Presentes no relatorio
AND 	CLASSE_GENERICA_REGISTRO.generic_cls_sc IN ('SERVICOS DE TIC', 'SOFTWARE' )
AND 	INCIDENT.INCIDENT_ID 					IN ( SELECT INCIDENT_ID FROM OPEN_INCS )
AND 	ACT_REG.INCIDENT_ID 					IN ( SELECT INCIDENT_ID FROM OPEN_INCS )
ORDER	BY ACT_REG.INCIDENT_ID
,		ACT_REG.ACT_REG_ID

