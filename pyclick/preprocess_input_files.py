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
import shutil
import pyclick.util as util
import pyclick.config as config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('preprocess_input_files')

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao  = dir_apuracao        
        
    def read_planilhas(self):
        logger.info('listando arquivos de entrada')
        currdir = os.getcwd()
        path = util.get_input_dir(self.dir_apuracao)
        try:
            os.chdir(path)
            arquivos = list(sorted(glob.iglob("*.csv")))
            return arquivos
        finally:
            os.chdir(currdir)
    
    def handle_filename(self, filename):
        orig_filename = filename
        filename = filename[ len(config.INPUT_FILENAME_PREFIX) : ]
        day, month, year_ext = filename.split("-")
        year, ext = year_ext.split(".")
        assert ext == "csv"
        new_name = year + "-" + month + "-" + day + "." + ext
        shutil.move(orig_filename, new_name)
        return new_name
        
    def process_input_file(self, filename):
        logger.info('processando arquivo %s', filename)
        currdir = os.getcwd()
        path = util.get_input_dir(self.dir_apuracao)
        try:
            os.chdir(path)
            if filename.startswith(config.INPUT_FILENAME_PREFIX):
                filename = self.handle_filename(filename)
            with open(filename, encoding="latin-1") as fh:
                line = fh.readline()
                if not line.startswith(config.SEPARATOR_HEADER):
                    return
                logger.info('removing separator header')
                filename_tmp = filename + ".tmp"
                with open(filename_tmp, "w", encoding="latin-1") as fh2:
                    for line in fh:
                        fh2.write(line)
            shutil.move(filename_tmp, filename)
        finally:
            os.chdir(currdir)
            
    def run(self):
        try:
            logger.info('Pré-processamento dos arquivos de entrada - versão %d.%d.%d', *self.VERSION)
            arq_planilhas = self.read_planilhas()
            for arq_planilha in arq_planilhas:
                self.process_input_file(arq_planilha)
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao)
    app.run()