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

logger = util.get_logger('dump_users')

SQL_USERS = util.get_query("ASSYST__USERS")

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
    
    def fetch_users(self, conn):
        logger.info('fetching users')
        df = pd.read_sql(SQL_USERS, conn, index_col=None)
        return df
    
    def save_users(self, schema, users_df):
        def generator(users_df):
            for row in users_df.itertuples():
                yield {
                    "USR_ID"          	: row.USR_ID
                ,   "USR_SC"          	: row.USR_SC
                ,   "USR_N"           	: row.USR_N
                ,   "USR_RMK"         	: row.USR_RMK
                ,   "USR_ROLE_ID"     	: row.USR_ROLE_ID
                ,   "USR_ROLE_SC"     	: row.USR_ROLE_SC
                ,   "USR_ROLE_N"      	: row.USR_ROLE_N
                ,   "SECTN_DEPT_ID"   	: row.SECTN_DEPT_ID
                ,   "SECTN_DEPT_SC"   	: row.SECTN_DEPT_SC
                ,   "DEPT_ID"			: row.DEPT_ID
                ,   "DEPT_SC"         	: row.DEPT_SC
                ,   "DEPT_N"          	: row.DEPT_N
                ,   "SECTN_ID"        	: row.SECTN_ID
                ,   "SECTN_SC"        	: row.SECTN_SC
                ,   "SECTN_N"         	: row.SECTN_N
                ,   "BRANCH_ID"       	: row.BRANCH_ID
                ,   "BRANCH_SC"       	: row.BRANCH_SC
                ,   "BRANCH_N"        	: row.BRANCH_N
                ,   "ORGANIZACAO_ID"  	: row.ORGANIZACAO_ID
                ,   "ORGANIZACAO_SC"	: row.ORGANIZACAO_SC
                ,   "ORGANIZACAO_N"   	: row.ORGANIZACAO_N
                ,   "COMPANHIA_ID"    	: row.COMPANHIA_ID
                ,   "COMPANHIA_SC"    	: row.COMPANHIA_SC
                ,   "COMPANHIA_N"     	: row.COMPANHIA_N
                ,   "SITE_ID"         	: row.SITE_ID
                ,   "SITE_SC"         	: row.SITE_SC
                ,   "SITE_N"          	: row.SITE_N
                ,   "SITE_RMK"        	: row.SITE_RMK
                ,   "SALA_SITE_ID"    	: row.SALA_SITE_ID 
                ,   "SALA_SITE_SC"    	: row.SALA_SITE_SC
                ,   "SALA_ID"         	: row.SALA_ID
                ,   "SALA_SC"         	: row.SALA_SC
                ,   "SALA_N"          	: row.SALA_N
                ,   "CIDADE_ID"       	: row.CIDADE_ID
                ,   "CIDADE_SC"       	: row.CIDADE_SC
                ,   "CIDADE_N"        	: row.CIDADE_N
                ,   "ESTADO_ID"       	: row.ESTADO_ID
                ,   "ESTADO_SC"       	: row.ESTADO_SC
                ,   "ESTADO_N"        	: row.ESTADO_N
                ,   "PAIS_ID"         	: row.PAIS_ID
                ,   "PAIS_SC"         	: row.PAIS_SC
                ,   "PAIS_N"          	: row.PAIS_N
                }
        fh = open(self.output, "wb")
        writer(fh, schema, generator(users_df), 'deflate')
            
    def run(self):
        conn = None
        try:
            logger.info('starting user dumper - version %d.%d.%d', *self.VERSION)
            schema = self.parse_schema()
            conn = self.connect_db()
            users_df = self.fetch_users(conn)
            self.save_users(schema, users_df)
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
    