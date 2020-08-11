# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import argparse
import logging
import datetime as dt

import pyclick.util as util
import pyclick.config as config
import pyclick.n4sap.config as n4_config

import pyclick.assyst.dump_schedules as dump_schedules
import pyclick.assyst.dump_slas as dump_slas
import pyclick.assyst.dump_surveys as dump_surveys
import pyclick.consolida_planilhaoV2 as consolida_planilhaoV2 
#import pyclick.n4sap.ddl as ddl # TODO: remove me
import pyclick.n4sap.kpis2 as kpis

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('runn4')

DIR_WORK = "DADOS/WORK"
DIR_IMPORT = "DADOS/IMPORTv3"
VIEW_MEDICOES = "VW_REL_MEDICAO"

class App(object):
    
    VERSION = (0, 0, 0)
        
    def __init__(self, dir_apuracao, start, end):
        self.dir_apuracao = dir_apuracao
        self.start = start
        self.end = end
        self.dir_import = DIR_IMPORT
    
    def has_schedules(self):
        path = os.path.join(self.dir_apuracao, config.BUSINESS_HOURS_SPREADSHEET)
        return os.path.exists(path)
    
    def has_slas(self):
        path = os.path.join(self.dir_apuracao, config.OFFERINGS_SPREADSHEET)
        return os.path.exists(path)    
    
    def run(self):
        try:
            logger.info('runn4 - versão %d.%d.%d', *self.VERSION)
            if not self.has_schedules():
                dump_schedules.App(self.dir_apuracao).run()
            else:
                logger.info('skiping schedules dump. It already exists. Delete it if necessary')
            if not self.has_slas():
                dump_slas.App(self.dir_apuracao).run()
            else:
                logger.info('skiping service offerings dump. It already exists. Delete it if necessary')
            dump_surveys.App(self.dir_apuracao, n4_config.START_CSAT_DT, self.end, delspotfire=True).run()
            consolida_planilhaoV2.App(DIR_WORK, self.dir_apuracao, self.dir_import, self.start, self.end, False, True).run()
            # ddl.App(self.dir_apuracao).run() # TODO: remove me
            kpis.App(self.dir_apuracao, strict_orientar=False).run()
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