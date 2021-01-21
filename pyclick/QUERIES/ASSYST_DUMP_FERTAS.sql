SELECT 	DISTINCT SERV_OFF.SERV_OFF_N 								AS 'Oferta'
/*
,		SERV_OFF.SERV_OFF_SC 										AS 'Oferta - Código'
,		CASE 	WHEN SERV.CSG_ID !=0 
				THEN SERV.SERV_SC+'#'+SERV.CSG_SC 
				ELSE SERV.SERV_N 
		END 														AS 'Serviço'
,		SERV_OFF.BUSINESS_REMARKS 									AS 'Descrição'
,		SERV_OFF.REMARKS 											AS 'Notas'
,		JPTSYS_CUST_ENT.JPTSYS_CUST_ENT_N 							AS 'Formulário'
,		CASE 	WHEN PROC_HDR.CSG_ID != 0
				THEN PROC_HDR.PROC_HDR_SC +'#'+ PROC_HDR.CSG_SC 
				ELSE PROC_HDR.PROC_HDR_N 
		END 														AS 'Processo'
,		CASE 	WHEN SERV_DEPT.CSG_ID != 0 
				THEN SERV_DEPT.SERV_DEPT_SC+'#'+ SERV_DEPT.CSG_SC 
				ELSE SERV_DEPT.SERV_DEPT_N 
		END 														AS 'Mesa'
,		SERV_OFF.READ_ONLY_NET										AS 'Read Only Assystnet'
,		SERV_OFF.READ_ONLY_WEB										AS 'Read Only Assystweb'
,		SERV_OFF.SERV_REQ_FLAG										AS 'Solicitação de Serviço'
,		SERV.BUSINESS_FLAG 											AS 'Serviço de Negócio'
,		PRODUCT.PRODUCT_N  											AS 'Produto'
,		ITEM.ITEM_N 												AS 'Item de Serviço'
,		INC_CAT.INC_CAT_N 											AS 'Categoria'
,		CASE 	WHEN INC_SERIOUS.CSG_ID != 0 
				THEN INC_SERIOUS.INC_SERIOUS_SC+'#'+ INC_SERIOUS.CSG_SC 
				ELSE INC_SERIOUS.INC_SERIOUS_N 
		END 														AS 'Impacto'
,		CASE 	WHEN INC_PRIOR.CSG_ID != 0 
				THEN INC_PRIOR.INC_PRIOR_SC+'#'+ INC_PRIOR.CSG_SC 
				ELSE INC_PRIOR.INC_PRIOR_N 
		END 														AS 'Urgencia'
,		SLA.SLA_N 													AS 'SLA Nome'
*/
,		SLA_SERIOUS.RESOLVE_TIME/60 								AS 'Prazo'
FROM 	SERV_OFF 		
		--
		INNER JOIN SERV
		ON 	SERV.SERV_ID 				= SERV_OFF.SERV_ID
		--
		INNER JOIN ITEM 
		ON 	ITEM.ITEM_ID 				= SERV_OFF.DEFAULT_ITEM_ID
		--
		INNER JOIN INC_SERIOUS 
		ON 	INC_SERIOUS.INC_SERIOUS_ID 	= SERV_OFF.DEFAULT_IMPACT_ID
		--
		INNER JOIN INC_PRIOR 
		ON INC_PRIOR.INC_PRIOR_ID 		= SERV_OFF.DEFAULT_URGENCY_ID
		--
		INNER JOIN JPTSYS_CUST_ENT 
		ON 	JPTSYS_CUST_ENT.JPTSYS_CUST_ENT_ID = SERV_OFF.JPTSYS_CUST_ENT_ID
		--
		INNER JOIN INC_CAT 
		ON 	INC_CAT.INC_CAT_ID 			= SERV_OFF.DEFAULT_CATEGORY_ID
		--	
		INNER JOIN PROC_HDR 	
		ON 	PROC_HDR.PROC_HDR_ID 		= SERV_OFF.DEFAULT_TEMPLATE_PROC_ID
		--	
		INNER JOIN SERV_DEPT 	
		ON 	SERV_DEPT.SERV_DEPT_ID 		= SERV_OFF.DEFAULT_ASS_SVD_ID
		--	
		INNER JOIN PRODUCT	
		ON 	ITEM.PRODUCT_ID 			= PRODUCT.PRODUCT_ID
		--	
		INNER JOIN SLA 	
		ON 	PRODUCT.DFLT_SLA_ID 		= SLA.SLA_ID
		--	
		INNER JOIN SLA_SERIOUS 	
		ON 	SLA_SERIOUS.SLA_ID 			= SLA.SLA_ID
		--
		INNER JOIN PRIORITY_DERIVED_RULE A
		ON A.PRIORITY_DERIVED_ID 		= SLA_SERIOUS.PRIORITY_DERIVED_ID
		--
WHERE 	SERV_OFF.DEFAULT_URGENCY_ID 	= A.INC_PRIOR_ID
AND 	SERV_OFF.STAT_FLAG 				= 'n' -- ATENÇÃO!!! Precisa ser caixa baixa