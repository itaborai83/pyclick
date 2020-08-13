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

logger = util.get_logger('csv2db')

# TODO: validate sheet name
EXPORT_TABLE = 'CSV'

class App(object):
    
    VERSION = (1, 0, 0)
        
    def __init__(self, overwrite, latin1, csv, db):
        self.overwrite = overwrite
        self.latin1 = latin1
        self.csv = csv
        self.db = db
    
    def validate(self):
        if not self.db.endswith('.db'):
            logger.error('invalid database name %s', self.db)
            sys.exit(1)
        if not self.csv.endswith('.csv'):
            logger.error('invalid spread sheet name %s', self.csv)
            sys.exit(2)
        if os.path.exists(self.db) and not self.overwrite:
            logger.error('export database already exists;. Please use --overwrite')
            sys.exit(3)
        if not os.path.exists(self.csv):
            logger.error('spreadsheet %s does not exist', self.csv)
            sys.exit(4)
            
    def read_csv(self):
        logger.info("reading spreadsheet")        
        df = pd.read_csv(
            self.csv, 
            sep             = config.CSV_SEPARATOR,
            verbose         = True,
            header          = 0, 
            encoding        = ("latin_1" if self.latin1 else "utf-8"),
            error_bad_lines = True, 
            warn_bad_lines  = True,
            low_memory      = False
        )
        return df

    def save(self, df):
        logger.info('saving db %s', self.db)
        if self.overwrite and os.path.exists(self.db):
            os.unlink(self.db)
        conn = sqlite3.connect(self.db)
        df.to_sql(EXPORT_TABLE, conn, index=False, if_exists="replace")
        conn.commit()
        conn.execute("VACUUM")
        conn.close()
        
    def run(self):
        try:
            logger.info('csv2db - versão %d.%d.%d', *self.VERSION)
            self.validate()
            df = self.read_csv()
            self.save(df)
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action="store_true", default=False, help='overwrite db')
    parser.add_argument('--latin1', action="store_true", default=False, help='csv in latin-1 encoding')
    parser.add_argument('csv', type=str, help='csv file')
    parser.add_argument('db', type=str, help='sqlite database name')
    args = parser.parse_args()
    app = App(args.overwrite, args.latin1, args.csv, args.db)
    app.run()