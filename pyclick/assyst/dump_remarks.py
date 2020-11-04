import re
import os
import argparse
import pandas as pd
import logging
import sqlite3
from unidecode import unidecode

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_remarks')

SQL_CREATE_DETAILS_TABLE = """
CREATE TABLE IF NOT EXISTS INCIDENTE_DETALHES(
    ID_CHAMADO  TEXT NOT NULL,
    DESCRICAO   TEXT NULL,
    RESOLUCAO   TEXT NULL,
    CONSTRAINT INCIDENTE_DETALHES_PK PRIMARY KEY(ID_CHAMADO)
)
"""

SQL_CREATE_REMARKS_TABLE = """
CREATE TABLE IF NOT EXISTS INCIDENTE_TEXTOS(
    ID_CHAMADO  TEXT NOT NULL,
    ID_ACAO     INTEGER NOT NULL,
    TEXTO       TEXT NULL,
    CONSTRAINT INCIDENTE_TEXTOS_PK PRIMARY KEY(ID_CHAMADO, ID_ACAO)
)
"""

SQL_FETCH_ACTION_IDS = """
SELECT	A.ID_CHAMADO
,		A.ID_ACAO
FROM	INCIDENTE_ACOES AS A
ORDER	BY A.ID_ACAO        
"""

SQL_FETCH_DETAIL_IDS = """
SELECT	A.ID_CHAMADO
,		MIN(A.ID_ACAO) AS MIN_ID_ACAO
,		MAX(CASE    WHEN A.ULTIMA_ACAO_NOME in ('Resolver', 'Cancelar')
                    THEN A.ID_ACAO 
                    ELSE NULL 
        END) AS MAX_ID_RESOLUCAO
FROM	INCIDENTE_ACOES AS A
GROUP	BY A.ID_CHAMADO
ORDER	BY A.ID_ACAO
"""

SQL_FETCH_REMARKS = """
SELECT	A.ACT_REG_ID AS ID_ACAO
,		LOWER(TRANSLATE(A.REMARKS, ''''+'"'+CHAR(9)+CHAR(10)+CHAR(13), '     ')) AS REMARKS
FROM	VW_ACT_REG AS A
WHERE	A.REMARKS IS NOT NULL 
AND		A.REMARKS <> ''
AND		A.ACT_REG_ID IN ({ACTION_IDS})
ORDER	BY A.ACT_REG_ID
"""

SQL_FETCH_DETAILS = """
SELECT	DISTINCT A.ACT_REG_ID AS ID_ACAO
,		LOWER(TRANSLATE(B.REMARKS, ''''+'"'+CHAR(9)+CHAR(10)+CHAR(13), '     ')) AS REMARKS
FROM	VW_ACT_REG AS A
		--
		INNER JOIN INC_DATA AS B
		ON	A.INCIDENT_ID = B.INCIDENT_ID 
		--
WHERE	B.REMARKS IS NOT NULL 
AND		B.REMARKS <> ''
AND		A.ACT_REG_ID IN ({ACTION_IDS})
ORDER	BY A.ACT_REG_ID
"""

STRIP_CHARS = set([
    '@', "'", '"', '!', '#', '$', '£', '%', '¢', '¨', '¬', '&', '*', '(', ')',
    '=', '+', '§', '|', '\\', ',', '<', '.', '>', ';', ':', '/', '?',
    '°', '~', '^', ']', '}', 'º', '´', '`', '[', '{', 'ª', '\n', '\t', '\0', 
    '\x8A', '\x8D', '\x87', '\x82', '\x83', '\x93', '\x90', '\x81'
])

SKIP_TEXTS = set([
    """
    'favor verificar',
    'fechamento automatico apos 2 dias',
    'relogio de fornecedor pausado apos o relogio de ans ser pausado',
    'relogio de fornecedor iniciado apos o relogio de ans ser iniciado',
    'assigned via workmanager',
    'requisicao de servico completada',
    'pendente aguardando aprovacao',
    'withdrawn',
    'retomar relogio apos aprovacao',
    'em analise',
    'incidente cancelado pelo analista',
    'relogio de sla iniciado apos retorno do usuario',
    'retorno do usuario',
    'designado',
    'verificar',
    'n4',
    'favor verificar grata',
    'sap n4',
    'aguardando retorno',
    'favor verificar grato',
    'inicio sap sust',
    'tarefa de mudanca value changed from empty to false'
    'prazo de atendimento e de 32 horas uteis favor verificar',
    'inicio n4 sust',
    'por favor verificar',
    'tentativa de contato sem sucesso',
    'aguardando retorno do usuario',
    'verificando',
    'gentileza verificar',
    'favor atender',
    'designando atraves do web service',
    '',
    'nao houve retorno da usuaria',
    'aguardando retorno da usuaria',
    'o prazo de atendimento e de ate 32 horas uteis favor verificar',
    'nao houve retorno do usuario'
    """
])


