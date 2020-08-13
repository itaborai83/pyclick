# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import glob
import argparse
import logging
import datetime as dt
import pandas as pd
import sqlite3
import concurrent.futures

import pyclick.ranges as ranges
import pyclick.util as util
import pyclick.config as config
import pyclick.consolidator

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('agg_indexes')

class App(object):
        
    VERSION = (1, 0, 0)
    
    def __init__(self, dir_import, dir_apuracao, dir_work, start_date, end_date, agg_index_file):
        self.dir_import     = dir_import
        self.dir_apuracao   = dir_apuracao
        self.dir_work       = dir_work
        self.start_date     = start_date
        self.end_date       = end_date
        self.agg_index_file = agg_index_file        
        self.csrv           = pyclick.consolidator.ConsolidatorSrv(None, None, dir_apuracao, dir_work)
        
    def read_mesas(self):
        logger.info('recuperando a listagem de mesas para apuração')
        return set(util.read_mesas(self.dir_apuracao))

    def read_index_files(self):
        logger.info(f"reading index files within {self.dir_work}")
        return self.csrv.read_index_files()
    
    def process_index_file(self, mesas, all_events, index_file):
        logger.info(f'processing index file {index_file}')
        self.csrv.process_index_file(mesas, all_events, index_file)
    
    def write_index_file(self, all_events):
        logger.info(f'writing aggregated index file {self.agg_index_file}')
        self.csrv.write_index_file(self.agg_index_file, all_events)
                
    def run(self):
        try:
            logger.info('started index aggregation program - version %d.%d.%d', *self.VERSION)
            all_events = set()
            mesas = self.read_mesas()
            assert len(mesas) > 0
            index_files = self.read_index_files()
            assert len(index_files) > 0
            for index_file in index_files:
                self.process_index_file(mesas, all_events, index_file)
            self.write_index_file(all_events)
            logger.info("finished")
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    parser.add_argument('dir_work', type=str, help='diretório de trabalho')
    parser.add_argument('agg_index_file', type=str, help='índice agregado')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.dir_work, args.agg_index_file)
    app.run()
    
    