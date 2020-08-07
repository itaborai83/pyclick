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
import pyclick.consolidator

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('filter_planilhao')

SQL_REL_MEDICAO_SELECT  = util.get_query("IMPORT__REL_MEDICAO_SELECT")
SQL_REL_MEDICAO_DDL     = util.get_query("IMPORT__REL_MEDICAO_DDL")
SQL_REL_MEDICAO_UPSERT  = util.get_query("IMPORT__REL_MEDICAO_UPSERT")

class App(object):
        
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao, dir_import, dir_work, dump_file, cutoff_date):
        assert dump_file.endswith('.db.gz')
        self.dir_apuracao = dir_apuracao
        self.dir_import = dir_import
        self.dir_work = dir_work
        self.dump_file = dump_file
        self.cutoff_date = cutoff_date
        dump_file_without_db_gz = self.dump_file[ :-6 ]
        self.output_file = dump_file_without_db_gz + "-FILTER.db"
        self.csrv = pyclick.consolidator.ConsolidatorSrv(dir_import, None, dir_apuracao, dir_work)
        
    def read_index(self):
        logger.info(f'reading aggregate index file')
        index_df = self.csrv.read_aggregate_index_mesas(self.dir_work)
        all_events = set(index_df[ 'id_chamado' ].to_list())
        return all_events
        
    def validate_filename(self):
        logger.info(f'validating filename {self.dump_file}')
        return self.csrv.validate_filename(self.dump_file)
    
    def read_dump(self):
        logger.info(f'readig dump file {self.dump_file}')
        return self.csrv.read_dump(self.dump_file)
    
    def apply_cutoff_date_closed(self, df):
        logger.info('filtrando eventos encerrados após a data de corte %s', self.cutoff_date)
        return self.csrv.apply_cutoff_date(df, self.cutoff_date, closed=True)

    def apply_cutoff_date_open(self, df):
        logger.info('filtrando eventos abertos após a data de corte %s', self.cutoff_date)
        return self.csrv.apply_cutoff_date(df, self.cutoff_date, closed=False)
        
    def save(self, df, db_name):
        logger.info(f'salvando planilhão filtrado {db_name}')
        self.csrv.save(df, db_name)
        
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
            df = self.csrv.filter_events(df, all_events)
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
    
    
    
    