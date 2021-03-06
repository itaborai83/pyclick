CREATE TABLE IF NOT EXISTS FILE_INDEX (
	NOME_ARQ						TEXT
,	ID_CHAMADO						TEXT
,	CHAMADO_PAI						TEXT
,	ABERTO							TEXT
,	QTD_ACOES						INTEGER
,	MIN_ID_ACAO						INTEGER
,	MAX_ID_ACAO						INTEGER
,	PRIMARY KEY(NOME_ARQ ASC, ID_CHAMADO ASC)
);

CREATE INDEX IF NOT EXISTS FILE_INDEX_IDX01 ON FILE_INDEX(ID_CHAMADO, NOME_ARQ, CHAMADO_PAI);
CREATE INDEX IF NOT EXISTS FILE_INDEX_IDX02 ON FILE_INDEX(CHAMADO_PAI, ID_CHAMADO, NOME_ARQ);