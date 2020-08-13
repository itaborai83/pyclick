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

logger = util.get_logger('index_planilhao')

SQL_REL_MEDICAO_SELECT = util.get_query("CONSOLIDA__REL_MEDICAO_SELECT")

class App(object):
        
    VERSION = (1, 0, 0)
    
    def __init__(self, dir_work, dir_import, dump_file, cutoff_date):
        assert dump_file.endswith('.db.gz')
        self.dir_work = dir_work
        self.dir_import = dir_import
        self.dump_file = dump_file
        self.cutoff_date = cutoff_date
        dump_file_without_db_gz = self.dump_file[ :-6 ]
        self.index_file = dump_file_without_db_gz + ".idx"
        self.csrv = pyclick.consolidator.ConsolidatorSrv(dir_import, None, None, dir_work)
        
    def read_dump(self):
        logger.info(f'lendo planilhão {self.dump_file}')
        return self.csrv.read_dump(self.dump_file)
    
    def apply_cutoff_date_closed(self, df):
        logger.info('filtrando eventos encerrados após a data de corte %s', self.cutoff_date)
        return self.csrv.apply_cutoff_date(df, self.cutoff_date, closed=True)

    def apply_cutoff_date_open(self, df):
        logger.info('filtrando eventos abertos após a data de corte %s', self.cutoff_date)
        return self.csrv.apply_cutoff_date(df, self.cutoff_date, closed=False)
        
    def update_event_mapping(self, mesa_evt_mapping, df):
        logger.info('atualizando mapeamento evento mesa')
        self.csrv.update_event_mapping(mesa_evt_mapping, df)
    
    def validate_filename(self):
        logger.info(f'validating filename {self.dump_file}')
        return self.csrv.validate_filename(self.dump_file)
            
    def run(self):
        try:
            logger.info('started dump file indexing - version %d.%d.%d', *self.VERSION)
            is_open = self.validate_filename()
            df = self.read_dump()
            if is_open:
                df = self.apply_cutoff_date_open(df)
            else:
                df = self.apply_cutoff_date_closed(df)
            mesa_evt_mapping = {}
            self.update_event_mapping(mesa_evt_mapping, df)
            index_path = os.path.join(self.dir_work, self.index_file)
            with open(index_path, "w") as fh:
                for mesa, events in sorted(mesa_evt_mapping.items()):
                    for event in sorted(events):
                        print(mesa, event, sep='\t', file=fh)
            logger.info("finished")
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_work', type=str, help='diretório de trabalho')
    parser.add_argument('dir_import', type=str, help='diretório importação')
    parser.add_argument('dump_file', type=str, help='arquivo planilhão')
    parser.add_argument('cutoff_date', type=str, help='data de corte')
    args = parser.parse_args()
    app = App(args.dir_work, args.dir_import, args.dump_file, args.cutoff_date)
    app.run()
    
    