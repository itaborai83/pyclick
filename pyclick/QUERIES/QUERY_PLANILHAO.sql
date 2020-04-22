SELECT 
	--ACT_REG.act_reg_id, --Distinguir as ações
	--INCIDENT.type_enum, -- apenas por constar em ORDER BY
	--INCIDENT.incident_id, -- apenas por constar em ORDER BY
	--INCIDENT_PAI.incident_id as incident_id_pai, -- apenas por constar em ORDER BY
	INCIDENT.date_logged AS 'Data Abertura Chamado',
	INCIDENT.inc_resolve_act AS 'Data Resolução Chamado',
	'"' + REPLACE(REPLACE(CAST(CASE
		WHEN INCIDENT.type_enum = 1 THEN '' + CAST(INCIDENT.incident_ref AS varchar(10))
		WHEN INCIDENT.type_enum = 2 THEN 'P' + CAST(INCIDENT.incident_ref AS varchar(10))
		WHEN INCIDENT.type_enum = 3 THEN 'R' + CAST(INCIDENT.incident_ref AS varchar(10))
		WHEN INCIDENT.type_enum = 7 THEN 'S' + CAST(INCIDENT.incident_ref AS varchar(10))
		WHEN INCIDENT.type_enum = 5 THEN 'D' + CAST(INCIDENT.incident_ref AS varchar(10))
	ELSE 'T' + CAST(INCIDENT.incident_ref AS varchar(10))
	END AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'ID Chamado',
	'"' + REPLACE(REPLACE(CAST(CASE
		WHEN INCIDENT_PAI.type_enum = 1 THEN ' ' + CAST((SELECT INCIDENT_PAI.incident_ref from incident where incident_id = inc_data.u_num2) AS varchar(10))
		WHEN INCIDENT_PAI.type_enum = 2 THEN 'P' + CAST((SELECT INCIDENT_PAI.incident_ref from incident where incident_id = inc_data.u_num2) AS varchar(10))
		WHEN INCIDENT_PAI.type_enum = 3 THEN 'R' + CAST((SELECT INCIDENT_PAI.incident_ref from incident where incident_id = inc_data.u_num2) AS varchar(10))
		WHEN INCIDENT_PAI.type_enum = 7 THEN 'S' + CAST((SELECT INCIDENT_PAI.incident_ref from incident where incident_id = inc_data.u_num2) AS varchar(10))
		WHEN inc_data.u_num2 = 0 THEN ''
	END AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Chamado Pai',
	'"' + REPLACE(REPLACE(CAST(CASE
		WHEN inc_data.receive_type = 't' THEN 'Telefone'
		WHEN inc_data.receive_type = 'e' THEN 'Email'
		WHEN inc_data.receive_type = 'l' THEN 'Carta'
		WHEN inc_data.receive_type = 'f' THEN 'Monitoração'
		WHEN inc_data.receive_type = 'n' THEN 'assystNET'
		WHEN inc_data.receive_type = 'o' THEN 'Outro'
		WHEN inc_data.receive_type = 'i' THEN 'Processador de importação'
		WHEN inc_data.receive_type = 'c' THEN 'Chat'
		WHEN inc_data.receive_type = 'a' THEN 'Registro de Cobertura'
	END AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Origem Chamado',
	'"' + REPLACE(REPLACE(CAST(USR_AFFECTED.usr_sc AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Usuário Afetado',
	'"' + REPLACE(REPLACE(CAST(Usr_AFFECTED.usr_n AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Nome do Usuário Afetado',
	'"' + REPLACE(REPLACE(CAST(USR_REPORTING.usr_sc AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Usuário Informante',
	'"' + REPLACE(REPLACE(CAST(USR_REPORTING.usr_n AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Nome do Usuário Informante',
	'"' + REPLACE(REPLACE(CAST(DIVISION.division_n AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Organização Cliente',
	'"' + REPLACE(REPLACE(CAST(CASE
		WHEN SECTION_DEPT.dept_n IS NULL then SECTION_DEPT.sectn_n
		else SECTION_DEPT.dept_n
	END AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Departamento Cliente',
	SITE_AREA.site_area_sc 'Estado',
	BUILDING.bldng_n 'Site',
	CASE
		WHEN (select count(act_reg_id) from act_reg where act_reg.incident_id = INCIDENT.incident_id and act_reg.act_type_id = 1) > 1 then 'NÃO'
		ELSE 'Sim'
	END 'FCR',
	CASE 
		WHEN INCIDENT.status_enum = 1 THEN 'Aberto'
		WHEN INCIDENT.status_enum = 2 THEN 'Fechado'
		WHEN INCIDENT.status_enum = 3 THEN 'Resolvido'
		ELSE 'Enviado'
	END 'Status de evento',
	INC_MAJOR_REGISTRO.inc_major_n AS 'Categoria Maior',
	'"' + REPLACE(REPLACE(CAST(replace(INCIDENT.short_desc,'"','') AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' AS 'Resumo',
	--replace(inc_data.remarks,'<==# ADD','') AS 'Descrição Detalhada',
--	CASE
--		WHEN inc_data.remarks like '%No description entered. No Additional Information available.%' then NULL
--		ELSE inc_data.remarks
--	END 'Descrição Detalhada',
	'"' + REPLACE(REPLACE(CAST(CASE
		WHEN INCIDENT.type_enum IN (4,6) THEN ( SELECT serv_n from inc_data
			inner join serv_off WITH(NOLOCK) on serv_off.serv_off_id = INC_DATA_PAI.serv_off_id
			inner join serv WITH(NOLOCK) on serv.serv_id = serv_off.serv_id
			WHERE inc_data.incident_id = INC_DATA_PAI.incident_id)
		
		ELSE SERV.serv_n
	END AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Serviço Catálogo',
	CLASSE_PRODUTO_REGISTRO.prod_cls_n AS 'Classe de Produto de Serviço',
	PRODUTO_REGISTRO.product_n AS 'Produto de Serviço',
	ITEM_REGISTRO.item_n AS 'Item de Serviço',
	INC_CAT_REGISTRO.inc_cat_n AS 'Categoria',
	CASE
		WHEN INCIDENT.type_enum IN (4,6) THEN ( SELECT serv_off_n from inc_data
			inner join serv_off WITH(NOLOCK) on serv_off.serv_off_id = INC_DATA_PAI.serv_off_id
			WHERE inc_data.incident_id = INC_DATA_PAI.incident_id)
		
		ELSE SERV_OFF.serv_off_n
	END 'Oferta Catálogo',
	CLASSE_GENERICA_B.generic_cls_n AS 'Classe Genérica B',
	CLASSE_PRODUTO_B.prod_cls_n AS 'Classe de Produto B',
	PRODUTO_B.product_n AS 'Produto B',
	SUPPLIER_PRODUCT_B.supplier_n AS 'Fabricante B',
	ITEM_B_MODELO.item_n AS 'Item Modelo B',
	ITEM_B.item_n AS 'Item B',
	INC_CAT_CAUSA.inc_cat_n AS 'Categoria Causa',
	CLASSE_GENERICA_CAUSA.generic_cls_n AS 'Classe Genérica Causa',
	CLASSE_PRODUTO_CAUSA.prod_cls_n AS 'Classe de Produto Causa',
	PRODUTO_CAUSA.product_n AS 'Produto Causa',
	SUPPLIER_PRODUCT_CAUSA.supplier_n AS 'Fabricante Causa',
	ITEM_CAUSA_MODELO.item_n AS 'Item Modelo Causa',
	ITEM_CAUSA.item_n AS 'Item Causa',
--	CASE
--		WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'PENDING-CLOSURE') THEN ACT_REG.remarks
--		ELSE NULL
--	END 'Resolução',
	'"' + REPLACE(REPLACE(CAST(CASE
		WHEN ACT_TYPE.act_type_id = 4 THEN ACT_REG.remarks
		ELSE NULL
	END AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Resolução', 
	ACT_REG.act_reg_id AS 'ID Ação',
	-- Falta Tipo do Movimento
	-- Falta Movimento Nº

	ACT_REG.date_actioned AS 'Data Inicio Ação',
	ACT_REG.last_action AS 'Ultima Ação',

	ACT_REG.next_date_actioned 'Data Fim Ação',	
	CAST( CAST((DATEDIFF(minute, ACT_REG.date_actioned, ACT_REG.next_date_actioned)) AS int) / 60 AS varchar) + ':'  + right('0' + CAST(CAST((DATEDIFF(minute, ACT_REG.date_actioned, ACT_REG.next_date_actioned)) AS int) % 60 AS varchar(2)),2) 'Tempo Total da Ação (h)',
	CAST( CAST((DATEDIFF(minute, ACT_REG.date_actioned, ACT_REG.next_date_actioned)) AS int) AS varchar) 'Tempo Total da Ação (M)',

	ACT_TYPE.act_type_n AS 'Ultima Ação Nome',
--	CASE
--		WHEN ACT_TYPE.user_status IN (SELECT user_status from act_type WHERE user_status IN ('c','u','l')) THEN ACT_REG.remarks
--		ELSE NULL
--	END 'Motivo Pendencia',
	'"' + REPLACE(REPLACE(CAST(CASE
		WHEN ACT_TYPE.user_status IN ('c','u','l') THEN ACT_REG.remarks
		ELSE NULL
	END AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Motivo Pendencia',
	'"' + REPLACE(REPLACE(CAST(CASE
		WHEN ACT_TYPE.act_type_id IN (5000015,5000036,5000034,5000033,5000027,52,62,5000031, -- Acoes de mudanca de campo no formulario
		5000038,63,58,55,5000030,70,53,51,5000035,59,56,5000014,5000063,5000037,61,5000010,
		5000029,5000048,5000045,5000049,5000012,5000011,60,5000013,5000028,5000046,5000047,
		54,50,5000032,31) THEN ACT_REG.remarks
		ELSE NULL
	END AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Campos alterados',
	'"' + REPLACE(REPLACE(CAST(CASE
		WHEN ACT_TYPE.act_type_id = 51 THEN ACT_REG.remarks -- Acao de mudanca de Item do formulario
		ELSE NULL
	END AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Itens alterados',
	CASE
		WHEN ACT_REG.supplier_id <> 0 THEN (SELECT sla.sla_n from supplier INNER JOIN sla ON sla.sla_id = supplier.dflt_sla_id WHERE supplier_id = ACT_REG.supplier_id)
		ELSE NULL
	END 'Nome do CA',
	CASE
		WHEN ACT_REG.supplier_id <> 0 THEN (SELECT supplier_n from supplier WHERE supplier_id = ACT_REG.supplier_id)
		ELSE NULL
	END 'Contrato',
	CASE
		WHEN ACT_TYPE.act_type_id = 1 THEN (select serv_dept_n from serv_dept where serv_dept_id = ACT_REG.ass_svd_id)
		ELSE NULL
	END 'Mesa',
	CASE
		WHEN ACT_TYPE.act_type_id = 1 THEN (select assyst_usr_n from assyst_usr where assyst_usr_id = ACT_REG.ass_usr_id)
		ELSE NULL
	END 'Designado',
	CASE
		WHEN ACT_TYPE.act_type_id = 1 THEN (select serv_dept.serv_dept_n from assyst_usr inner join serv_dept on serv_dept.serv_dept_id = assyst_usr.serv_dept_id where assyst_usr_id = ACT_REG.ass_usr_id)
		ELSE NULL
	END 'Grupo Default',
	PRIORITY_DERIVED.priority_derived_n 'Prioridade do CA',
	'"' + REPLACE(REPLACE(CAST(CASE
		WHEN ACT_REG.supplier_id <> 0 THEN (SELECT sla.sla_rmk from supplier INNER JOIN sla ON sla.sla_id = supplier.dflt_sla_id WHERE supplier_id = ACT_REG.supplier_id)
		ELSE NULL
	END AS VARCHAR(254)),CHAR(13),' '),CHAR(10),' ') + '"' 'Descrição da Prioridade do CA', -- Remarks do CA aplicado ao fornecedor
	INCIDENT.time_to_resolve 'Prazo Prioridade ANS (m)',
	CAST( CAST((INCIDENT.time_to_resolve) AS int) / 60 AS varchar) + ':'  + right('0' + CAST(CAST((INCIDENT.time_to_resolve) AS int) % 60 AS varchar(2)),2) 'Prazo Prioridade ANS (h)',	
	CASE
		WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'ASSIGN') THEN  ACT_REG.time_to_resolve
		ELSE NULL
	END 'Prazo Prioridade ANO (m)',
	CASE
		WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'ASSIGN') THEN 
		CAST( CAST((ACT_REG.time_to_resolve) AS int) / 60 AS varchar) + ':'  + right('0' + CAST(CAST((ACT_REG.time_to_resolve) AS int) % 60 AS varchar(2)),2)
		ELSE NULL
	END 'Prazo Prioridade ANO (h)',
	CASE
		WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'SUPP-ASSIGN') THEN  ACT_REG.time_to_resolve
		ELSE NULL
	END 'Prazo Prioridade CA (m)', 
	CASE
		WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'SUPP-ASSIGN') THEN 
		CAST( CAST((ACT_REG.time_to_resolve) AS int) / 60 AS varchar) + ':'  + right('0' + CAST(CAST((ACT_REG.time_to_resolve) AS int) % 60 AS varchar(2)),2)
		ELSE NULL
	END 'Prazo Prioridade CA (h)', 
	DATEDIFF(minute, INCIDENT.date_logged, INCIDENT.inc_resolve_act) 'Tempo Total Evento (m)',
	CAST( CAST((DATEDIFF(minute, INCIDENT.date_logged, INCIDENT.inc_resolve_act)) AS int) / 60 AS varchar) + ':'  + right('0' + CAST(CAST((DATEDIFF(minute, INCIDENT.date_logged, INCIDENT.inc_resolve_act)) AS int) % 60 AS varchar(2)),2) 'Tempo Total Evento (h)',
	INCIDENT.inc_resolve_sla 'Tempo Util Evento (m)',
	CAST( CAST((INCIDENT.inc_resolve_sla) AS int) / 60 AS varchar) + ':'  + right('0' + CAST(CAST((INCIDENT.inc_resolve_sla) AS int) % 60 AS varchar(2)),2) 'Tempo Util Evento (h)',
	-- Falta Tempo Total de Atribuição Mesa (m)
	CASE
		WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'ASSIGN') THEN  ACT_REG.assignment_time
		ELSE NULL
	END 'Tempo Util Atribuição Mesa (m)',
	CASE
		WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'ASSIGN') THEN 
		CAST( CAST((ACT_REG.assignment_time) AS int) / 60 AS varchar) + ':'  + right('0' + CAST(CAST((ACT_REG.assignment_time) AS int) % 60 AS varchar(2)),2)
		ELSE NULL
	END 'Tempo Util Atribuição Mesa (h)',
	
	-- Falta Tempo Total de Atribuição CA (m)
	CASE
		WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'SUPP-ASSIGN') THEN  ACT_REG.assignment_time
		ELSE NULL
	END 'Tempo Util Atribuição CA (m)',
	CASE
		WHEN ACT_TYPE.act_type_sc = (SELECT act_type_sc from act_type WHERE act_type_sc = 'SUPP-ASSIGN') THEN 
		CAST( CAST((ACT_REG.assignment_time) AS int) / 60 AS varchar) + ':'  + right('0' + CAST(CAST((ACT_REG.assignment_time) AS int) % 60 AS varchar(2)),2)
		ELSE NULL
	END 'Tempo Util Atribuição CA (h)',
	CASE
		WHEN (select count(link_inc_id) from link_inc where link_inc.incident_id = INCIDENT.incident_id) > 0 then 'Sim' 
		ELSE 'Não'
	END 'Vinculo',
	CASE 
             WHEN (select count(link_inc.incident_id) from link_inc
             INNER JOIN link_grp WITH(NOLOCK)
                    ON link_grp.link_grp_id = link_inc.link_grp_id
             INNER JOIN link_rsn WITH(NOLOCK)
                    ON link_rsn.link_rsn_id = link_grp.link_rsn_id
             WHERE link_rsn.link_rsn_n LIKE 'Incidente Grave' AND link_inc.incident_id = INCIDENT.incident_id) > 0 then 'Sim'
             ELSE 'Não'
	END 'Vinculo com Incidente Grave?',
	CASE 
			WHEN incident.major_inc = 0 then 'Não' else 'Sim' 
	END 'Incidente Grave?' 
from (SELECT act_reg.*, LEAD(date_actioned) OVER (PARTITION BY incident_id ORDER BY date_actioned) as next_date_actioned FROM act_reg) ACT_REG
INNER JOIN incident INCIDENT WITH(NOLOCK)
	ON INCIDENT.incident_id = ACT_REG.incident_id 
INNER JOIN serv_dept SERV_DEPT WITH(NOLOCK)
	ON SERV_DEPT.serv_dept_id = ACT_REG.ass_svd_id
INNER JOIN supplier SUPPLIER WITH(NOLOCK)
	ON SUPPLIER.supplier_id = ACT_REG.supplier_id
INNER JOIN act_type ACT_TYPE WITH(NOLOCK)
	ON ACT_TYPE.act_type_id = ACT_REG.act_type_id 
INNER JOIN inc_data  WITH(NOLOCK)
	ON inc_data.incident_id = INCIDENT.incident_id 
INNER JOIN incident INCIDENT_PAI  WITH(NOLOCK)
	ON INCIDENT_PAI.incident_id = inc_data.u_num2 
INNER JOIN inc_data INC_DATA_PAI WITH(NOLOCK)
	ON INC_DATA_PAI.incident_id = inc_data.u_num2 
INNER JOIN inc_cat INC_CAT_REGISTRO  WITH(NOLOCK)
	ON INC_CAT_REGISTRO.inc_cat_id = INCIDENT.inc_cat_id 
INNER JOIN inc_major INC_MAJOR_REGISTRO  WITH(NOLOCK)
	ON INC_MAJOR_REGISTRO.inc_major_id = INC_CAT_REGISTRO.inc_major_id 
INNER JOIN serv_off SERV_OFF WITH(NOLOCK)
	ON SERV_OFF.serv_off_id = inc_data.serv_off_id 
INNER JOIN serv SERV WITH(NOLOCK)
	ON SERV.serv_id = SERV_OFF.serv_id 
INNER JOIN item ITEM_REGISTRO  WITH(NOLOCK)
	ON ITEM_REGISTRO.item_id = INCIDENT.item_id 
INNER JOIN product PRODUTO_REGISTRO WITH(NOLOCK) 
	ON PRODUTO_REGISTRO.product_id = ITEM_REGISTRO.product_id 
INNER JOIN prod_cls CLASSE_PRODUTO_REGISTRO WITH(NOLOCK)
	ON CLASSE_PRODUTO_REGISTRO.prod_cls_id = PRODUTO_REGISTRO.prod_cls_id 
INNER JOIN generic_cls CLASSE_GENERICA_REGISTRO  WITH(NOLOCK)
	ON CLASSE_GENERICA_REGISTRO.generic_cls_id = CLASSE_PRODUTO_REGISTRO.generic_cls_id 
INNER JOIN item ITEM_B  WITH(NOLOCK)
	ON ITEM_B.item_id = inc_data.item_b_id
INNER JOIN product PRODUTO_B  WITH(NOLOCK)
	ON PRODUTO_B.product_id = ITEM_B.product_id 
INNER JOIN item ITEM_B_MODELO WITH(NOLOCK)
	ON ITEM_B_MODELO.item_id = PRODUTO_B.model_item_id 
INNER JOIN prod_cls CLASSE_PRODUTO_B WITH(NOLOCK)
	ON CLASSE_PRODUTO_B.prod_cls_id = PRODUTO_B.prod_cls_id 
INNER JOIN generic_cls CLASSE_GENERICA_B WITH(NOLOCK)
	ON CLASSE_GENERICA_B.generic_cls_id = CLASSE_PRODUTO_B.generic_cls_id 
INNER JOIN inc_cat INC_CAT_CAUSA  WITH(NOLOCK)
	ON INC_CAT_CAUSA.inc_cat_id = INCIDENT.cause_id 
INNER JOIN supplier SUPPLIER_PRODUCT_B WITH(NOLOCK)
	ON PRODUTO_B.supplier_id = SUPPLIER_PRODUCT_B.supplier_id 
INNER JOIN item ITEM_CAUSA  WITH(NOLOCK)
	ON ITEM_CAUSA.item_id = incident.cause_item_id 
INNER JOIN supplier SUPPLIER_CAUSA_ITEM WITH(NOLOCK)
	ON ITEM_CAUSA.inv_supp_id = SUPPLIER_CAUSA_ITEM.supplier_id 
INNER JOIN product PRODUTO_CAUSA  WITH(NOLOCK)
	ON PRODUTO_CAUSA.product_id = ITEM_CAUSA.product_id 
INNER JOIN prod_cls CLASSE_PRODUTO_CAUSA WITH(NOLOCK)
	ON CLASSE_PRODUTO_CAUSA.prod_cls_id = PRODUTO_CAUSA.prod_cls_id 
INNER JOIN item ITEM_CAUSA_MODELO WITH(NOLOCK)
	ON ITEM_CAUSA_MODELO.item_id = PRODUTO_CAUSA.model_item_id
INNER JOIN generic_cls CLASSE_GENERICA_CAUSA  WITH(NOLOCK)
	ON CLASSE_GENERICA_CAUSA.generic_cls_id = CLASSE_PRODUTO_CAUSA.generic_cls_id
INNER JOIN supplier SUPPLIER_PRODUCT_CAUSA WITH(NOLOCK)
	ON PRODUTO_CAUSA.supplier_id = SUPPLIER_PRODUCT_CAUSA.supplier_id
--LEFT JOIN ole_items OLE_ITEMS WITH(NOLOCK)
--	ON OLE_ITEMS.source_id = ACT_REG.act_reg_id
INNER JOIN priority_derived PRIORITY_DERIVED WITH(NOLOCK)
	ON  PRIORITY_DERIVED.priority_derived_id = inc_data.priority_derived_id
INNER JOIN usr USR_AFFECTED WITH(NOLOCK)
	ON USR_AFFECTED.usr_id = INCIDENT.aff_usr_id
INNER JOIN usr USR_REPORTING WITH(NOLOCK)
	ON USR_REPORTING.usr_id = INCIDENT.rep_usr_id
INNER JOIN sectn_dept SECTION_DEPT WITH(NOLOCK)
	ON SECTION_DEPT.sectn_dept_id = INCIDENT.sectn_dept_id
INNER JOIN sectn SECTION WITH(NOLOCK)
	ON SECTION.sectn_id = SECTION_DEPT.sectn_id
INNER JOIN branch BRANCH WITH(NOLOCK)
	ON BRANCH.branch_id = SECTION.branch_id
INNER JOIN division DIVISION WITH(NOLOCK)
	ON DIVISION.division_id = BRANCH.division_id
INNER JOIN bldng_room BUILDING_ROOM
	ON BUILDING_ROOM.bldng_room_id = INCIDENT.bldng_room_id
INNER JOIN bldng BUILDING WITH(NOLOCK)
	ON BUILDING.bldng_id = BUILDING_ROOM.bldng_id
INNER JOIN site SITE WITH(NOLOCK)
	ON SITE.site_id = BUILDING.site_id
INNER JOIN site_area SITE_AREA WITH(NOLOCK)
	ON SITE_AREA.site_area_id = SITE.site_area_id
WHERE	
	INCIDENT.incident_id > 0 -- Id de sistema
	AND INCIDENT.type_enum IN (1,4,7) -- Incidentes, requisições e tarefas
	AND ACT_REG.act_type_id IN (
	154,153,1,142,140,151,18,52,70,51,31,5,141,119,149,146,150,148,147,4,6,155,152,120,121,11,15,14,13,122) --ações Presentes no relatorio
	AND CLASSE_GENERICA_REGISTRO.generic_cls_sc IN ('SERVICOS DE TIC','SOFTWARE')
	AND 
	(
		(
			INCIDENT.status_enum = 2 -- Encerrados
			AND 
			INCIDENT.inc_close_date >= DATEADD(DD,-1,CONVERT(DATE,'03-02-2020',105)) and INCIDENT.inc_close_date < CONVERT(DATE,'03-02-2020',105) --  rem <-- Alterar aqui
		)
		OR
		(
			INCIDENT.status_enum = 3 -- Resolvidos
			AND 
			INCIDENT.inc_resolve_act >= DATEADD(DD,-1,CONVERT(DATE,'03-02-2020',105)) and INCIDENT.inc_resolve_act < CONVERT(DATE,'03-02-2020',105) --  rem <-- Alterar aqui
		)
		OR
		(
			INCIDENT.status_enum = 1 -- Abertos
			AND 
			EXISTS (SELECT 1 
					FROM ACT_REG A1 
					WHERE A1.act_reg_id = ACT_REG.act_reg_id 
					AND A1.date_actioned >= DATEADD(DD,-1,CONVERT(DATE,'03-02-2020',105)) and A1.date_actioned < CONVERT(DATE,'03-02-2020',105) --  rem <-- Alterar aqui
					AND A1.date_actioned <= CONVERT(DATE,'03-02-2020',105)) --  rem <-- Alterar aqui
		)
	)
