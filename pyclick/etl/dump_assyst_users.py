import os
import argparse
import pandas as pd
import logging
import io
import lmdb

from fastavro import writer, reader, parse_schema, schemaless_writer
from fastavro.schema import load_schema

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config
import pyclick.etl.config as etl_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_assyst_user')

SQL_USERS = util.get_query("ASSYST__DUMP_ASSYST_USERS")

class App(object):
    
    VERSION = (1, 0, 0)
    DB_MAP_SIZE = 10 * 1024 * 1024 * 1024
    DB_MAX_DBS = 100

    def __init__(self, output):
        self.schema_file = etl_config.ASSYST_USERS_SCHEMA_FILE
        self.output = output
    
    def parse_schema(self):
        logger.info('parsing avro schema')
        return load_schema(self.schema_file)
        
    def connect_db(self):
        logger.info('connecting to db')
        return click_config.SQLALCHEMY_ENGINE.connect()    
    
    def fetch_assyst_users(self, conn):
        logger.info('fetching assyst_users')
        df = pd.read_sql(SQL_USERS, conn, index_col=None)
        return df
        
    def save_assyst_users(self, assyst_users_df):
        def generator(df):
            for row in df.itertuples():
                yield (
                    row.ASSYST_USR_ID, 
                    {
                        "ASSYST_USR_ID"	    : row.ASSYST_USR_ID
                    ,   "ASSYST_USR_SC"     : row.ASSYST_USR_SC
                    ,   "ASSYST_USR_N"      : row.ASSYST_USR_N
                    ,   "ASSYST_USR_RMK"    : row.ASSYST_USR_RMK
                    ,   "SERV_DEPT_ID"      : row.SERV_DEPT_ID
                    ,   "SERV_DEPT_SC"      : row.SERV_DEPT_SC
                    ,   "SERV_DEPT_N"       : row.SERV_DEPT_N
                    }
                )
        import pyclick.etl.load_repo as r
        repo = r.LoadRepo(self.output)
        repo.save_assyst_users(self.schema_file, generator(assyst_users_df))
        
    def run(self):
        conn = None
        try:
            logger.info('starting assyst users dumper - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            assyst_users_df = self.fetch_assyst_users(conn)
            self.save_assyst_users(assyst_users_df)
            logger.info('finished')
        finally:
            if conn:
                conn = None
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=str, help='output file')
    args = parser.parse_args()
    app = App(args.output)
    app.run()
    