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

logger = util.get_logger('dump_actions')

SQL_ACTIONS = util.get_query("ASSYST__DUMP_ACTIONS")

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
    
    def fetch_actions(self, conn):
        logger.info('fetching actions')
        df = pd.read_sql(SQL_ACTIONS, conn, index_col=None)
        return df
        
    def save_actions(self, schema, actions_df):
        def generator(actions_df):
            #actions_df = actions_df.where(pd.notnull(actions_df), None)
            for row in actions_df.itertuples():
                assert row.IS_RESOLUTION in ('y', 'n')
                yield {
                    "ACT_REG_ID"		: row.ACT_REG_ID
                ,    "INCIDENT_ID"		: row.INCIDENT_ID
                ,    "DATE_ACTIONED"	: row.DATE_ACTIONED
                ,    "ACT_TYPE_N"		: row.ACT_TYPE_N
                ,    "SUPPLIER_ID"		: row.SUPPLIER_ID
                ,    "ASS_SVD_ID"		: row.ASS_SVD_ID
                ,    "SERV_DEPT_N"		: row.SERV_DEPT_N
                ,    "ASS_USR_ID"		: row.ASS_USR_ID
                ,    "ASSYST_USR_SC"	: row.ASSYST_USR_SC
                ,    "ASSYST_USR_N"		: row.ASSYST_USR_N
                ,    "TIME_TO_RESOLVE"	: row.TIME_TO_RESOLVE
                ,    "ACT_TYPE_ID"		: row.ACT_TYPE_ID
                ,    "ASSIGNMENT_TIME"	: row.ASSIGNMENT_TIME
                ,    "IS_RESOLUTION"	: row.IS_RESOLUTION == 'y'
                ,    "USER_STATUS"		: row.USER_STATUS
                ,    "REMARKS"			: row.REMARKS
                }
        fh = open(self.output, "wb")
        writer(fh, schema, generator(actions_df), 'deflate')
            
    def run(self):
        conn = None
        try:
            logger.info('starting incidents dumper - version %d.%d.%d', *self.VERSION)
            schema = self.parse_schema()
            conn = self.connect_db()
            actions_df = self.fetch_actions(conn)
            self.save_actions(schema, actions_df)
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
    