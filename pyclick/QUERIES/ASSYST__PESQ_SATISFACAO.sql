SELECT 	--ID da pesquisa de satisfação.
		surv_req.surv_req_id AS 'ID Pesquisa',
		--Data de criação da pesquisa.
		surv_req.issued_date AS 'Data de Criação da Pesquisa',
		--ID do incidente.
		CASE
		  WHEN incident.type_enum = 1 THEN ' ' + CAST(incident.incident_ref AS varchar(10))
		  WHEN incident.type_enum = 2 THEN 'P' + CAST(incident.incident_ref AS varchar(10))
		  WHEN incident.type_enum = 3 THEN 'R' + CAST(incident.incident_ref AS varchar(10))
		  WHEN incident.type_enum = 7 THEN 'S' + CAST(incident.incident_ref AS varchar(10))
		  WHEN incident.type_enum = 5 THEN 'D' + CAST(incident.incident_ref AS varchar(10))
		  ELSE 'T' + CAST(incident.incident_ref AS varchar(10))
		END 'ID Incidente',
		--Data de abertura do incidente.
		incident.date_logged as 'Data Abertura Incidente',
		--Tipo de Incidente.
		CASE
		  WHEN incident.type_enum = 1 THEN 'Incidente' 
		  WHEN incident.type_enum = 2 THEN 'P' 
		  WHEN incident.type_enum = 3 THEN 'R' 
		  WHEN incident.type_enum = 7 THEN 'Solicitação'
		  WHEN incident.type_enum = 5 THEN 'D' 
		ELSE 'Tarefa' 
		END 'Tipo',
		--Mesa Ação
		serv_dept.serv_dept_sc AS 'Mesa Ação',
		--Chave do Técnico.
		assyst_usr.assyst_usr_sc AS 'Chave do Técnico',
		--Nome do Técnico.
		assyst_usr.assyst_usr_n AS 'Nome do Técnico',
		--Departamento do Técnico.
		sectn_dept.sectn_n AS 'Departamento do Técnico',
		--Item B
		item.item_n AS 'Item B',
		--Categoria.
		inc_cat.inc_cat_n AS 'Categoria',
		--Classe de Produto de Serviço.
		prod_cls.prod_cls_n AS 'Classe de Produto de Serviço',
		--Produto de Serviço.
		product.product_n AS 'Produto de Serviço',
		--ANS.
		sla.sla_n AS 'ANS',
		--Data de Resolução do Chamado.
		incident.inc_resolve_act AS 'Data de Resolução do Chamado',
		--Chave do Usuário.
		usr.usr_sc AS 'Chave do Usuário',
		--Nome do Usuário.
		usr.usr_n AS 'Nome do Usuário',
		--Seção.
		sectn_dept.sectn_n AS 'Seção',
		--Site.
		(
			select bldng.bldng_n from bldng  
			INNER JOIN bldng_room ON bldng_room.bldng_id = bldng.bldng_id
			WHERE bldng_room_id = usr.bldng_room_id
		) as 'SITE',
		--Data de Resposta.
		surv_req.resp_date AS 'Data de Resposta',
		--Como você avalia a sua experiencia com esse serviço?
		surv_req.response_1 AS 'Como você avalia a sua experiencia com esse serviço?',
		--O que motivou sua opinião?
		surv_req.response_2 AS 'O que motivou sua opinião?',
		--Motivo.
		CASE
			WHEN surv_req.response_2 = 1 THEN 'Prazo' 
			WHEN surv_req.response_2 = 2 THEN 'Atendimento' 
			WHEN surv_req.response_2 = 3 THEN 'Solução' 
			WHEN surv_req.response_2 = 4 THEN 'Acesso'
			WHEN surv_req.response_2 = 5 THEN 'Outros' 
			ELSE '' 
		END 'Motivo' ,
		surv_req.comments AS 'Comentários'
		--Tabela principal - Pesquisa de Satisfação.
FROM 	surv_req 
		--Junções.
		INNER JOIN vw_incident as incident 
		ON	incident.incident_id = surv_req.incident_id
		--
		INNER JOIN vw_act_reg ar 
		ON 	ar.act_reg_id = surv_req.act_reg_id
		--
		INNER JOIN serv_dept 
		ON 	serv_dept.serv_dept_id = incident.ass_svd_id
		--
		INNER JOIN assyst_usr 
		ON 	assyst_usr.assyst_usr_id = incident.ass_usr_id
		--
		INNER JOIN usr 
		ON 	usr.usr_sc = assyst_usr.assyst_usr_sc
		--
		INNER JOIN sectn_dept
		ON 	sectn_dept.sectn_dept_id = usr.sectn_dept_id
		--
		INNER JOIN inc_data
		ON 	inc_data.incident_id = incident.incident_id
		--
		INNER JOIN item 
		ON 	item.item_id = inc_data.item_b_id
		--
		INNER JOIN inc_cat
		ON 	inc_cat.inc_cat_id = incident.inc_cat_id
		--
		INNER JOIN product
		ON 	item.product_id = product.product_id
		--
		INNER JOIN prod_cls
		ON 	prod_cls.prod_cls_id = product.prod_cls_id
		--
		INNER JOIN sla 
		ON 	product.dflt_sla_id = sla.sla_id
		--Where
WHERE 	surv_req.surv_req_id > 0
		--Filtros adicionais.
AND 	surv_req.resp_date IS NOT NULL
AND 	surv_req.resp_type = 'c'
AND 	surv_req.resp_date BETWEEN ? AND ?
AND 	serv_dept.serv_dept_n in (
			-- BEGIN RISK OF SQL INJECTION
			{MESAS}
			-- END RISK OF SQL INJECTION
		)