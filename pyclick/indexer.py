# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import glob
import shutil
import argparse
import logging
import datetime as dt
import pandas as pd
import sqlite3

import pyclick.util as util
import pyclick.config as config
import pyclick.consolidator as consolidator

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('indexer')

SQL_FILE_INDEX_DDL      = util.get_query('IMPORT__FILE_INDEX_DDL')
SQL_FILE_INDEX_INSERT   = util.get_query('IMPORT__FILE_INDEX_INSERT')

class IndexerSrv(object):

    def __init__(self):
        pass
    
    ###########################################################################
    # MESA INDEXING METHODS
    ###########################################################################
    
    def index_mesas(self, df):
        # TODO: create indexer class
        logger.info('indexing mesas x incident')
        result           = { 'mesa' : [], 'id_chamado' : [] }
        df_mesas         = df[ ~(df.mesa.isna()) ]
        id_chamados      = df_mesas.id_chamado.to_list() # to allow ordering
        chamados_pai     = df_mesas.chamado_pai.to_list()
        mesas            = df_mesas.mesa.to_list()
        for id_chamado, chamado_pai, mesa in zip(id_chamados, chamados_pai, mesas):
            result[ 'mesa'       ].append(mesa)
            result[ 'id_chamado' ].append(id_chamado)
            if not pd.isna(chamado_pai) and chamado_pai is not None and chamado_pai != "":
                result[ 'mesa'       ].append(mesa)
                result[ 'id_chamado' ].append(chamado_pai)
        return pd.DataFrame(result)
        
    def write_index_mesas(self, dir, date, is_open, df):
        path = self._build_path_index_mesas(dir, date, is_open)
        logger.info('writing index file %s', path)
        df.to_csv(path, sep='\t', index=False)
        
    def read_index_mesas(self, dir, date, is_open):
        path = self._build_path_index_mesas(dir, date, is_open)
        logger.info('reading index file %s', path)
        df = pd.read_csv(path, sep='\t', index_col=False)
        return df
    
    def delete_index_mesas(self, dir, date, is_open):
        path = self._build_path_index_mesas(dir, date, is_open)
        logger.info('deleting index file %s', path)
        os.unlink(path)

    def _build_path_index_mesas(self, dir, date, is_open):
        filename = date + ('-OPEN.idx.gz' if is_open else '-CLOSED.idx.gz')
        path = os.path.join(dir, filename)
        return path
    
    ###########################################################################
    # STAGING FILE INDEXING
    ###########################################################################
    
    def index_staging_file(self, staging_file, df):
        chamados = {}
        logger.debug('indexing staging file %s', staging_file)
        
        def is_open(row):
            if pd.isna(row.data_resolucao_chamado) or not row.data_resolucao_chamado:
                return True
            return False
            
        for row in df.itertuples():
            if row.id_chamado not in chamados:
                chamados[ row.id_chamado ] = {
                    'staging_file'  : staging_file,
                    'id_chamado'    : row.id_chamado,
                    'chamado_pai'   : row.chamado_pai,
                    'aberto'        : 'N' if is_open(row) else 'S',
                    'qtd_acoes'     : 1,
                    'min_id_acao'   : int(row.id_acao),
                    'max_id_acao'   : int(row.id_acao),
                }
            else:
                chamado = chamados[ row.id_chamado ]
                chamado[ 'qtd_acoes'   ] += 1
                chamado[ 'min_id_acao' ] = min(int(row.id_acao), chamado[ 'min_id_acao' ])
                chamado[ 'max_id_acao' ] = max(int(row.id_acao), chamado[ 'max_id_acao' ])
        return pd.DataFrame.from_dict(chamados, orient="index")

    def open_staging_file_index_db(self, dir_import):
        db_filename = os.path.join(dir_import, config.FILE_INDEX_DB)
        conn = sqlite3.connect(db_filename)
        conn.executescript(SQL_FILE_INDEX_DDL)
        return conn
    
    def purge_stale_index_data(self, conn, staging_file):
        logger.info("clearing stale index data for %s", staging_file)
        conn.execute("DELETE FROM FILE_INDEX WHERE NOME_ARQ = ?", (staging_file,))

    def write_staging_file_index(self, dir_import, staging_file, index_df):
        conn = self.open_staging_file_index_db(dir_import)
        self.purge_stale_index_data(conn, staging_file)
        logger.debug('generating sql statements for staging file %s', staging_file)
        params_set = []
        for row in index_df.itertuples():
            params_set.append([
                staging_file,
                row.id_chamado,
                row.chamado_pai,
                row.aberto,
                row.qtd_acoes,
                row.min_id_acao,
                row.max_id_acao
            ])
        logger.debug('inserting index data for staging file %s', staging_file)
        conn.executemany(SQL_FILE_INDEX_INSERT, params_set)
        conn.commit()
        conn.close()