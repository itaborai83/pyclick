SELECT	A.ASSYST_USR_ID
,		A.ASSYST_USR_SC
,		A.ASSYST_USR_N
,		A.ASSYST_USR_RMK
,		B.SERV_DEPT_ID
,		B.SERV_DEPT_SC
,		B.SERV_DEPT_N
FROM	ASSYST_USR					AS A
		--
		LEFT OUTER JOIN SERV_DEPT	AS B
		ON	A.SERV_DEPT_ID 			= B.SERV_DEPT_ID
		--
WHERE	A.ASSYST_USR_ID NOT IN (0, -100)
ORDER	BY A.ASSYST_USR_ID
