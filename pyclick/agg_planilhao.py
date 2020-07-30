# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import glob
import argparse
import logging
import datetime as dt
import pandas as pd
import sqlite3
import concurrent.futures

import pyclick.ranges as ranges
import pyclick.util as util
import pyclick.config as config
from pyclick.repo import Repo

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('agg_planilhao')

SQL_REL_MEDICAO_SELECT  = util.get_query("IMPORT__REL_MEDICAO_SELECT")
SQL_REL_MEDICAO_DDL     = util.get_query("IMPORT__REL_MEDICAO_DDL")
SQL_REL_MEDICAO_UPSERT  = util.get_query("IMPORT__REL_MEDICAO_UPSERT")


class App(object):
        
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_work):
        assert dump_file.endswith('.db.gz')
        self.dir_work = dir_work
        
    def validate_filename(self):
        logger.info(f'validating filename {self.dump_file}')
        is_open = 'OPEN' in self.dump_file
        is_closed = 'CLOSED' in self.dump_file
        is_db_gz = self.dump_file.endswith('.db.gz')
        if not is_db_gz or (not is_open and not is_closed):
            logger.error(f'invalid filename {self.dump_file}')
            sys.exit(1)
        return is_open
    
    def read_dump(self):
        logger.info(f'readig dump file {self.dump_file}')
        filename = os.path.join(self.dir_import, self.dump_file)
        dump_file_without_gz = self.dump_file[ :-3 ]
        decompressed_filename = os.path.join(self.dir_work, "$WORK-" + dump_file_without_gz)
        logger.info('lendo arquivo %s', filename)
        util.decompress_to(filename, decompressed_filename)
        conn = sqlite3.connect(decompressed_filename)
        df = pd.read_sql(SQL_REL_MEDICAO_SELECT, conn)
        util.sort_rel_medicao(df)
        del conn
        os.unlink(decompressed_filename)
        return df
    
    def apply_cutoff_date_closed(self, df):
        logger.info('filtrando eventos encerrados após a data de corte %s', self.cutoff_date)
        df = df[ df.data_resolucao_chamado < self.cutoff_date ]
        return df.copy()

    def apply_cutoff_date_open(self, df):
        logger.info('filtrando eventos abertos após a data de corte %s', self.cutoff_date)
        df = df[ df.data_abertura_chamado < self.cutoff_date ]
        return df.copy()
    
    def save(self, df, db_name):
        logger.info(f'salvando planilhão filtrado {db_name}')
        conn = sqlite3.connect(db_name)
        conn.executescript(SQL_REL_MEDICAO_DDL)
        param_sets = list(df.itertuples(index=False))
        conn.executemany(SQL_REL_MEDICAO_UPSERT, param_sets)
        conn.commit()
        conn.execute("VACUUM")
        conn.close()
        del conn
        logger.info('compressing...')
        util.compress_to(db_name, db_name + '.gz')
        os.unlink(db_name)
        
    def run(self):
        try:
            logger.info('started dump file indexing - version %d.%d.%d', *self.VERSION)
            all_events = self.read_index()
            is_open = self.validate_filename()
            df = self.read_dump()
            if is_open:
                df = self.apply_cutoff_date_open(df)
            else:
                df = self.apply_cutoff_date_closed(df)
            df = df[ df.id_chamado.isin(all_events) ].copy()
            dbname = os.path.join(self.dir_work, self.output_file)
            self.save(df, dbname)
            logger.info("finished")
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    parser.add_argument('dir_import', type=str, help='diretório importação')
    parser.add_argument('dir_work', type=str, help='diretório de trabalho')
    parser.add_argument('dump_file', type=str, help='arquivo planilhão')
    parser.add_argument('cutoff_date', type=str, help='data de corte')
    parser.add_argument('agg_index_file', type=str, help='índice agregado')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.dir_import, args.dir_work, args.dump_file, args.cutoff_date, args.agg_index_file)
    app.run()
    
    
    
    