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

import pyclick.util as util
import pyclick.config as config
import pyclick.n4sap.config as n4_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('consolida_planilhao')

SQL_PROCESSA_CONSOLIDADO = util.get_query("PROCESSA_CONSOLIDADO")
SQL_EXPORT_OVERRIDE = util.get_query("EXPORT_OVERRIDE")

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao, skip_ddl):
        self.dir_apuracao = dir_apuracao
        self.skip_ddl     = skip_ddl
    
    def process_n4_ddl(self):
        logger.info('processando DDL do N4')
        currdir = os.getcwd()
        os.chdir(self.dir_apuracao)
        try:
            conn = sqlite3.connect(config.CONSOLIDATED_DB)
            conn.executescript(SQL_PROCESSA_CONSOLIDADO)
            conn.commit()
            conn.execute("VACUUM")
            conn.close()
        finally:
            os.chdir(currdir)
    
    def export_override_spreadsheet(self):
        logger.info('exportando planilha de override')
        db_in = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        filename_out = os.path.join(self.dir_apuracao, n4_config.OVERRIDE_SPREADSHEET)
        conn = sqlite3.connect(db_in)
        df = pd.read_sql(SQL_EXPORT_OVERRIDE, conn)
        df.to_excel(filename_out, index=False)
    
            
    def run(self):
        try:
            logger.info('começando processamento do consolidado - versão %d.%d.%d', *self.VERSION)
            if self.skip_ddl:
                logger.warning("bypassando execução de DDL")
            else:
                self.process_n4_ddl()
            self.export_override_spreadsheet()
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip_ddl', action="store_true", help='pula execução de DDL', default=False)
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.skip_ddl)
    app.run()