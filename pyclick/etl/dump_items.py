import io
import os
import argparse
import pandas as pd
import logging
import lmdb
from fastavro import writer, reader, parse_schema, schemaless_writer
from fastavro.schema import load_schema

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config
import pyclick.etl.config as etl_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_items')

SQL_ITEMS_DB = util.get_query("ASSYST__DUMP_ITEMS")

class App(object):
    
    VERSION = (1, 0, 0)
    DB_MAX_DBS = 100
    DB_MAP_SIZE = 10 * 1024 * 1024 * 1024
    
    def __init__(self, output):
        self.schema_file = etl_config.ITEMS_SCHEMA_FILE
        self.output = output
    
    def parse_schema(self):
        logger.info('parsing avro schema')
        return load_schema(self.schema_file)
        
    def connect_db(self):
        logger.info('connecting to db')
        return click_config.SQLALCHEMY_ENGINE.connect()    
    
    def fetch_items(self, conn):
        logger.info('fetching items')
        df = pd.read_sql(SQL_ITEMS_DB, conn, index_col=None)
        return df
    
    def save_items(self, items_df):
        def generator(df):
            for row in df.itertuples():
                yield (row.ITEM_ID,
                    {
                        "ITEM_ID"        : row.ITEM_ID,
                        "ITEM_N"         : row.ITEM_N,
                        "PRODUCT_ID"     : row.PRODUCT_ID,
                        "PRODUCT_N"      : row.PRODUCT_N,
                        "PROD_CLS_ID"    : row.PROD_CLS_ID,
                        "PROD_CLS_N"     : row.PROD_CLS_N,
                        "GENERIC_CLS_ID" : row.GENERIC_CLS_ID,
                        "GENERIC_CLS_N"  : row.GENERIC_CLS_N,
                        "SUPPLIER_ID"    : row.SUPPLIER_ID,
                        "SUPPLIER_N"     : row.SUPPLIER_N
                    }
                )
        import pyclick.etl.load_repo as r
        repo = r.LoadRepo(self.output)
        repo.save_items(self.schema_file, generator(items_df))
        
    def run(self):
        conn = None
        try:
            logger.info('starting scheduler dumper - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            items_df = self.fetch_items(conn)
            self.save_items(items_df)
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
    