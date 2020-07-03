# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import argparse
import logging
import glob
import re
import datetime as dt
import sqlite3
import pyclick.util as util
import pyclick.config as config
import pyclick.n4sap.config as n4_config
import runn4 as runn4

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('runmwn4')

class App(object):
    
    VERSION = (0, 0, 0)
    DIR_IMPORT_V2 = "DADOS/IMPORTv2"
    
    def __init__(self, dir_apuracao, begin_date, end_date, delta_days, output_tsv, truncate):
        assert begin_date <= end_date
        assert delta_days > 1
        assert output_tsv.endswith(".tsv")
        self.dir_apuracao = dir_apuracao
        self.begin_date = begin_date
        self.end_date = end_date
        self.delta_days = delta_days
        self.output_tsv = output_tsv
        self.truncate = truncate
    
    def get_dates(self):
        logger.info('listing dates')
        assert self.begin_date <= self.end_date
        result = []
        date = self.begin_date
        while date <= self.end_date:
            result.append(date)
            date = util.next_date(date)
        return result
    
    def min_import_date(self):
        logger.info('discovering min import date')
        path = os.path.join(self.DIR_IMPORT_V2, "*CLOSED.db.gz")
        date_regex = re.compile(r'(\d{4}-\d{2}-\d{2})-CLOSED.db.gz')
        files = sorted(glob.glob(path))
        min_import_file = files[ 0 ]
        match = date_regex.search(min_import_file)
        min_import_date = match[ 1 ]
        logger.info(f"min import date is {min_import_date}")
        return min_import_date

    def connect_db(self):
        logger.info('connecting to db')
        result_db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        conn = sqlite3.connect(result_db)
        return conn
    
    def report_kpis_headers(self, fh):
        print('DATA', 'PRP', 'PRO', 'PRC', 'PRS', 'IDS', 'CSAT', 'CSAT - Período', 'ESTOQUE', 'PESO30', 'PEND.FECH.', 'INICIO_APURACAO','FIM_APURACAO'
        , sep='\t'
        , file=fh
        )
    
    def report_kpis(self, conn, fh):
        PRP = conn.execute("SELECT VALOR FROM INDICADORES WHERE INDICADOR = 'PRP'").fetchone()[ 0 ]
        PRO = conn.execute("SELECT VALOR FROM INDICADORES WHERE INDICADOR = 'PRO'").fetchone()[ 0 ]
        PRC = conn.execute("SELECT VALOR FROM INDICADORES WHERE INDICADOR = 'PRC'").fetchone()[ 0 ]
        PRS = conn.execute("SELECT VALOR FROM INDICADORES WHERE INDICADOR = 'PRS'").fetchone()[ 0 ]
        IDS = conn.execute("SELECT VALOR FROM INDICADORES WHERE INDICADOR = 'IDS'").fetchone()[ 0 ]
        CSAT = conn.execute("SELECT VALOR FROM INDICADORES WHERE INDICADOR = 'CSAT'").fetchone()[ 0 ]
        CSAT_PERIODO = conn.execute("SELECT VALOR FROM INDICADORES WHERE INDICADOR = 'CSAT - Período'").fetchone()[ 0 ]
        ESTOQUE = conn.execute("SELECT VALOR FROM INDICADORES WHERE INDICADOR = 'ESTOQUE'").fetchone()[ 0 ]
        PESO30 = conn.execute("SELECT VALOR FROM INDICADORES WHERE INDICADOR = 'PESO30'").fetchone()[ 0 ]
        PEND_FECH = conn.execute("SELECT VALOR FROM INDICADORES WHERE INDICADOR = 'PEND.FECH.'").fetchone()[ 0 ]
        INICIO_APURACAO = conn.execute("SELECT VALOR FROM PARAMS WHERE PARAM = 'HORA_INICIO_APURACAO'").fetchone()[ 0 ]
        FIM_APURACAO = conn.execute("SELECT VALOR FROM PARAMS WHERE PARAM = 'HORA_FIM_APURACAO'").fetchone()[ 0 ]
        
        f = lambda x: str(x).replace('.', ',')
        print(  f(PRP)
        ,       f(PRO)
        ,       f(PRC)
        ,       f(PRS)
        ,       f(IDS)
        ,       f(CSAT)
        ,       f(CSAT_PERIODO)
        ,       f(ESTOQUE)
        ,       f(PESO30)
        ,       f(PEND_FECH)
        ,       f(CSAT)
        ,       f(INICIO_APURACAO)
        ,       f(FIM_APURACAO)
        ,       sep='\t'
        ,       file=fh
        )
        
    def run(self):
        try:
            logger.info('runmwn4 - versão %d.%d.%d', *self.VERSION)
            dates = self.get_dates()
            min_import_date = self.min_import_date()
            if self.truncate:
                logger.warning(f"truncating output file {self.output_tsv}")
                open(self.output_tsv, "w").close()
            with open(self.output_tsv, "a") as fh:
                self.report_kpis_headers(fh)
                for date in dates:
                    begin_date = util.prior_n_days(date, self.delta_days)
                    begin_date = min_import_date if begin_date < min_import_date else begin_date
                    end_date = date
                    logger.info(f"processing from {begin_date} to {end_date}")
                    app = runn4.App(self.dir_apuracao, begin_date, end_date)
                    app.run()
                    conn = self.connect_db()
                    self.report_kpis(conn, fh)
                    conn.close()
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--truncate', action="store_true", default=False, help='truncate output file')
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    parser.add_argument('begin_date', type=str, help='begin date')
    parser.add_argument('end_date', type=str, help='end date')
    parser.add_argument('delta_days', type=int, help='delta days')
    parser.add_argument('output_tsv', type=str, help='tsv output file')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.begin_date, args.end_date, args.delta_days, args.output_tsv, args.truncate)
    app.run()