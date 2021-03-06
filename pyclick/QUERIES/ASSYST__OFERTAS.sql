SELECT 	DISTINCT SERV_OFF_ID 										AS SERV_OFF_ID
,		SERV_OFF.SERV_OFF_SC 										AS SERV_OFF_SC
,		SERV_OFF.SERV_OFF_N 										AS SERV_OFF_N
,		SERV_OFF.BUSINESS_REMARKS 									AS BUSINESS_REMARKS
,		SERV_OFF.REMARKS 											AS REMARKS
,		SERV_OFF.STAT_FLAG											AS STAT_FLAG -- n = Active / y = Discontinued
,		SERV_OFF.SERV_REQ_FLAG										AS SOLIC_SERVICO
,		SERV.SERV_SC												AS SERV_SC
,		SERV.SERV_N													AS SERV_N 
,		SERV.CSG_SC													AS SERV_CSG
,		SERV_DEPT.SERV_DEPT_SC										AS SERV_DEPT_SC
,		SERV_DEPT.SERV_DEPT_N										AS SERV_DEPT_N
,		SERV.BUSINESS_FLAG 											AS SERV_NEGOCIO
,		JPTSYS_CUST_ENT.JPTSYS_CUST_ENT_N 							AS FORMULARIO
,		PROC_HDR.PROC_HDR_N											AS PROCESSO
,		PROC_HDR.CSG_SC												AS PROCESSO_CSG
,		PRODUCT.PRODUCT_SC  										AS PRODUCT_SC
,		PRODUCT.PRODUCT_N  											AS PRODUCT_N
,		ITEM.ITEM_ID 												AS ITEM_ID
,		ITEM.ITEM_SC 												AS ITEM_SC
,		ITEM.ITEM_N 												AS ITEM_N
,		INC_CAT.INC_CAT_N 											AS CATEGORIA
,		INC_SERIOUS.INC_SERIOUS_SC									AS IMPACTO_SC
,		INC_SERIOUS.INC_SERIOUS_N									AS IMPACTO_N
,		INC_SERIOUS.CSG_SC											AS IMPACTO_CSG
,		INC_PRIOR.INC_PRIOR_SC										AS URGENCIA_SC
,		INC_PRIOR.INC_PRIOR_N										AS URGENCIA_N
,		INC_PRIOR.CSG_SC 											AS URGENCIA_CSG
,		SLA.SLA_SC 													AS SLA_SC
,		SLA.SLA_N 													AS SLA_N
,		SLA_SERIOUS.RESOLVE_TIME/60 								AS PRAZO_M
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
		ON 	A.PRIORITY_DERIVED_ID 		= SLA_SERIOUS.PRIORITY_DERIVED_ID
		AND	SERV_OFF.DEFAULT_URGENCY_ID = A.INC_PRIOR_ID
		AND SERV_OFF.DEFAULT_IMPACT_ID	= A.INC_SERIOUS_ID 
		--
ORDER	BY SERV_OFF.SERV_OFF_ID