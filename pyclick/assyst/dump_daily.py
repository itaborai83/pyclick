import os
import shutil
import argparse
import sys
import pandas as pd
import sqlalchemy
import logging
import datetime as dt
import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as assyst_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_daily')

SQL_DAILY_DUMP = util.get_query("ASSYST__QUERY_PLANILHAOv2")

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_staging, date, compress):
        self.dir_staging    = dir_staging
        self.date           = date
        self.compress       = compress
        self.start_dt       = util.prior_date(date) + " 00:00:00"
        self.end_dt         = util.prior_date(date) + " 23:59:59"
    
    def connect_db(self):
        logger.info('connecting to db')
        return assyst_config.SQLALCHEMY_ENGINE.connect()
        
    def get_daily_dump(self, conn):
        logger.info('retrieving daily dump')
        logger.info('starting ... %s', dt.datetime.now())
        params = (self.start_dt, self.end_dt)
        df = pd.read_sql_query(SQL_DAILY_DUMP, conn, index_col=None, params=params)
        logger.info('done ... %s', dt.datetime.now())
        return df
    
    def save_daily_dump(self, df):
        logger.info('saving daily dump')
        curdir = os.getcwd()
        try:
            os.chdir(self.dir_staging)
            filename = self.date + ".csv"
            logger.info("saving file %s to dir %s", self.date, self.dir_staging)
            df.to_csv( 
                filename,
                sep         = ";",
                index       = False,
                decimal     = ","
            )
            if self.compress:
                logger.info('compressing output file')
                util.compress(filename)
        finally:
            os.chdir(curdir)
    def run(self):
        try:
            logger.info('starting daily dumper - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            df = self.get_daily_dump(conn)
            self.save_daily_dump(df)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--compress', action='store_true', default=False, help='comprimir arquivo de saída' )
    parser.add_argument('dir_staging', type=str, help='diretório de staging')
    parser.add_argument('date', type=str, help='data planilhão')
    args = parser.parse_args()
    app = App(args.dir_staging, args.date, args.compress)
    app.run()
    