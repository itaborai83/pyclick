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
import pyclick.kpis as kpis

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('kpis2')


class N4Handler(kpis.Handler):
    
    MESAS = [
        'N4-SAP-SUSTENTACAO-ABAST_GE', 
        'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 
        'N4-SAP-SUSTENTACAO-CORPORATIVO', 
        'N4-SAP-SUSTENTACAO-FINANCAS', 
        'N4-SAP-SUSTENTACAO-GRC', 
        'N4-SAP-SUSTENTACAO-PORTAL', 
        'N4-SAP-SUSTENTACAO-SERVICOS', 
        'N4-SAP-SUSTENTACAO-ESCALADOS', 
        'N4-SAP-SUSTENTACAO-PRIORIDADE'
    ]
    
class PrpHandler(N4Handler):

    class PrpEvent(object):
        
        PRAZO_PRP = 9 * 60
        
        def __init__(self, row):
            self.id_chamado     = row.ID_CHAMADO
            self.chamado_pai    = row.CHAMADO_PAI
            self.start_dt       = row.DATA_INICIO_ACAO
            self.end_dt         = row.DATA_INICIO_ACAO
            self.status         = None
            self.duracao        = 0
        
        def update(self, row):
            self.end_dt = row.DATA_INICIO_ACAO
            self.duracao += (0 if row.PENDENCIA == 'S' else row.DURACAO_M)
            self.status = row.ULTIMA_ACAO_NOME
            
    def __init__(self):
        self.watch_list = {}
        self.entries = []
    
    def begin(self):
        pass
    
    def new_day(self, date):
        pass
        
    def begin_event(self, id_chamado):
        pass
        
    def process_action(self, row):
        if row.MESA_ATUAL == 'N4-SAP-SUSTENTACAO-PRIORIDADE' and row.ID_CHAMADO not in self.watch_list:
            evt = self.PrpEvent(row)
            self.watch_list[ row.ID_CHAMADO ] = evt
        
        if row.ID_CHAMADO not in self.watch_list:
            return
        
        evt = self.watch_list[ row.ID_CHAMADO ]
        if row.MESA_ATUAL == 'N4-SAP-SUSTENTACAO-PRIORIDADE':
            evt.update(row)
        
        elif row.MESA_ATUAL != 'N4-SAP-SUSTENTACAO-PRIORIDADE':
            del self.watch_list[ row.ID_CHAMADO ]
            self.entries.append(evt)
            
    def end_event(self, id_chamado):
        if id_chamado in self.watch_list:
            evt = self.watch_list[ id_chamado ]
            del self.watch_list[ id_chamado ]
            self.entries.append(evt)
        
    def end(self):
        pass
        
    def compute_kpi(self):
        df = self.get_kpi_entries()
        if len(df) == 0:
            return 0.0
        kpi = sum([ 1.0 if e.duracao > self.PRAZO_PRP else 0.0 ]) / len(df)
        return kpi * 100.0
    
    def get_kpi_details(self):
        df = pd.DataFrame({
            'id_chamado'    : [ e.id_chamado                    for e in self.entries ],
            'chamado_pai'   : [ e.chamado_pai                   for e in self.entries ],
            'data_inicio'   : [ util.parse_datetime(e.start_dt) for e in self.entries ],
            'data_fime'     : [ util.parse_datetime(e.end_dt)   for e in self.entries ],
            'status'        : [ e.status                        for e in self.entries ],
            'duracao'       : [ e.duracao                       for e in self.entries ]
        })
        return df

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
    
    def connect_db(self):
        logger.info('connecting to db')
        result_db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        conn = sqlite3.connect(result_db)
        return conn
    
    def get_actions(self, conn):
        logger.info('retrieving actions')
        sql = "SELECT * FROM VW_REL_MEDICAO ORDER BY DATA_INICIO_ACAO, ID_CHAMADO, ID_ACAO"
        df = pd.read_sql(sql, conn)
        return df
       
    def compute_kpis(self, conn, df, xw):
        logger.info('calculating KPI\'s')
        f = None #lambda row: row.ID_CHAMADO == '400982'
        kpi_runner = kpis.Runner(f)
        prp_handler = PrpHandler()
        kpi_runner.add_handler(prp_handler)
        kpi_runner.run(df)
        prp_handler.write_details('PRP_DETALHES', xw)
        
    def open_spreadsheet(self):
        logger.info("opening KPI spreadsheet")
        ks = os.path.join(self.dir_apuracao, "__" + n4_config.KPI_SPREADSHEET)
        if os.path.exists(ks):
            logger.warning("KPI spreadsheet already exists. Deleting it")
            os.unlink(ks)
        return pd.ExcelWriter(ks, datetime_format=None)
        
    """
    def write_kpi(self, conn, xw):
        logger.info("exporting KPI's")
        sql = "SELECT INDICADOR, VALOR, OBSERVACAO FROM INDICADORES ORDER BY ORDEM"
        df = pd.read_sql(sql, conn)
        df.to_excel(xw, sheet_name="INDICADORES", index=False)
    """ 
    
    def run(self):
        try:
            logger.info('starting geração indicadores - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            df = self.get_actions(conn)
            with self.open_spreadsheet() as xw:
                self.compute_kpis(conn, df, xw)
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
    