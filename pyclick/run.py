import sys
import os
import os.path
import glob
import argparse
import logging
import datetime as dt
import shutil
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
        
    def cleanup(self):
        consolidated_dir = util.get_consolidated_dir(self.dir_apuracao)
        consolidated_file = util.get_consolidated_file(self.dir_apuracao)
        processed_file = util.get_processed_file(self.dir_apuracao)
        processed_db = util.get_processed_db(self.dir_apuracao)

        if os.path.exists(consolidated_dir):
            logger.warning("rm -R %s", consolidated_dir)
            shutil.rmtree(consolidated_dir)
        os.mkdir(consolidated_dir)
        if os.path.exists(processed_file):
            logger.warning("rm %s", processed_file)
            os.unlink(processed_file)
        if os.path.exists(processed_db):
            logger.warning("rm %s", processed_db)
            os.unlink(processed_db)
        
    def run(self):
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
            logger.info('******************************************************************************')            
            logger.info('******************************************************************************')
            logger.info('cleaning up')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('')
            self.cleanup()
            
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')            
            logger.info('******************************************************************************')
            logger.info('preprocessing input files')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')            
            logger.info('')
            pif.App(self.dir_apuracao).run()
            
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')            
            logger.info('******************************************************************************')
            logger.info('consolidating input files')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')            
            logger.info('')
            cp.App(self.dir_apuracao, self.cutoff_date).run()

            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('concatenating and deduping')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')            
            logger.info('')
            cd.App(self.dir_apuracao).run()
            
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')            
            logger.info('******************************************************************************')
            logger.info('processing consolidated file and generating db')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')
            logger.info('******************************************************************************')            
            logger.info('')            
            pd.App(self.dir_apuracao).run()
            
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