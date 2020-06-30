# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os.path
import shutil
import re
import argparse
import logging
import datetime as dt

import pyclick.util as util
import pyclick.config as config
import pyclick.n4sap.config as n4_config

import pyclick.assyst.dump_multi_days as dump_multi_days
import pyclick.import_planilhao as import_planilhao

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('loader')

class App(object):
    
    VERSION = (0, 0, 0)
    
    PARALLEL_QUERIES = 4
    def __init__(self, first, clear_work, clear_existing, dir_work, dir_staging, dir_import, begin_date, end_date):
        self.first          = first
        self.clear_work     = clear_work
        self.clear_existing = clear_existing
        self.dir_work       = dir_work
        self.dir_staging    = dir_staging
        self.dir_import     = dir_import
        self.begin_date     = begin_date
        self.end_date       = end_date
    
    def get_dates(self):
        logger.info('listing dates')
        assert self.begin_date <= self.end_date
        result = []
        date = self.begin_date
        while date <= self.end_date:
            result.append(date)
            date = util.next_date(date)
        return result
    
    def get_dir_files(self, dir, filter=None):
        files = []
        for file in os.listdir(dir):
            path = os.path.join(dir, file)
            if filter and not filter(path):
                continue
            if os.path.isfile(path):
                files.append(path)
        return sorted(files)
        
    def check_work_dir(self):
        logger.info('checking work directory before processing')
        files = self.get_dir_files(self.dir_work)
        if len(files) == 0:
            return
        if not self.clear_work:
            logger.error('work dir has already files in it. Please use an empty directory or use --clear-work)')
            sys.exit(1)
        for f in files:
            logger.warning(f'deleting file {f}')
            os.unlink(f)
    
    def check_staging_dir(self, dates):
        logger.info('checking staging directory before processing')
        date_regex = re.compile(r'\d{4}-\d{2}-\d{2}[.]csv([.]gz)?')
        files = self.get_dir_files(self.dir_staging)
        if len(files) == 0:
            return
        to_delete = []
        for f in files:
            if match := date_regex.search(f):
                file_date = match[ 0 ]
                if file_date in dates:
                    to_delete.append(f)
        if len(to_delete) == 0:
            return
        if not self.clear_existing:
            logger.error('staging dir already has some of the dates to be processed')
            logger.error('please use --clear-existing to delete them')
            sys.exit(1)
        for f in to_delete:
            logger.warning(f'deleting file {f}')
            os.unlink(f)
    
    def check_import_dir(self, dates):
        logger.info('checking import directory before processing')
        date_regex = re.compile(r'\d{4}-\d{2}-\d{2}-(CLOSED|OPEN)[.]db([.]gz)?')
        min_date = min(dates)
        files = self.get_dir_files(self.dir_import)
        to_delete = []
        for f in files:
            if match := date_regex.search(f):
                file_date = match[ 0 ]
                if file_date >= min_date:
                    to_delete.append(f)
        if len(to_delete) == 0:
            return
        if not self.clear_existing:
            logger.error('import dir already has later dates processed')
            logger.error('please use --clear-existing to delete them')
            sys.exit(1)
        for f in to_delete:
            logger.warning(f'deleting file {f}')
            os.unlink(f)            
    
    def create_planilhoes(self, dates):
        logger.info("creating planilhoes on work dir")
        app = dump_multi_days.App(
            dir_staging = self.dir_work,
            begin_date = min(dates),
            end_date = max(dates),
            compress = True,
            parallel = self.PARALLEL_QUERIES
        )
        app.run()
    
    def move_planilhoes_to_staging(self):
        logger.info("moving planilhoes from work to staging directory")
        filter = lambda x: x.endswith(".csv.gz")
        src_files = self.get_dir_files(self.dir_work, filter)
        dst_dir = os.path.join(self.dir_staging, ".") # slashdot
        for file in src_files:
            logger.info(f"moving file {file} from work dir to staging")
            shutil.copy2(file, dst_dir)
            os.unlink(file)
        # remove .out files
        filter = lambda x: x.endswith(".out")
        dotout_files = self.get_dir_files(self.dir_work, filter)
        for file in dotout_files:
            logger.info(f"deleting file {file}")
            os.unlink(file)
    
    def import_planilhoes(self, dates):
        logger.info("import planilhoes from staging directory")
        for i, date in enumerate(dates):
            logger.info(f"importing date {date}")
            planilhao_compressed = os.path.join(self.dir_staging, f"{date}.csv.gz")
            planilhao = os.path.join(self.dir_staging, f"{date}.csv")
            util.decompress_to(planilhao_compressed, planilhao)
            if i == 0 and self.first:
                app = import_planilhao.App(open_acc=None, staging_file=planilhao, import_dir = self.dir_import, latin1=False) # TODO: fix naming inconsistency
            else:
                prior_date = util.prior_date(date)
                open_acc = os.path.join(self.dir_import, f"{prior_date}-OPEN.db.gz")
                app = import_planilhao.App(open_acc=open_acc, staging_file=planilhao, import_dir=self.dir_import, latin1=False) # TODO: fix naming inconsistency
            app.run()
            os.unlink(planilhao)
    
    def run(self):
        try:
            logger.info('loader - versão %d.%d.%d', *self.VERSION)
            dates = self.get_dates()
            self.check_work_dir()
            self.check_staging_dir(dates)
            self.check_import_dir(dates)
            self.create_planilhoes(dates)
            self.move_planilhoes_to_staging()
            self.import_planilhoes(dates)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--first', action='store_true', default=False, help='start é o primeiro dia')
    parser.add_argument('--clear-work', action='store_true', default=False, help='limpa diretório de trabalho')
    parser.add_argument('--clear-existing', action='store_true', default=False, help='limpa arquivos pré-existentes de staging e importação da carga solicitada')
    parser.add_argument('dir_work', type=str, help='diretório download')
    parser.add_argument('dir_staging', type=str, help='diretório staging')
    parser.add_argument('dir_import', type=str, help='diretório importação')
    parser.add_argument('begin_date', type=str, help='data início carga')
    parser.add_argument('end_date', type=str, help='data fim carga')
    args = parser.parse_args()
    app = App(
        args.first, 
        args.clear_work, 
        args.clear_existing,
        args.dir_work, 
        args.dir_staging, 
        args.dir_import, 
        args.begin_date, 
        args.end_date
    )
    app.run()