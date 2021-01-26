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
    
    def __init__(self, schema_file, output, start_dt, end_dt, open, closed):
        assert start_dt <= end_dt
        assert len(start_dt) == len('yyyy-mm-dd')
        assert len(end_dt) == len('yyyy-mm-dd')
        assert open or closed
        self.schema_file = schema_file
        self.output = output
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.open = 1 if open else 0
        self.closed = 1 if closed else 0
        
    def connect_db(self):
        logger.info('connecting to db')
        return click_config.SQLALCHEMY_ENGINE.connect()    
    
    def fetch_incidents(self, conn):
        logger.info('fetching incidents')
        params = (self.start_dt, self.end_dt)
        sql = SQL_INCIDENTS.format(self.open, self.closed)
        df = pd.read_sql(sql, conn, params=params, index_col=None)
        return df

    def save_incidents(self, incidents_df):
        def generator(df):
            for row in df.itertuples():
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
        import pyclick.etl.load_repo as r
        r.save_avro(self.schema_file, self.output, generator(incidents_df))
            
    def run(self):
        conn = None
        try:
            logger.info('starting incidents dumper - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            incidents_df = self.fetch_incidents(conn)
            self.save_incidents(incidents_df)
            logger.info('finished')
        finally:
            if conn:
                conn = None
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--open', action='store_true', help='dump open incidents')
    parser.add_argument('--closed', action='store_true', help='dump closed incidents')
    parser.add_argument('schema', type=str, help='schema file')
    parser.add_argument('output', type=str, help='output file')
    parser.add_argument('start_dt', type=str, help='start date')
    parser.add_argument('end_dt', type=str, help='end date')    
    args = parser.parse_args()
    app = App(args.schema, args.output, args.start_dt, args.end_dt, args.open, args.closed)
    app.run()
    