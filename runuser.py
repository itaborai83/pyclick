# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os.path
import argparse
import logging
import datetime as dt

import pyclick.util as util
import pyclick.config as config

import pyclick.assyst.dump_schedules as dump_schedules
import pyclick.assyst.dump_slas as dump_slas
import pyclick.assyst.dump_surveys as dump_surveys
import pyclick.consolida_planilhao as consolida_planilhao 
import pyclick.tools.db2excel as db2excel

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('runuser')

DIR_WORK        = r"DADOS\WORK2"
DIR_IMPORT      = r"DADOS\IMPORT"
VIEW_MEDICOES   = "VW_REL_MEDICAO"

class App(object):
    
    VERSION = (1, 0, 0)
        
    def __init__(self, dir_apuracao, start, end):
        self.dir_apuracao = dir_apuracao
        self.start = start
        self.end = end
        self.dir_import = DIR_IMPORT
        self.dir_work = DIR_WORK

    def has_schedules(self):
        path = os.path.join(self.dir_apuracao, config.BUSINESS_HOURS_SPREADSHEET)
        return os.path.exists(path)
    
    def has_slas(self):
        path = os.path.join(self.dir_apuracao, config.OFFERINGS_SPREADSHEET)
        return os.path.exists(path)    
        
    def run(self):
        try:
            logger.info('excel2db - versão %d.%d.%d', *self.VERSION)

            if not self.has_schedules():
                dump_schedules.App(self.dir_apuracao).run()
            else:
                logger.info('skiping schedules dump. It already exists. Delete it necessary')
            if not self.has_slas():
                dump_slas.App(self.dir_apuracao).run()
            else:
                logger.info('skiping service offerings dump. It already exists. Delete it necessary')
            dump_surveys.App(self.dir_apuracao, self.start, self.end).run()
            consolida_planilhao.App(self.dir_work, self.dir_apuracao, self.dir_import, self.start, self.end, datafix=False, parallel=True).run()
            db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
            excel = os.path.join(self.dir_apuracao, "export_{}-{}.xlsx".format(self.start, self.end))
            db2excel.App(db, VIEW_MEDICOES, excel, "PyClick", overwrite=True).run()
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    parser.add_argument('start', type=str, help='start date')
    parser.add_argument('end', type=str, help='end date')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.start, args.end)
    app.run()