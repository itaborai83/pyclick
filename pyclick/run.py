import sys
import os
import os.path
import glob
import argparse
import logging
import datetime as dt
import pandas as pd

import pyclick.util as util
import pyclick.config as config
import pyclick.preprocess_input_files as pif
import pyclick.concat_dedup as cd
import pyclick.consolida_planilhao as cp
import pyclick.processa_consolidado as pd

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('run')

class App(object):
    
    VERSION = (0, 0, 0)

    def __init__(self, dir_apuracao, cutoff_date):
        self.dir_apuracao   = dir_apuracao
        self.cutoff_date    = cutoff_date
    
    def get_consolidated_file(self):
        return os.path.join(self.dir_apuracao, config.CONSOLIDATED_DIR, config.CONSOLIDATED_FILE)

    def get_input_dir(self):
        return os.path.join(self.dir_apuracao, config.INPUT_DIR)
    
    def get_consolidated_dir(self):
        return os.path.join(self.dir_apuracao, config.CONSOLIDATED_DIR)
        
    def get_processed_file(self):
        return os.path.join(self.dir_apuracao, config.PROCESSED_FILE)
    
    def get_processed_db(self):
        return os.path.join(self.dir_apuracao, config.PROCESSED_DB)
        
    def run(self):
        input_dir = self.get_input_dir()
        consolidated_dir = self.get_consolidated_dir()
        consolidated_file = self.get_consolidated_file()
        processed_file = self.get_processed_file()
        processed_db = self.get_processed_db()
        try:
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('run - versão %d.%d.%d', *self.VERSION)
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('')
            
            logger.info('******************************************************************************')
            logger.info('preprocessing input files')
            logger.info('******************************************************************************')
            logger.info('')
            pif.App(self.dir_apuracao).run()
            
            logger.info('******************************************************************************')
            logger.info('consolidating input files')
            logger.info('******************************************************************************')
            logger.info('')
            cp.App(self.dir_apuracao, self.cutoff_date).run()

            logger.info('******************************************************************************')
            logger.info('concatenating and deduping')
            logger.info('******************************************************************************')
            logger.info('')
            cd.App(consolidated_file, consolidated_dir, [ config.CONSOLIDATED_GLOB ]).run()
            
            logger.info('******************************************************************************')
            logger.info('processing consolidated file and generating db')
            logger.info('******************************************************************************')
            logger.info('')            
            pd.App(consolidated_file, processed_file, processed_db).run()
            
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    parser.add_argument('cutoff_date', type=str, help='data de corte encerramento evento')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.cutoff_date)
    app.run()