class App(object):
    
    VERSION = (1, 0, 0)
    BATCH_SIZE = 5000
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
    
    def connect_db_assyst(self):
        logger.info('connecting to assyst db')
        return click_config.SQLALCHEMY_ENGINE.connect()    

    def connect_db_apuracao(self):
        logger.info('connecting to apuracao db')
        result_db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        conn = sqlite3.connect(result_db)
        conn.executescript(SQL_CREATE_REMARKS_TABLE)
        conn.executescript(SQL_CREATE_DETAILS_TABLE)
        return conn
    
    def fetch_action_ids(self, conn_apuracao):
        logger.info('fetching action ids')
        action_ids_df = pd.read_sql(SQL_FETCH_ACTION_IDS, conn_apuracao, index_col=None)
        qty = len(action_ids_df)
        logger.info(f'{qty} action ids fetched')
        return action_ids_df
    
    def fetch_details_action_ids(self, conn_apuracao):
        logger.info('fetching deatils action ids')
        details_action_ids_df = pd.read_sql(SQL_FETCH_DETAIL_IDS, conn_apuracao, index_col=None)
        qty = len(details_action_ids_df)
        logger.info(f'{qty} action ids fetched')
        return details_action_ids_df

        
    def create_batches(self, action_ids_df, batch_size):
        batch_count = 0
        batches = []
        current_batch = []
        for row in action_ids_df.itertuples():
            batch_count += 1
            current_batch.append( (row.ID_CHAMADO, row.ID_ACAO) )
            if batch_count >= batch_size:
                batches.append(current_batch)
                current_batch = []
                batch_count = 0
        if batch_count >= 0:
            batches.append(current_batch)
            current_batch = []
            batch_count = 0
        return batches

    def create_detail_batches(self, detail_action_ids_df, batch_size):
        batches_details = []
        batch_count     = 0
        current_batch   = []
        for row in detail_action_ids_df.itertuples():
            batch_count += 1
            current_batch.append( (row.ID_CHAMADO, row.MIN_ID_ACAO) )
            if batch_count >= batch_size:
                batches_details.append(current_batch)
                current_batch   = []
                batch_count     = 0
        if batch_count >= 0:
            batches_details.append(current_batch)
            current_batch   = []
            batch_count     = 0
        
        
        batches_resolutions = []
        batch_count         = 0
        current_batch       = []
        for row in detail_action_ids_df.itertuples():
            if not row.MAX_ID_RESOLUCAO or pd.isna(row.MAX_ID_RESOLUCAO): # chamado cancelado ou aberto
                continue
            batch_count += 1
            current_batch.append( (row.ID_CHAMADO, row.MAX_ID_RESOLUCAO) )
            if batch_count >= batch_size:
                batches_resolutions.append(current_batch)
                current_batch = []
                batch_count = 0
        if batch_count >= 0:
            batches_resolutions.append(current_batch)
            current_batch = []
            batch_count = 0
        
        return batches_details, batches_resolutions
        
        
        
    def fetch_remarks(self, conn, batch, remarks):
        id_chamados = map(lambda x: x[0], batch)
        id_acoes = map(lambda x: x[1], batch)
        ids_map = dict(zip(id_acoes, id_chamados))
        batch_ids_txt = ', '.join(list([ str(action_id) for _, action_id in batch ]))
        sql = SQL_FETCH_REMARKS.replace('{ACTION_IDS}', batch_ids_txt)
        remarks_df = pd.read_sql(sql, conn, index_col=None)
        qty = len(remarks_df)
        logger.info(f'{qty} remarks fetched')
        for row in remarks_df.itertuples():
            id_chamado = ids_map[ row.ID_ACAO ]
            id_acao = row.ID_ACAO
            txt = self.clean_text(row.REMARKS)
            if txt not in SKIP_TEXTS:
                remarks.append( (id_chamado, id_acao, txt) )
        
    def fetch_details(self, conn, batch, details):
        id_chamados = map(lambda x: x[0], batch)
        id_acoes = map(lambda x: x[1], batch)
        ids_map = dict(zip(id_acoes, id_chamados))
        batch_ids_txt = ', '.join(list([ str(action_id) for _, action_id in batch ]))
        sql = SQL_FETCH_DETAILS.replace('{ACTION_IDS}', batch_ids_txt)
        details_df = pd.read_sql(sql, conn, index_col=None)
        qty = len(details_df)
        logger.info(f'{qty} details fetched')
        for row in details_df.itertuples():
            id_chamado = ids_map[ row.ID_ACAO ]
            txt = self.clean_text(row.REMARKS)
            if txt not in SKIP_TEXTS:
                details.append( (id_chamado, txt) )

    def fetch_resolutions(self, conn, batch, resolutions):
        id_chamados = map(lambda x: x[0], batch)
        id_acoes = map(lambda x: x[1], batch)
        ids_map = dict(zip(id_acoes, id_chamados))
        batch_ids_txt = ', '.join(list([ str(action_id) for _, action_id in batch ]))
        sql = SQL_FETCH_REMARKS.replace('{ACTION_IDS}', batch_ids_txt)
        resolutions_df = pd.read_sql(sql, conn, index_col=None)
        qty = len(resolutions_df)
        logger.info(f'{qty} resolutions fetched')
        for row in resolutions_df.itertuples():
            id_chamado = ids_map[ row.ID_ACAO ]
            txt = self.clean_text(row.REMARKS)
            if txt not in SKIP_TEXTS:
                resolutions.append( (txt, id_chamado) )
                
    def clean_text(self, txt):
        txt = unidecode(txt)
        txt = "".join([ (' ' if ch in STRIP_CHARS else ch) for ch in txt ])
        txt, _ = re.subn(r'\s+', ' ', txt)
        txt = txt.strip()
        return txt

    def save_remarks(self, conn_apuracao, remarks):
        logger.info(f'saving {len(remarks)} remarks')
        sql = 'INSERT INTO INCIDENTE_TEXTOS(ID_CHAMADO, ID_ACAO, TEXTO) VALUES(?, ?, ?)'
        conn_apuracao.executescript('DELETE FROM INCIDENTE_TEXTOS')
        conn_apuracao.executemany(sql, remarks)
        conn_apuracao.commit()
    
    def save_details(self, conn_apuracao, details, resolutions):
        logger.info(f'saving {len(details)} details and {len(resolutions)} resolutions')
        
        conn_apuracao.executescript('DELETE FROM INCIDENTE_DETALHES')
        
        sql = 'INSERT INTO INCIDENTE_DETALHES(ID_CHAMADO, DESCRICAO, RESOLUCAO) VALUES(?, ?, NULL)'
        conn_apuracao.executemany(sql, details)
        
        sql = 'UPDATE INCIDENTE_DETALHES SET RESOLUCAO = ? WHERE ID_CHAMADO = ?'
        conn_apuracao.executemany(sql, resolutions)
        conn_apuracao.commit()
        
    def dump_remarks(self, conn_assyst, conn_apuracao):
        action_ids_df = self.fetch_action_ids(conn_apuracao)
        batches = self.create_batches(action_ids_df, self.BATCH_SIZE)
        remarks = []
        for i, batch in enumerate(batches):
            logger.info(f'fetching batch {i + 1} containing {len(batch)} actions')
            self.fetch_remarks(conn_assyst, batch, remarks)
        self.save_remarks(conn_apuracao, remarks)
    
    def dump_details(self, conn_assyst, conn_apuracao):
        details_action_ids_df = self.fetch_details_action_ids(conn_apuracao)
        batches_details, batches_resolutions = self.create_detail_batches(details_action_ids_df, self.BATCH_SIZE)
        details = []
        for i, batch in enumerate(batches_details):
            logger.info(f'fetching details batch {i + 1} containing {len(batch)} actions')
            self.fetch_details(conn_assyst, batch, details)
        resolutions = []
        for i, batch in enumerate(batches_resolutions):
            logger.info(f'fetching resolutions batch {i + 1} containing {len(batch)} actions')
            self.fetch_resolutions(conn_assyst, batch, resolutions)
        self.save_details(conn_apuracao, details, resolutions)
        
    def run(self):
        try:
            logger.info('starting remarks dumper - version %d.%d.%d', *self.VERSION)
            conn_assyst = self.connect_db_assyst()
            conn_apuracao = self.connect_db_apuracao()
            self.dump_remarks(conn_assyst, conn_apuracao)
            self.dump_details(conn_assyst, conn_apuracao)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao)
    app.run()
    