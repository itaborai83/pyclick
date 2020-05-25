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
import pyclick.kpis as kpis
from pyclick.n4sap.kpis import PrpHandler

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('kpis2')
    
class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
    
    def connect_db(self):
        logger.info('connecting to db')
        result_db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        conn = sqlite3.connect(result_db)
        return conn
    
    def get_actions(self, conn):
        logger.info('retrieving actions')
        sql = "SELECT * FROM VW_REL_MEDICAO ORDER BY DATA_INICIO_ACAO, ID_CHAMADO, ID_ACAO"
        df = pd.read_sql(sql, conn)
        return df
       
    def compute_kpis(self, conn, df, xw):
        logger.info('calculating KPI\'s')
        f = None #lambda row: row.ID_CHAMADO == '400982'
        kpi_runner = kpis.Runner(f)
        prp_handler = PrpHandler()
        kpi_runner.add_handler(prp_handler)
        kpi_runner.run(df)
        prp_handler.write_details('PRP_DETALHES', xw)
        
    def open_spreadsheet(self):
        logger.info("opening KPI spreadsheet")
        ks = os.path.join(self.dir_apuracao, "__" + n4_config.KPI_SPREADSHEET)
        if os.path.exists(ks):
            logger.warning("KPI spreadsheet already exists. Deleting it")
            os.unlink(ks)
        return pd.ExcelWriter(ks, datetime_format=None)
            
    def run(self):
        try:
            logger.info('starting geração indicadores - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            df = self.get_actions(conn)
            with self.open_spreadsheet() as xw:
                self.compute_kpis(conn, df, xw)
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
    