WITH PENDENCIAS AS (
	select	id_chamado
	,		id_acao
	,		LEAD(A.ID_ACAO, 1, 999999999) OVER (
				PARTITION BY A.ID_CHAMADO
				ORDER BY A.ID_ACAO
			) AS ID_ACAO_NEXT	
	,		case when user_status = 'SUPPLIER STOP CLOCK' then 'S' else 'N' end as PENDENCIA
	from	rel_medicao as a
	where	user_status IN ('SUPPLIER STOP CLOCK', 'SUPPLIER START CLOCK')
	order	by 1, 2
),
PENDENCIAS_ATUAIS AS (
	SELECT	A.ID_CHAMADO
	,		A.ID_ACAO
	,		A.ULTIMA_ACAO_NOME
	,		COALESCE(B.PENDENCIA, 'N') AS PENDENCIA
	FROM	REL_MEDICAO AS A
			--
			LEFT OUTER JOIN PENDENCIAS AS B
			ON 	A.ID_CHAMADO = B.ID_CHAMADO
			AND	A.ID_ACAO >= B.ID_ACAO
			AND	A.ID_ACAO < B.ID_ACAO_NEXT
			--
	ORDER	BY A.ID_CHAMADO
	,		A.ID_ACAO
)
UPDATE 	REL_MEDICAO AS UPD
SET		PENDENCIA = (
			SELECT 	A.PENDENCIA  
			FROM 	PENDENCIAS_ATUAIS AS A
			WHERE 	A.ID_CHAMADO	= UPD.ID_CHAMADO 
			AND		A.ID_ACAO		= UPD.ID_ACAO
		);