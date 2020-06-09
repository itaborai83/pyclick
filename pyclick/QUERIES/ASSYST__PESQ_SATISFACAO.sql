SELECT 	--ID da pesquisa de satisfação.
		surv_req.surv_req_id AS 'id_pesquisa',
		--Data de criação da pesquisa.
		surv_req.issued_date AS 'data_pesquisa',
		--ID do incidente.
		CASE
		  WHEN incident.type_enum = 1 THEN ' ' + CAST(incident.incident_ref AS varchar(10))
		  WHEN incident.type_enum = 2 THEN 'P' + CAST(incident.incident_ref AS varchar(10))
		  WHEN incident.type_enum = 3 THEN 'R' + CAST(incident.incident_ref AS varchar(10))
		  WHEN incident.type_enum = 7 THEN 'S' + CAST(incident.incident_ref AS varchar(10))
		  WHEN incident.type_enum = 5 THEN 'D' + CAST(incident.incident_ref AS varchar(10))
		  ELSE 'T' + CAST(incident.incident_ref AS varchar(10))
		END 'id_chamado',
		--Data de abertura do incidente.
		incident.date_logged as 'data_abertura_incidente',
		--Tipo de Incidente.
		CASE
		  WHEN incident.type_enum = 1 THEN 'Incidente' 
		  WHEN incident.type_enum = 2 THEN 'P' 
		  WHEN incident.type_enum = 3 THEN 'R' 
		  WHEN incident.type_enum = 7 THEN 'Solicitação'
		  WHEN incident.type_enum = 5 THEN 'D' 
		ELSE 'Tarefa' 
		END 'tipo',
		--Mesa Ação
		serv_dept.serv_dept_sc AS 'mesa_acao',
		--Chave do Técnico.
		assyst_usr.assyst_usr_sc AS 'chave_tecnico',
		--Nome do Técnico.
		assyst_usr.assyst_usr_n AS 'nome_tecnico',
		--Departamento do Técnico.
		sectn_dept.sectn_n AS 'dept_tecnico',
		--Item B
		item.item_n AS 'item_b',
		--Categoria.
		inc_cat.inc_cat_n AS 'categoria',
		--Classe de Produto de Serviço.
		prod_cls.prod_cls_n AS 'classe_prod_serv',
		--Produto de Serviço.
		product.product_n AS 'prod_serv',
		--ANS.
		sla.sla_n AS 'sla',
		--Data de Resolução do Chamado.
		incident.inc_resolve_act AS 'data_resolucao_chamado',
		--Chave do Usuário.
		usr.usr_sc AS 'chave_usuario',
		--Nome do Usuário.
		usr.usr_n AS 'nome_usuario',
		--Seção.
		sectn_dept.sectn_n AS 'secao',
		--Site.
		(
			select bldng.bldng_n from bldng  
			INNER JOIN bldng_room ON bldng_room.bldng_id = bldng.bldng_id
			WHERE bldng_room_id = usr.bldng_room_id
		) as 'site',
		--Data de Resposta.
		surv_req.resp_date AS 'data_resposta',
		--Como você avalia a sua experiencia com esse serviço?
		surv_req.response_1 AS 'avaliacao',
		--Motivo.
		CASE
			WHEN surv_req.response_2 = 1 THEN 'Prazo' 
			WHEN surv_req.response_2 = 2 THEN 'Atendimento' 
			WHEN surv_req.response_2 = 3 THEN 'Solução' 
			WHEN surv_req.response_2 = 4 THEN 'Acesso'
			WHEN surv_req.response_2 = 5 THEN 'Outros' 
			ELSE '' 
		END 'motivo' ,
		surv_req.comments AS 'comentario'
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
AND 	surv_req.resp_date BETWEEN CONVERT(DATETIME, ?, 120) AND CONVERT(DATETIME, ?, 120)
AND 	serv_dept.serv_dept_n in (
			-- BEGIN RISK OF SQL INJECTION
			{MESAS}
			-- END RISK OF SQL INJECTION
		)