import os
import shutil
import argparse
import sys
import pandas as pd
import sqlite3
import logging

import pyclick.util as util
import pyclick.config as config
import pyclick.n4sap.config as n4_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('gerar_indicadores')

SQL_COMPUTE_KPIS = util.get_query("CALCULA_INDICADORES")
SQL_INCIDENTES_ABERTOS_VELHOS = util.get_query("INCIDENTES_ABERTOS_VELHOS")

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao, skip_calc):
        self.dir_apuracao = dir_apuracao
        self.skip_calc = skip_calc
    
    def connect_db(self):
        logger.info('connecting to db')
        result_db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        conn = sqlite3.connect(result_db)
        return conn
        df_slas.to_excel(xw, sheet_name="SLAs", index=False)
        df_actions.to_excel(xw, sheet_name="DADOS", index=False)
    
    def compute_kpis(self, conn):
        logger.info("calculating KPI's")
        conn.executescript(SQL_COMPUTE_KPIS)
        
    def open_spreadsheet(self):
        logger.info("opening KPI spreadsheet")
        ks = os.path.join(self.dir_apuracao, n4_config.KPI_SPREADSHEET)
        if os.path.exists(ks):
            logger.warning("KPI spreadsheet already exists. Deleting it")
            os.unlink(ks)
        return pd.ExcelWriter(ks)
    
    def write_kpi(self, conn, xw):
        logger.info("exporting KPI's")
        sql = "SELECT INDICADOR, VALOR, OBSERVACAO FROM INDICADORES ORDER BY ORDEM"
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="INDICADORES", index=False)

    def write_data(self, conn, xw):
        logger.info("exporting dados medição")
        sql = "SELECT * FROM VW_DADOS_MEDICAO"
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="DADOS_MEDICAO", index=False)

    def write_missing_data(self, conn, xw):
        logger.info("exporting missing data entries")
        sql = "SELECT * FROM VW_DADOS_MEDICAO_FALTANDO"
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="DADOS_MEDICAO_FALTANDO", index=False)

    def write_override_data(self, conn, xw):
        logger.info("exporting override data")
        sql = "SELECT * FROM INCIDENTES_OVERRIDE ORDER BY ID_CHAMADO"
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="OVERRIDE", index=False)

    def write_source_data(self, conn, xw):
        logger.info("exporting source data")
        sql = "SELECT * FROM VW_REL_MEDICAO "
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="REL_MEDICAO", index=False)

    def write_source_prp_details(self, conn, xw):
        logger.info("exporting PRP details")
        sql = "SELECT * FROM VW_KPI_PRP_DETALHES"
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="VW_KPI_PRP_DETALHES", index=False)

    def write_source_pro_details(self, conn, xw):
        logger.info("exporting PRO details")
        sql = "SELECT * FROM VW_KPI_PRO_DETALHES;"
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="VW_KPI_PRO_DETALHES", index=False)

    def write_source_prc_details(self, conn, xw):
        logger.info("exporting PRC details")
        sql = "SELECT * FROM VW_KPI_PRC_DETALHES;"
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="VW_KPI_PRC_DETALHES", index=False)

    def write_source_prs_details(self, conn, xw):
        logger.info("exporting PRS details")
        sql = "SELECT * FROM VW_KPI_PRS_DETALHES;"
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="VW_KPI_PRS_DETALHES", index=False)

    def write_source_cri_details(self, conn, xw):
        logger.info("exporting CRI details")
        sql = "SELECT * FROM VW_KPI_CRI_DETALHES;"
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="VW_KPI_CRI_DETALHES", index=False)

    def write_source_sit_details(self, conn, xw):
        logger.info("exporting SIT details")
        sql = "SELECT * FROM VW_KPI_SIT_DETALHES;"
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="VW_KPI_SIT_DETALHES", index=False)
        
    def vacuum(self, conn):
        logger.info("vacuuming database")
        conn.execute("VACUUM")
        
    def run(self):
        try:
            logger.info('starting geração indicadores - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            if self.skip_calc:
                logger.warning("skipping calculate KPI's due to command line argument")
            else:
                self.compute_kpis(conn)
            with self.open_spreadsheet() as xw:
                self.write_kpi(conn, xw)
                self.write_data(conn, xw)
                self.write_missing_data(conn, xw)
                self.write_override_data(conn, xw)
                self.write_source_data(conn, xw)
                self.write_source_prp_details(conn, xw)
                self.write_source_pro_details(conn, xw)
                self.write_source_prc_details(conn, xw)
                self.write_source_prs_details(conn, xw)
                self.write_source_cri_details(conn, xw)
                self.write_source_sit_details(conn, xw)
                self.vacuum(conn)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--skipcalc', action="store_true", default=False, help='pula cálculo de indicadores')
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.skipcalc)
    app.run()
    