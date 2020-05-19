import os
import argparse
import pandas as pd
import logging

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_schedules')

SQL_SCHEDULES_INFO = util.get_query("ASSYST__FUNCIONAMENTO_MESAS")

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
    
    def connect_db(self):
        logger.info('connecting to db')
        return click_config.SQLALCHEMY_ENGINE.connect()    
    
    def get_schedules(self, conn):
        logger.info('retrieving schedules')
        df = pd.read_sql(SQL_SCHEDULES_INFO, conn, index_col=None)
        return df
    
    def save_schedules(self, df):
        logger.info('saving schedules')
        curdir = os.getcwd()
        try:
            os.chdir(self.dir_apuracao)
            df.to_excel(config.BUSINESS_HOURS_SPREADSHEET, index=False)
        finally:
            os.chdir(curdir)
    def run(self):
        try:
            logger.info('starting scheduler dumper - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            df = self.get_schedules(conn)
            self.save_schedules(df)
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
    