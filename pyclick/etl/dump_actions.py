import os
import argparse
import pandas as pd
import logging
import pprint
from fastavro import writer, reader, parse_schema
from fastavro.schema import load_schema

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config
import pyclick.etl.config as etl_config
import pyclick.etl.load_repo as r

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_actions')

SQL_ACTIONS = util.get_query("ASSYST__DUMP_ACTIONS")

class App(object):
    
    VERSION = (1, 0, 0)
    INTERNAL_ASSIGNMENT_ACTION = 1
    INCIDENT_CLOSING_ACTIONS = set([
        4	# PENDING-CLOSURE	/ Resolver
    ,   5	# CLOSURE	        / Encerrar
    ,   18	# CANCELLED	        / Cancelado
    ,   151	# CANCELAR	        / Cancelar    
    ])
    PRINT_ACTIONS = False
    PRINT_INDEXES_ENTRIES = False
    
    def __init__(self, output, index_output, start_dt, end_dt, open, closed):
        assert start_dt <= end_dt
        assert len(start_dt) == len('yyyy-mm-dd')
        assert len(end_dt) == len('yyyy-mm-dd')
        assert open or closed
        self.schema_file        = etl_config.ACTIONS_SCHEMA_FILE
        self.index_schema_file  = etl_config.ACTIONS_IDX01_SCHEMA_FILE
        self.output             = output
        self.index_output       = index_output
        self.start_dt           = start_dt  + ' 00:00:00'
        self.end_dt             = end_dt    + ' 23:59:59'
        self.open               = (1 if open else 0)
        self.closed             = (1 if closed else 0)
            
    def parse_schemas(self):
        logger.info('parsing avro schema')
        schema = load_schema(self.schema_file)
        index_schema = load_schema(self.index_schema_file)
        return schema, index_schema 
        
    def connect_db(self):
        logger.info('connecting to db')
        return click_config.SQLALCHEMY_ENGINE.connect()    
    
    def fetch_actions(self, conn):
        logger.info('fetching actions')
        params = (self.start_dt, self.end_dt)
        sql = SQL_ACTIONS.format(self.open, self.closed)
        df = pd.read_sql(sql, conn, params=params, index_col=None)
        return df
        
    def save_actions(self, actions_df):
        def generator(actions_df):
            for row in actions_df.itertuples():
                assert row.IS_RESOLUTION in ('y', 'n')
                assert row.DATE_ACTIONED <= self.end_dt
                action = {
                    "ACT_REG_ID"		: row.ACT_REG_ID
                ,   "INCIDENT_ID"		: row.INCIDENT_ID
                ,   "DATE_ACTIONED"	    : row.DATE_ACTIONED
                ,   "ACT_TYPE_ID"		: row.ACT_TYPE_ID
                ,   "ACT_TYPE_SC"		: row.ACT_TYPE_SC
                ,   "ACT_TYPE_N"		: row.ACT_TYPE_N
                ,   "SUPPLIER_ID"		: row.SUPPLIER_ID
                ,   "SERV_DEPT_ID"		: row.SERV_DEPT_ID
                ,   "SERV_DEPT_SC"		: row.SERV_DEPT_SC
                ,   "SERV_DEPT_N"		: row.SERV_DEPT_N
                ,   "ASS_USR_ID"		: row.ASS_USR_ID
                ,   "TIME_TO_RESOLVE"	: row.TIME_TO_RESOLVE
                ,   "ACT_TYPE_ID"		: row.ACT_TYPE_ID
                ,   "ASSIGNMENT_TIME"	: row.ASSIGNMENT_TIME       # can actually be higher than END_DT for the last action. Don't know how to handle
                ,   "IS_RESOLUTION"	    : row.IS_RESOLUTION == 'y'
                ,   "USER_STATUS"		: row.USER_STATUS
                ,   "REMARKS"			: row.REMARKS
                }
                if self.PRINT_ACTIONS:
                    pprint.pprint(action)
                yield action
        logger.info('saving action entries')
        r.save_avro(self.schema_file, self.output, generator(actions_df))
    
    def _create_index_entries(self, actions):
        assert len(actions) > 0
        assignments      = []
        curr_index_entry = None
        last_row         = None
        for row in actions:
            # assert the actions belong to the same incident and that they are ordered
            assert last_row is None or (\
                (row.INCIDENT_ID == last_row.INCIDENT_ID) and \
                (row.ACT_REG_ID   > last_row.ACT_REG_ID) 
            )
            
            # save the last row for processing after the for loop
            last_row = row
            
            if row.ACT_TYPE_ID != self.INTERNAL_ASSIGNMENT_ACTION:
                # if the current action is not an internal assignment    
                if curr_index_entry:
                    # update the end date of the current assignment with the date of the current action
                    curr_index_entry[ "NEXT_DATE_ACTIONED" ] = row.DATE_ACTIONED
                else:
                    # do nothing because there is not a valid assignment yet.
                    # in practice this asserts that the first action needs to be an internal assignment
                    assert 1 == 2 # should not happen

            else:
                if row.ACT_TYPE_ID == self.INTERNAL_ASSIGNMENT_ACTION:
                    # if the current action is an internal assignment
                    if curr_index_entry:
                        # update the current index entry
                        curr_index_entry[ "NEXT_DATE_ACTIONED" ] = row.DATE_ACTIONED
                        assignments.append(curr_index_entry)
                    
                    curr_index_entry = {
                        "SERV_DEPT_ID"          : row.SERV_DEPT_ID
                    ,   "SERV_DEPT_SC"          : row.SERV_DEPT_SC
                    ,   "SERV_DEPT_N"           : row.SERV_DEPT_N
                    ,   "DATE_ACTIONED"         : row.DATE_ACTIONED
                    ,   "NEXT_DATE_ACTIONED"    : row.DATE_ACTIONED # zero duration action by default
                    ,   "INCIDENT_ID"           : row.INCIDENT_ID
                    ,   "ACT_REG_ID"            : row.ACT_REG_ID
                    }
                else:
                    assert 1 == 2 # should not happen
        assert curr_index_entry != None
        assert len(assignments) == 0 or assignments[ -1 ] != curr_index_entry
        assignments.append(curr_index_entry)
        # assert len(assignments) > 0 # assignments can have lenght zero if there is a single internal assignment
        # if the incident remains open after the last action
        # assign the end date as its end date
        if last_row.ACT_TYPE_ID not in self.INCIDENT_CLOSING_ACTIONS:
            assignments[ -1 ][ "NEXT_DATE_ACTIONED" ] = self.end_dt
        return assignments
    
    def index_actions(self, actions_df):
        def generator(actions_df):
            last_row         = None
            curr_incident    = []
            incident_actions = []
            
            if len(actions_df) == 0:
                # bailing out early to avoid post loop processing
                return
                
            for row in actions_df.itertuples():                
            
                if last_row is None or last_row.INCIDENT_ID == row.INCIDENT_ID:
                    incident_actions.append(row)
                
                else: 
                    if len(incident_actions) > 0:
                        # process grouped actions
                        index_entries = self._create_index_entries(incident_actions)
                        for index_entry in index_entries:
                            if self.PRINT_INDEXES_ENTRIES:
                                pprint.pprint(index_entry)
                            yield index_entry
                    # start a new action grouping containing the current row
                    incident_actions = [ row ]
                # save the current row to compare with the next one
                last_row = row
            
            assert len(incident_actions) > 0 # don't know if this holds true in every case. Asserting for safety
            index_entries = self._create_index_entries(incident_actions)
            for index_entry in index_entries:
                yield index_entry
                
        logger.info('saving index entries for internal assignments')
        r.save_avro(self.index_schema_file, self.index_output, generator(actions_df))
        
    def run(self):
        conn = None
        try:
            logger.info('starting incidents dumper - version %d.%d.%d', *self.VERSION)
            schema, index_schema = self.parse_schemas()
            conn = self.connect_db()
            actions_df = self.fetch_actions(conn)
            self.save_actions(actions_df)
            self.index_actions(actions_df)
            logger.info('finished')
        finally:
            if conn:
                conn = None
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--closed',     action='store_true',    help='dump closed incidents')
    parser.add_argument('--open',       action='store_true',    help='dump open incidents')
    parser.add_argument('output',       type=str,               help='output file')
    parser.add_argument('index_output', type=str,               help='index output file')
    parser.add_argument('start_dt',     type=str,               help='start date')
    parser.add_argument('end_dt',       type=str,               help='end date')
    args = parser.parse_args()
    app = App(
        args.output
    ,   args.index_output
    ,   args.start_dt
    ,   args.end_dt
    ,   args.open
    ,   args.closed
    )
    app.run()
    
    