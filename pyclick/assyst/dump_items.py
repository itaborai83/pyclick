import os
import shutil
import argparse
import sys
import pandas as pd
import sqlite3
import logging

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_items')

SQL_LIST_ITENS = util.get_query("ASSYST__BASE_ITENS")

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_import):
        self.dir_import = dir_import
    
    def connect_db(self):
        logger.info('connecting to db')
        return click_config.SQLALCHEMY_ENGINE.connect()    
    
    def get_items(self, conn):
        logger.info('retrieving items database')
        df = pd.read_sql(SQL_LIST_ITENS, conn, index_col=None)
        return df
    
    def save_items(self, df):
        logger.info('saving items')
        curdir = os.getcwd()
        try:
            os.chdir(self.dir_import)
            conn = sqlite3.connect(config.ITEMS_DB)
            df.to_sql("ITEMS", conn, if_exists='replace', index=False)
            conn.execute("VACUUM")
            conn.commit()
        finally:
            os.chdir(curdir)
    def run(self):
        logger.info('starting items db dumper - version %d.%d.%d', *self.VERSION)
        conn = self.connect_db()
        df = self.get_items(conn)
        self.save_items(df)
        logger.info('finished')

            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_import', type=str, help='diretório de importação')
    args = parser.parse_args()
    app = App(args.dir_import)
    app.run()
    