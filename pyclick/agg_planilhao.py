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
from pyclick.consolidator import ConsolidatorSrv

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('agg_planilhao')

SQL_REL_MEDICAO_SELECT  = util.get_query("IMPORT__REL_MEDICAO_SELECT")
SQL_REL_MEDICAO_DDL     = util.get_query("IMPORT__REL_MEDICAO_DDL")
SQL_REL_MEDICAO_UPSERT  = util.get_query("IMPORT__REL_MEDICAO_UPSERT")


class App(object):
        
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_work):
        self.dir_work = dir_work
        self.csrv = ConsolidatorSrv(None, None, None, dir_work)
        
    def save(self, df, db_name):
        logger.info(f'salvando planilhão filtrado {db_name}')
        self.csrv.save(df, db_name)
    
    def read_dump(self, dump_file):
        return self.csrv.read_filtered_dump(dump_file)
        
    def get_filtered_planilhoes(self):
        logger.info("reading filtered dump files")
        return self.csrv.get_filtered_planilhoes("*OPEN-FILTER.db.gz", "*CLOSED-FILTER.db.gz")
    
    def concat_planilhoes(self, open_df, closed_dfs):
        logger.info("concatenating dump files")
        return self.csrv.concat_planilhoes(open_df, closed_dfs)
        
    def run(self):
        try:
            logger.info('started filtered planilhão aggregator - version %d.%d.%d', *self.VERSION)
            open_planilhao, closed_planilhoes = self.get_filtered_planilhoes()
            logger.info(f'processing open {open_planilhao}')
            open_df = self.read_dump(open_planilhao)
            closed_dfs = []
            
            for closed_planilhao in closed_planilhoes:
                logger.info(f'processing closed {closed_planilhao}')
                closed_df = self.read_dump(closed_planilhao)
                closed_dfs.append(closed_df)

            df = self.concat_planilhoes(open_df, closed_dfs)
            db_name = os.path.join(self.dir_work, 'df.db')
            self.save(df, db_name)
            logger.info("finished")
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_work', type=str, help='diretório de trabalho')
    args = parser.parse_args()
    app = App(args.dir_work)
    app.run()
    
    
    
    