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

logger = util.get_logger('index_remarks')

SQL_DDL = """
CREATE TABLE IF NOT EXISTS INCIDENTE_TERMOS(
    ID_CHAMADO  TEXT NOT NULL,
    TERMO       TEXT NOT NULL,
    FREQ		INTEGER NOT NULL,
    CONSTRAINT INCIDENTE_TERMOS_PK PRIMARY KEY(ID_CHAMADO, TERMO)
);
"""

SQL_FETCH_TEXTS = """
    WITH TEXTOS AS (
        SELECT	A.ID_CHAMADO
        ,		0 AS ID_ACAO
        ,		A.DESCRICAO AS TEXTO
        FROM	INCIDENTE_DETALHES AS A
        UNION	ALL
        SELECT	ID_CHAMADO
        ,		ID_ACAO
        ,		TEXTO
        FROM	INCIDENTE_TEXTOS IT 
        ORDER	BY 1, 2
    )
    SELECT	ID_CHAMADO
    ,		GROUP_CONCAT(TEXTO, ' ') AS TEXTO
    FROM	TEXTOS
    GROUP	BY ID_CHAMADO
    ORDER	BY ID_CHAMADO
"""

class App(object):
    
    VERSION             = (1, 0, 0)
    MIN_TERM_FREQ       = 5
    MAX_TERM_PCT_FREQ   = 0.50
    
    def __init__(self, dir_apuracao, stop_words):
        self.dir_apuracao = dir_apuracao
        self.stop_words = stop_words
    
    def connect_db(self):
        logger.info('connecting to  db')
        result_db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        conn = sqlite3.connect(result_db)
        conn.executescript(SQL_DDL)
        return conn
    
    def fetch_texts(self, conn):
        logger.info('fetching texts')
        texts_df = pd.read_sql(SQL_FETCH_TEXTS, conn, index_col=None)
        qty = len(texts_df)
        logger.info(f'{qty} texts fetched')
        return texts_df
    
    def index_incident(self, id_chamado, text, acc_terms, stop_words):
        terms = re.split(r'\s+', text)
        chamado_terms = {}
        for term in terms:
            if term in stop_words:
                continue
            if term not in acc_terms:
                acc_terms[ term ] = set()
            if term not in chamado_terms:
                chamado_terms[ term ] = 0
            acc_terms[ term ].add(id_chamado)
            chamado_terms[ term ] += 1
        return chamado_terms
    
    def build_prune_set(self, acc_terms):
        prune_set = set()
        # prune infrequent terms
        for term, chamados_set in acc_terms.items():
            if len(chamados_set) < self.MIN_TERM_FREQ:
                prune_set.add(term)
        # prune too frequent terms
        qty = len(acc_terms)
        max_term_freq = round(qty * self.MAX_TERM_PCT_FREQ)
        for term, chamados_set in acc_terms.items():
            if len(chamados_set) > max_term_freq:
                prune_set.add(term)
        #logger.debug(prune_set)
        return prune_set
        
    def prune_terms(self, chamados, acc_terms):
        prune_set = self.build_prune_set(acc_terms)
        for id_chamado, chamado_terms in chamados.items():
            exclude_terms = []
            for term, freq in chamado_terms.items():
                if term in prune_set:
                    exclude_terms.append(term)
            for term in exclude_terms:
                del chamado_terms[ term ]
        
    def clear_terms(self, conn):
        conn.executescript('DELETE FROM INCIDENTE_TERMOS')
        
    def save_terms(self, conn, id_chamado, chamado_terms):
        sql = 'insert into incidente_termos(id_chamado, termo, freq) values (?, ?, ?)'
        args_set = []
        for term, freq in chamado_terms.items():
            args_set.append( (id_chamado, term, freq) )
        conn.executemany(sql, args_set)
    
    def read_stop_words(self):
        stop_words = set()
        with open(self.stop_words) as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("#"):    
                    continue # comment
                stop_words.add(line)
        return stop_words
        
    def run(self):
        try:
            logger.info('starting remarks indexer - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            stop_words = self.read_stop_words()
            texts_df = self.fetch_texts(conn)
            acc_terms = {}
            chamado_terms = {}
            chamados = {}
            for row in texts_df.itertuples():
                chamado_terms = self.index_incident(row.ID_CHAMADO, row.TEXTO, acc_terms, stop_words)
                chamados[ row.ID_CHAMADO ] = chamado_terms
            logger.info('pruning terms')
            self.prune_terms(chamados, acc_terms)
            logger.info('clearing terms')
            self.clear_terms(conn)
            logger.info('storing terms')
            for id_chamado, chamado_terms in chamados.items():
                self.save_terms(conn, id_chamado, chamado_terms)
            conn.commit()
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    parser.add_argument('stop_words', type=str, help='arquivo de stop words')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.stop_words)
    app.run()
     