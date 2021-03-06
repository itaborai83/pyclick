SELECT	INCIDENT.TYPE_ENUM
,		INCIDENT.INCIDENT_ID
,		INCIDENT.DATE_LOGGED AS 'DATA ABERTURA CHAMADO'
,		INCIDENT.INC_RESOLVE_ACT AS 'DATA RESOLUÇÃO CHAMADO'
,		CASE	WHEN INCIDENT.TYPE_ENUM = 1 THEN '' 
				WHEN INCIDENT.TYPE_ENUM = 2 THEN 'P'
				WHEN INCIDENT.TYPE_ENUM = 3 THEN 'R'
				WHEN INCIDENT.TYPE_ENUM = 7 THEN 'S'
				WHEN INCIDENT.TYPE_ENUM = 5 THEN 'D'
											ELSE 'T'								
		END 
+		CAST(INCIDENT.INCIDENT_REF AS VARCHAR(10))'ID CHAMADO'
,	CASE 	WHEN INCIDENT.STATUS_ENUM = 1 THEN 'ABERTO'
			WHEN INCIDENT.STATUS_ENUM = 2 THEN 'FECHADO'
			WHEN INCIDENT.STATUS_ENUM = 3 THEN 'RESOLVIDO'
			ELSE 'ENVIADO'
	END 'STATUS DE EVENTO'
FROM 	INCIDENT INCIDENT WITH(NOLOCK)
WHERE	1=1
		-- ID DE SISTEMA
AND		INCIDENT.INCIDENT_ID 	<> 0
AND 	INCIDENT.TYPE_ENUM 		IN (1,4,7) -- INCIDENTES, REQUISIÇÕES E TAREFAS
AND		INCIDENT.DATE_LOGGED	 < CONVERT(DATETIME, ?, 120)
AND		( 	(1=1 AND INCIDENT.STATUS_ENUM = 1 AND INCIDENT.INC_RESOLVE_ACT IS NULL) 					OR -- ABERTOS
			(1=1 AND INCIDENT.STATUS_ENUM = 2 AND INCIDENT.INC_CLOSE_DATE  > CONVERT(DATETIME, ?, 120)) OR -- ENCERRADOS 
			(1=1 AND INCIDENT.STATUS_ENUM = 3 AND INCIDENT.INC_RESOLVE_ACT > CONVERT(DATETIME, ?, 120)) )  -- RESOLVIDOS 				
ORDER	BY 3, 4, 1, 2