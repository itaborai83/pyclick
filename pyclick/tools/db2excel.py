# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import glob
import shutil
import argparse
import logging
import datetime as dt
import pandas as pd
import sqlite3

import pyclick.util as util
import pyclick.config as config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('db2excel')

class App(object):
    
    VERSION = (0, 0, 0)
        
    def __init__(self, db, table, excel, sheet, overwrite):
        self.db         = db
        self.table      = table
        self.excel      = excel
        self.sheet      = sheet
        self.overwrite  = overwrite
    
    def validate(self):
        if not self.db.endswith('.db'):
            logger.error('invalid database name %s', self.db)
            sys.exit(1)
        if not self.excel.endswith('.xlsx'):
            logger.error('invalid spread sheet name %s', self.excel)
            sys.exit(2)
        if os.path.exists(self.excel) and not self.overwrite:
            logger.error('export spreadsheet already exists;. Please use --overwrite')
            sys.exit(3)
        if not os.path.exists(self.db):
            logger.error('database %s does not exist', self.db)
            sys.exit(4)
    
    def save(self, df):    
        logger.info("saving spreadsheet")        
        if self.overwrite and os.path.exists(self.excel):
            os.unlink(self.excel)
        df.to_excel(self.excel, sheet_name = self.sheet, index = False)

    def read_db(self):
        logger.info('reading db %s', self.db)
        conn = sqlite3.connect(self.db)
        sql = "SELECT * FROM {}".format(self.table) # SECURITY VULNERABILITY!!!
        df = pd.read_sql(sql, conn)
        conn.close()
        return df
        
    def run(self):
        try:
            logger.info('db2excel - versão %d.%d.%d', *self.VERSION)
            self.validate()
            df = self.read_db()
            self.save(df)
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action="store_true", default=False, help='overwrite excel')
    parser.add_argument('db', type=str, help='sqlite database name')
    parser.add_argument('table', type=str, help='sqlite table name')
    parser.add_argument('excel', type=str, help='excel spreadsheet')
    parser.add_argument('sheet', type=str, help='sheet name')
    args = parser.parse_args()
    app = App(args.db, args.table, args.excel, args.sheet, args.overwrite)
    app.run()