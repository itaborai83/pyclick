import os
import shutil
import argparse
import sys
import pandas as pd
import sqlite3
import logging

import pyclick.models as models
import pyclick.util as util
import pyclick.config as config
import pyclick.n4sap.repo as repo

import pyclick.n4sap.config as n4_config
from pyclick.n4sap.prp import PrpV2 as Prp
from pyclick.n4sap.pro import Pro
from pyclick.n4sap.prc import Prc
from pyclick.n4sap.prs import PrsV2 as Prs
from pyclick.n4sap.ids import IdsV2 as Ids

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('kpis2')
    
class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
    
    def connect_db(self):
        logger.info('connecting to db')
        result_db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        conn = sqlite3.connect(result_db)
        return conn
    
    def load_click(self, r):
        logger.info('loading click data model')
        click = models.Click()
        evts = r.load_events()
        for i, evt in enumerate(evts):
            if (i + 1) % 10000 == 0:
                logger.info("%d events loaded so far", i+1)
            click.update(evt)
        logger.info("%d events loaded in total", len(evts))
        return click, models.Event.to_df(evts)
    
    def load_relatorio_medicao(self, r):
        logger.info('loading relatório medição')
        return r.load_relatorio_medicao()
   
    def open_spreadsheet(self):
        logger.info("opening KPI spreadsheet")
        ks = os.path.join(self.dir_apuracao, "__" + n4_config.KPI_SPREADSHEET)
        if os.path.exists(ks):
            logger.warning("KPI spreadsheet already exists. Deleting it")
            os.unlink(ks)
        return pd.ExcelWriter(ks, datetime_format=None)   
    
    def compute_kpis(self, click, xw):
        logger.info('calculating KPI\'s')
        summary = { 'INDICADOR': [], 'VALOR': [], 'SLA': [], 'OBS': [] }
        prp = Prp()
        pro = Pro()
        prc = Prc()
        prs = Prs()
        ids = Ids()
        
        logger.info('computing PRP')
        prp.evaluate(click)
        prp.update_summary(summary)
        prp_details_df = prp.get_details()
        
        logger.info('computing PRO')
        pro.evaluate(click)
        pro.update_summary(summary)
        pro_details_df = pro.get_details()
        
        logger.info('computing PRC')
        prc.evaluate(click)
        prc.update_summary(summary)
        prc_details_df = prc.get_details()
        
        logger.info('computing PRS')
        prs.evaluate(click)
        prs.update_summary(summary)
        prs_details_df = prs.get_details()
        
        logger.info('computing IDS')
        ids.evaluate(click)
        ids.update_summary(summary)
        ids_details_df = ids.get_details()
        
        logger.info('writing summary table')
        df_summary = pd.DataFrame(summary)
        df_summary.to_excel(xw, sheet_name="INDICADORES", index=False)
        logger.info('writing KPI details')
        prp_details_df.to_excel(xw, sheet_name="PRP_DETALHES", index=False)
        pro_details_df.to_excel(xw, sheet_name="PRO_DETALHES", index=False)
        prc_details_df.to_excel(xw, sheet_name="PRC_DETALHES", index=False)
        prs_details_df.to_excel(xw, sheet_name="PRS_DETALHES", index=False)
        ids_details_df.to_excel(xw, sheet_name="IDS_DETALHES", index=False)

    def write_business_times(self, repo, xw):
        logger.info("exporting tempo útil mesas")
        df = repo.get_business_times()
        df.to_excel(xw, sheet_name="TEMPO_UTIL", index=False)

    def write_pending_times(self, repo, xw):
        logger.info("exporting tempo pendências mesas")
        df = repo.get_pending_times()
        df.to_excel(xw, sheet_name="TEMPO_PENDENTE", index=False)

    def run(self):
        try:
            logger.info('starting geração indicadores - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            r = repo.RepoN4(conn)
            click, events_df = self.load_click(r)
            df_rel_medicao = self.load_relatorio_medicao(r)
            with self.open_spreadsheet() as xw:
                events_df.to_excel(xw, sheet_name="EVENTOS_MEDICAO", index=False)
                self.compute_kpis(click, xw)
                self.write_business_times(r, xw)
                self.write_pending_times(r, xw)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao)
    app.run()
    