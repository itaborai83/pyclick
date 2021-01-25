SELECT	A.SUPPLIER_ID
,		A.SUPPLIER_SC
,		A.SUPPLIER_N
,		B.SLA_ID
,		B.SLA_SC
,		B.SLA_N
,		B.SLA_RMK
FROM	SUPPLIER AS A
		--
		LEFT OUTER JOIN SLA 		AS B
		ON	A.DFLT_SLA_ID			= B.SLA_ID
		--
WHERE	A.SUPPLIER_ID <> 0
ORDER	BY A.SUPPLIER_ID