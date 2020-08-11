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

# TODO: Delete this file

ASSERT 1 == 2 # DISABLE IT FROM RUNNING
"""
assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('consolida_planilhao')

SQL_PROCESSA_CONSOLIDADO = util.get_query("PROCESSA_CONSOLIDADO")

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
    
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
            
    def run(self):
        try:
            logger.info('começando processamento do consolidado - versão %d.%d.%d', *self.VERSION)
            self.process_n4_ddl()
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao)
    app.run()
"""