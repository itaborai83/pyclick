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
    
    def __init__(self, output, input_dir, inputs):
        if len(inputs) == 1:
            if input_dir:
                currdir = os.getcwd()
                os.chdir(input_dir)
            inputs = list(sorted(glob.iglob(inputs[0])))
            if input_dir:
                os.chdir(currdir)
        self.output     = output
        self.input_dir  = input_dir
        self.inputs     = inputs
    
    def read_planilha(self, input_file):
        filename = os.path.join(self.input_dir, input_file)
        logger.info('lendo arquivo %s', filename)
        df = pd.read_excel(filename, verbose=False)
        headers = df.columns.to_list()
        if headers != config.RENAMED_COLUMNS:
            util.report_file_mismatch(logger, headers, config.RENAMED_COLUMNS)
            sys.exit(config.EXIT_FILE_MISMATCH)
        return df
    
    def save_planilhao(self, df):
        logger.info('salvando planilhão')
        df.to_excel(self.output, index=False)
        
    def run(self):
        try:
            logger.info('concat_dedup - versão %d.%d.%d', *self.VERSION)
            if len(self.inputs) < 2:
                logger.error('especificar ao menos 2 arquivos')
                sys.exit(config.EXIT_TOO_FEW_FILES)      
            logger.info('iniciando loop de parsing')
            dfs = []
            for input_file in self.inputs:
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
    parser.add_argument('--output', type=str, help='planilha saida', required=True)
    parser.add_argument('--input_dir', type=str, help='planilha saida', default='.')
    parser.add_argument('input', nargs='+', type=str, help='planilhas a serem consolidadas')
    args = parser.parse_args()
    app = App(args.output, args.input_dir, args.input)
    app.run()