WITH USERS_STATUSES AS (
	SELECT 	ULTIMA_ACAO_NOME
	,		CASE	
			------------------------------------------------------------------------------
			-- BEGIN - ADD SELECT CLAUSE OUTPUT OF ASSYST_ACT_TYPE_USER_STATUS.SQL HERE --
			------------------------------------------------------------------------------
			------------------------------------------------------------------------------
			---- WARNING: DO NOT UPPERCASE THE SQL ---------------------------------------
			------------------------------------------------------------------------------
				WHEN ULTIMA_ACAO_NOME = 'Iniciar Atendimento' THEN 'USER STATUS AND INT. START CLOCK ' -- 'a'
				WHEN ULTIMA_ACAO_NOME = 'Iniciar Relógio' THEN 'USER STATUS AND INT. START CLOCK ' -- 'a'
				WHEN ULTIMA_ACAO_NOME = 'Pendência Sanada' THEN 'USER STATUS AND INT. START CLOCK ' -- 'a'
				WHEN ULTIMA_ACAO_NOME = 'Pendência Sanada - Aprovação' THEN 'USER STATUS AND INT. START CLOCK ' -- 'a'
				WHEN ULTIMA_ACAO_NOME = 'Pendência Sanada Feriado Local' THEN 'USER STATUS AND INT. START CLOCK ' -- 'a'
				WHEN ULTIMA_ACAO_NOME = 'Aguardando Cliente - Aprovação' THEN 'INTERNAL STOP CLOCK' -- 'c'
				WHEN ULTIMA_ACAO_NOME = 'Aguardando Cliente' THEN 'USER STATUS AND INT. STOP CLOCK' -- 'l'
				WHEN ULTIMA_ACAO_NOME = 'Aguardando Cliente - Aprovação' THEN 'USER STATUS AND INT. STOP CLOCK' -- 'l'
				WHEN ULTIMA_ACAO_NOME = 'Atendimento Agendado' THEN 'USER STATUS AND INT. STOP CLOCK' -- 'l'
				WHEN ULTIMA_ACAO_NOME = 'Parar Relógio' THEN 'USER STATUS AND INT. STOP CLOCK' -- 'l'
				WHEN ULTIMA_ACAO_NOME = 'Pendência Feriado Local' THEN 'USER STATUS AND INT. STOP CLOCK' -- 'l'
				WHEN ULTIMA_ACAO_NOME = 'Pendência Sanada - Fornecedor/TIC' THEN 'SUPPLIER START CLOCK' -- 'p'
				WHEN ULTIMA_ACAO_NOME = 'Aguardando Cliente - Fornecedor' THEN 'SUPPLIER STOP CLOCK' -- 'u'
				WHEN ULTIMA_ACAO_NOME = 'Pendencia de Fornecedor' THEN 'SUPPLIER STOP CLOCK' -- 'u'
				WHEN ULTIMA_ACAO_NOME = 'Pendência de TIC' THEN 'SUPPLIER STOP CLOCK' -- 'u'
				------------------------------------------------------------------------------
				-- BEGIN - ADD SELECT CLAUSE OUTPUT OF ASSYST_ACT_TYPE_USER_STATUS.SQL HERE --
				------------------------------------------------------------------------------
			END USER_STATUS
	FROM 	REL_MEDICAO
	WHERE	ULTIMA_ACAO_NOME IN (
				NULL
				------------------------------------------------------------------------
				-- BEGIN - ADD WHERE CLAUSE OUTPUT OF ASSYST_ACT_TYPE_USER_STATUS.SQL --
				------------------------------------------------------------------------
				------------------------------------------------------------------------------
				---- WARNING: DO NOT UPPERCASE THE SQL ---------------------------------------
				------------------------------------------------------------------------------			
				,		 'Pendência Sanada'
				,		 'Iniciar Relógio'
				,		 'Parar Relógio'
				,		 'Aguardando Cliente'
				,		 'Iniciar Atendimento'
				,		 'Atendimento Agendado'
				,		 'Pendencia de Fornecedor'
				,		 'Pendência de TIC'
				,		 'Pendência Sanada Feriado Local'
				,		 'Pendência Feriado Local'
				,		 'Pendência Sanada - Fornecedor/TIC'
				,		 'Aguardando Cliente - Aprovação'
				,		 'Aguardando Cliente - Fornecedor'
				,		 'Pendência Sanada - Aprovação'
				,		 'Aguardando Cliente - Aprovação'			
				----------------------------------------------------------------------
				-- END - ADD WHERE CLAUSE OUTPUT OF ASSYST_ACT_TYPE_USER_STATUS.SQL --
				----------------------------------------------------------------------
			)
	GROUP	BY ULTIMA_ACAO_NOME
)
UPDATE 	REL_MEDICAO AS UPD
SET		USER_STATUS = (SELECT A.USER_STATUS FROM USERS_STATUSES AS A WHERE A.ULTIMA_ACAO_NOME = UPD.ULTIMA_ACAO_NOME);

	
