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

logger = util.get_logger('dump_incidents')

SQL_INCIDENTS = util.get_query("ASSYST__DUMP_INCIDENTS")

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
    
    def fetch_incidents(self, conn):
        logger.info('fetching incidents')
        df = pd.read_sql(SQL_INCIDENTS, conn, index_col=None)
        self.process_ids(df)
        return df

    def process_ids(self, df):
        def to_str(value):
            return (value if pd.isna(value) else str(value))
        def to_int(value):
            return (value if pd.isna(value) else int(value))
        df[ 'CHAMADO_ID'        ] = df['CHAMADO_ID'        ].apply(to_str)
        df[ 'PARENT_CHAMADO_ID' ] = df['PARENT_CHAMADO_ID' ].apply(to_str)
        
    def save_incidents(self, schema, incidents_df):
        def float_to_int(x):
            if not x and x != 0:
                return x
            return int(x)
        def generator(incidents_df):
            #incidents_df = incidents_df.where(pd.notnull(incidents_df), None)
            for row in incidents_df.itertuples():
                assert row.MAJOR_INC in ('y', 'n')
                yield {
                    "TYPE_ENUM"                 : row.TYPE_ENUM
                ,   "INCIDENT_ID"               : row.INCIDENT_ID
                ,   "PARENT_INCIDENT_ID"        : row.PARENT_INCIDENT_ID
                ,   "DATE_LOGGED"               : row.DATE_LOGGED
                ,   "INC_RESOLVE_ACT"           : row.INC_RESOLVE_ACT
                ,   "CHAMADO_ID"                : row.CHAMADO_ID
                ,   "PARENT_CHAMADO_ID"         : row.PARENT_CHAMADO_ID
                ,   "SOURCE_INCIDENT"           : row.SOURCE_INCIDENT      
                ,   "AFF_USR_ID"                : row.AFF_USR_ID        
                ,   "REP_USR_ID"                : row.REP_USR_ID
                ,   "INCIDENT_STATUS"           : row.INCIDENT_STATUS
                ,   "MAJOR_CATEGORY"            : row.MAJOR_CATEGORY
                ,   "SHORT_DESC"                : row.SHORT_DESC
                ,   "REMARKS"                   : row.REMARKS
                ,   "SERV_OFF_ID"               : row.SERV_OFF_ID
                ,   "ITEM_ID"                   : row.ITEM_ID
                ,   "ITEM_B_ID"                 : row.ITEM_B_ID
                ,   "CAUSE_ITEM_ID"             : row.CAUSE_ITEM_ID
                ,   "CATEGORY"                  : row.CATEGORY
                ,   "CAUSE_CATEGORY"            : row.CAUSE_CATEGORY
                ,   "PRIORITY_DERIVED_N"        : row.PRIORITY_DERIVED_N
                ,   "TIME_TO_RESOLVE"           : row.TIME_TO_RESOLVE
                ,   "INCIDENT_TOTAL_TIME_M"     : row.INCIDENT_TOTAL_TIME_M
                ,   "INC_RESOLVE_SLA"			: row.INC_RESOLVE_SLA
                ,   "MAJOR_INC"				    : row.MAJOR_INC	== 'y'
                }

        fh = open(self.output, "wb")
        writer(fh, schema, generator(incidents_df), 'deflate')
            
    def run(self):
        conn = None
        try:
            logger.info('starting incidents dumper - version %d.%d.%d', *self.VERSION)
            schema = self.parse_schema()
            conn = self.connect_db()
            incidents_df = self.fetch_incidents(conn)
            self.save_incidents(schema, incidents_df)
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
    