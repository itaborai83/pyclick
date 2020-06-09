import os
import argparse
import pandas as pd
import logging

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_schedules')

SQL_SURVEYS = util.get_query("ASSYST__PESQ_SATISFACAO")

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao, start_date, end_date):
        self.dir_apuracao = dir_apuracao
        self.start_date = start_date + " 00:00:00"
        self.end_date = end_date + " 00:00:00"
    
    def connect_db(self):
        logger.info('connecting to db')
        return click_config.SQLALCHEMY_ENGINE.connect()    
    
    def read_mesas(self):
        logger.info('reading mesas list')
        return util.read_mesas(self.dir_apuracao)

    def scrub_input(self, mesa):
        clean =  mesa\
                    .replace('\'', '')      \
                    .replace('"', '')       \
                    .replace('--', '')      \
                    .replace('NULL', '')    \
                    .strip()
        return clean
                    
    def get_surveys(self, conn, mesas):
        logger.info('retrieving surveys')
        mesas_scrubbed = [ '\'' + self.scrub_input(mesa) + '\'' for mesa in mesas ]
        mesas_txt = ", ".join(mesas_scrubbed)
        sql = SQL_SURVEYS.replace("{MESAS}", mesas_txt)
        args = self.start_date, self.end_date
        df = pd.read_sql(sql, conn, index_col=None, params=args)
        return df
    
    def save_surveys(self, df):
        logger.info('saving surveys')
        curdir = os.getcwd()
        try:
            os.chdir(self.dir_apuracao)
            df.to_excel(config.SURVEYS_SPREADSHEET, index=False)
        finally:
            os.chdir(curdir)
    
    def run(self):
        try:
            logger.info('starting surveys dumper - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            mesas = self.read_mesas()
            df = self.get_surveys(conn, mesas)
            self.save_surveys(df)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    parser.add_argument('start_date', type=str, help='data início período de apuração')
    parser.add_argument('end_date', type=str, help='data fim período de apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.start_date, args.end_date)
    app.run()
    