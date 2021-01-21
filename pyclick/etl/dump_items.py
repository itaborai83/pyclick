import os
import argparse
import pandas as pd
import logging

from fastavro import writer, reader, parse_schema
from fastavro.schema import load_schema
#from fastavro.schema import parse
#from fastavro.codecs import DeflateCodec
#from fastavro.datafile import DataFileWriter
#from fastavro.io import DatumWriter

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_items')

SQL_ITEMS_DB = util.get_query("ASSYST__BASE_ITENS")

class App(object):
    
    VERSION = (1, 0, 0)
    
    def __init__(self, schema_file, output):
        self.schema_file = schema_file
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
    
    def save_items(self, schema, items_df):        
        def generator(items_df):
            for row in items_df.itertuples():
                yield {
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
        fh = open(self.output, "wb")
        writer(fh, schema, generator(items_df), 'deflate')
            
    def run(self):
        conn = None
        try:
            logger.info('starting scheduler dumper - version %d.%d.%d', *self.VERSION)
            schema = self.parse_schema()
            conn = self.connect_db()
            items_df = self.fetch_items(conn)
            self.save_items(schema, items_df)
            logger.info('finished')
        finally:
            if conn:
                conn = None
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('schema', type=str, help='schema file')
    parser.add_argument('output', type=str, help='output file')
    args = parser.parse_args()
    app = App(args.schema, args.output)
    app.run()
    