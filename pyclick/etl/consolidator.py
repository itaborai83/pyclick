import os
import os.path
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

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_incidents')

SQL_INCIDENTS = util.get_query("ASSYST__DUMP_INCIDENTS")

class App(object):
    
    VERSION         = (1, 0, 0)
    OPEN_STATUS     = 'Aberto'
    PRINT_INCIDENTS = True
    
    def __init__(self, data_dir, dimensions_db, output_file, start_dt, end_dt, mesas_file):
        assert start_dt <= end_dt
        assert len(start_dt) == len('yyyy-mm-dd')
        assert len(end_dt) == len('yyyy-mm-dd')
        self.data_dir       = data_dir
        self.dimensions_db  = dimensions_db
        self.output_file    = output_file
        self.start_dt       = start_dt
        self.end_dt         = end_dt
        self.mesas_file     = mesas_file
    
    def build_files(self):
        logger.info('building file list for searching')
        dates = util.dates_between(self.start_dt, self.end_dt)
        return {
            'open_actions_index_file'       : etl_config.OPEN_ACTIONS_IDX01_FILE_TMPLT.format(self.end_dt)
        ,   'open_actions_file'             : etl_config.OPEN_ACTIONS_FILE_TMPLT.format(self.end_dt)
        ,   'open_incidents_files'          : etl_config.OPEN_INCIDENTS_FILE_TMPLT.format(self.end_dt)
        ,   'closed_actions_index_files'    : list([ etl_config.CLOSED_ACTIONS_IDX01_FILE_TMPLT.format(d)    for d in dates ])
        ,   'closed_actions_files'          : list([ etl_config.CLOSED_ACTIONS_FILE_TMPLT.format(d)          for d in dates ])
        ,   'closed_incidents_file'         : list([ etl_config.CLOSED_INCIDENTS_FILE_TMPLT.format(d)        for d in dates ])
        }

    def search_action_index(self, index_file, mesas):
        path = self.data_dir + '/' + index_file
        logger.info(f'searching action index file {path}')
        with open(path, 'rb') as fh:
            r = reader(fh, reader_schema=etl_config.ACTIONS_IDX01_SCHEMA)
            result = set()
            for index_entry in r:
                if index_entry[ "SERV_DEPT_N" ] not in mesas:
                    continue
                if index_entry[ "DATE_ACTIONED" ] > self.end_dt:
                    continue
                if index_entry[ "NEXT_DATE_ACTIONED" ] < self.start_dt:
                    continue
                result.add( index_entry[ "INCIDENT_ID" ] )
            logger.info(f'found { len(result) } incident ids in this file')
            return result
    
    def search_action_indexes(self, files, mesas):
        result = self.search_action_index( files[ 'open_actions_index_file' ], mesas)
        for index_file in files[ 'closed_actions_index_files' ]:
            incident_ids = self.search_action_index(index_file, mesas)
            result.update(incident_ids)
        logger.info(f'found { len(result) } incident ids in total')
        return result
                    
    def run(self):
        logger.info('starting consolidator - version %d.%d.%d', *self.VERSION)
        files = self.build_files()
        mesas = set(util.read_mesas_file(self.mesas_file))
        incident_ids = self.search_action_indexes(files, mesas)
        logger.info('finished')
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir',         type=str, help='data directory')
    parser.add_argument('dimensions_db',    type=str, help='output file')
    parser.add_argument('output_file',      type=str, help='output file')
    parser.add_argument('start_dt',         type=str, help='start date')
    parser.add_argument('end_dt',           type=str, help='end date')
    parser.add_argument('mesas_file',       type=str, help='arquivo de mesas')
    args = parser.parse_args()
    app = App(args.data_dir, args.dimensions_db, args.output_file, args.start_dt, args.end_dt, args.mesas_file)
    app.run()
    