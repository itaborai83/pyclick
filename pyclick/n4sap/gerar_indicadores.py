import os
import shutil
import argparse
import sys
import pandas as pd
import sqlite3
import logging

import pyclick.util as util
import pyclick.config as config
import pyclick.n4sap.config as n4_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('gerar_indicadores')

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
    
    def connect_db(self):
        logger.info('connecting to db')
        result_db = os.path.join(self.dir_apuracao, n4_config.RESULT_DB)
        conn = sqlite3.connect(result_db)
        return conn
    
    def list_actions(self, conn):
        logger.info('listing Click actions')
        sql = util.get_query('LISTA_ACOES')
        df = pd.read_sql(sql, conn, index_col=None)
        return df
        
    def compute_slas(self, conn):
        logger.info('computing SLA\'s')
        sql = util.get_query('SLA')
        df = pd.read_sql(sql, conn, index_col=None)
        return df
    
    def write_result(self, df_slas, df_actions):
        logger.info('writing result spreadsheet')
        rs = os.path.join(self.dir_apuracao, n4_config.KPI_SPREADSHEET)
        with pd.ExcelWriter(rs) as xw:
            df_slas.to_excel(xw, sheet_name="SLAs", index=False)
            df_actions.to_excel(xw, sheet_name="DADOS", index=False)
        
    def run(self):
        try:
            logger.info('starting geração indicadores - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            df_slas = self.compute_slas(conn)
            df_actions = self.list_actions(conn)
            self.write_result(df_slas, df_actions)
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