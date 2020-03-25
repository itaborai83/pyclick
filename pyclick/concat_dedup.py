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

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('concat_dedup')

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
    
    def read_planilha(self, input_file):
        consolidated_dir = util.get_consolidated_dir(self.dir_apuracao)
        filename = os.path.join(consolidated_dir, input_file)
        logger.info('lendo arquivo %s', filename)
        df = pd.read_excel(filename, verbose=False)
        headers = df.columns.to_list()
        if headers != config.RENAMED_COLUMNS:
            util.report_file_mismatch(logger, headers, config.RENAMED_COLUMNS)
            sys.exit(config.EXIT_FILE_MISMATCH)
        return df
    
    def save_planilhao(self, df):
        logger.info('salvando planilhão')
        output = util.get_consolidated_file(self.dir_apuracao)
        df.to_excel(output, index=False)
    
    def get_inputs(self):
        consolidated_dir = util.get_consolidated_dir(self.dir_apuracao)
        currdir = os.getcwd()
        try:
            os.chdir(consolidated_dir)
            inputs = list(sorted(glob.iglob(config.CONSOLIDATED_GLOB)))
            return inputs
        finally:
            os.chdir(currdir)
            
    def run(self):
        try:
            logger.info('concat_dedup - versão %d.%d.%d', *self.VERSION)
            inputs = self.get_inputs()
            if len(inputs) < 2:
                logger.error('especificar ao menos 2 arquivos')
                sys.exit(config.EXIT_TOO_FEW_FILES)
            logger.info('iniciando loop de parsing')
            dfs = []
            for input_file in inputs:
                logger.info('processsando planilha %s', input_file)
                df = self.read_planilha(input_file)
                dfs.append(df)
            assert len(dfs) > 1
            logger.info('concatenando')
            df = pd.concat(dfs)
            logger.info('removendo linhas duplicadas')
            df.drop_duplicates(keep='last', inplace=True)
            logger.info('salvando resultado')
            self.save_planilhao(df)
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao)
    app.run()