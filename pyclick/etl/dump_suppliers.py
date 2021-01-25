import os
import argparse
import pandas as pd
import logging

from fastavro import writer, reader, parse_schema
from fastavro.schema import load_schema

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_suppliers')

SQL_SUPPLIERS = util.get_query("ASSYST__DUMP_SUPPLIERS")

class App(object):
    
    VERSION = (1, 0, 0)
    
    def __init__(self, schema_file, output):
        self.schema_file = schema_file
        self.output = output
        
    def connect_db(self):
        logger.info('connecting to db')
        return click_config.SQLALCHEMY_ENGINE.connect()    
    
    def fetch_suppliers(self, conn):
        logger.info('fetching suppliers')
        df = pd.read_sql(SQL_SUPPLIERS, conn, index_col=None)
        return df

    def save_suppliers(self, suppliers_df):
        def generator(df):
            for row in df.itertuples():
                yield (row.SUPPLIER_ID, {
                    "SUPPLIER_ID"   : row.SUPPLIER_ID
                ,   "SUPPLIER_SC"   : row.SUPPLIER_SC
                ,   "SUPPLIER_N"    : row.SUPPLIER_N
                ,   "SLA_ID"        : row.SLA_ID 
                ,   "SLA_SC"        : row.SLA_SC
                ,   "SLA_N"         : row.SLA_N
                ,   "SLA_RMK"       : row.SLA_RMK
                })
        import pyclick.etl.load_repo as r
        repo = r.LoadRepo(self.output)
        repo.save_suppliers(self.schema_file, generator(suppliers_df))
            
    def run(self):
        logger.info('starting suppliers dumper - version %d.%d.%d', *self.VERSION)
        conn = self.connect_db()
        suppliers_df = self.fetch_suppliers(conn)
        self.save_suppliers(suppliers_df)
        logger.info('finished')
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('schema', type=str, help='schema file')
    parser.add_argument('output', type=str, help='output file')
    args = parser.parse_args()
    app = App(args.schema, args.output)
    app.run()
    