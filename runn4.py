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
import pyclick.consolida_planilhao as consolida_planilhao 
import pyclick.n4sap.ddl as ddl
import pyclick.n4sap.kpis2 as kpis

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('runn4')


DIR_IMPORT_V1 = "DADOS/IMPORT"
DIR_IMPORT_V2 = "DADOS/IMPORTv2"
VIEW_MEDICOES = "VW_REL_MEDICAO"

class App(object):
    
    VERSION = (0, 0, 0)
        
    def __init__(self, dir_apuracao, start, end, v1=False, strict_orientar=False):
        self.dir_apuracao = dir_apuracao
        self.start = start
        self.end = end
        self.dir_import = (DIR_IMPORT_V1 if v1 else DIR_IMPORT_V2)
        self.strict_orientar = strict_orientar
    
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
            dump_surveys.App(self.dir_apuracao, n4_config.START_CSAT_DT, self.end).run()
            consolida_planilhao.App(self.dir_apuracao, self.dir_import, self.start, self.end, False).run()
            ddl.App(self.dir_apuracao).run()
            kpis.App(self.dir_apuracao, strict_orientar=self.strict_orientar).run()
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--v1', action='store_true', default=False, help='usar diretório de importatação antigo')
    parser.add_argument('--strict-orientar', action='store_true', help='categorização estrita de orientar')
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    parser.add_argument('start', type=str, help='start date')
    parser.add_argument('end', type=str, help='end date')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.start, args.end, args.v1, args.strict_orientar)
    app.run()