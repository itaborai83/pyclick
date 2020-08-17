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
import pyclick.n4sap.models as n4_models
from pyclick.n4sap.prp import PrpV2 as Prp
from pyclick.n4sap.pro import Pro
from pyclick.n4sap.prc import Prc
from pyclick.n4sap.prs import Prs
from pyclick.n4sap.ids import Ids
from pyclick.n4sap.csat import Csat, CsatPeriodo
from pyclick.n4sap.status import Estoque, Encerrados, Cancelados
from pyclick.n4sap.peso30 import Peso30
from pyclick.n4sap.aging import Aging


assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('kpis')

SQL_PROCESSA_CONSOLIDADO = SQL_PROCESSA_CONSOLIDADO = util.get_query("PROCESSA_CONSOLIDADO")

class App(object):
    
    VERSION = (1, 0, 0)

    MESAS  = {
        'N4-SAP-SUSTENTACAO-ESCALADOS'      : 'PESO30'
    ,   'N4-SAP-SUSTENTACAO-ABAST_GE'       : 'ABGE'
    ,   'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' : 'PRAPO'
    ,   'N4-SAP-SUSTENTACAO-CORPORATIVO'    : 'CORP'
    ,   'N4-SAP-SUSTENTACAO-FINANCAS'       : 'FIN'
    ,   'N4-SAP-SUSTENTACAO-GRC'            : 'GRC'
    ,   'N4-SAP-SUSTENTACAO-PORTAL'         : 'PORTAL'
    ,   'N4-SAP-SUSTENTACAO-SERVICOS'       : 'SERV'
    }

    MESAS_COM_PESO35  = {
        'N4-SAP-SUSTENTACAO-PRIORIDADE'     : 'PESO35'
    ,   'N4-SAP-SUSTENTACAO-ESCALADOS'      : 'PESO30'
    ,   'N4-SAP-SUSTENTACAO-ABAST_GE'       : 'ABGE'
    ,   'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' : 'PRAPO'
    ,   'N4-SAP-SUSTENTACAO-CORPORATIVO'    : 'CORP'
    ,   'N4-SAP-SUSTENTACAO-FINANCAS'       : 'FIN'
    ,   'N4-SAP-SUSTENTACAO-GRC'            : 'GRC'
    ,   'N4-SAP-SUSTENTACAO-PORTAL'         : 'PORTAL'
    ,   'N4-SAP-SUSTENTACAO-SERVICOS'       : 'SERV'
    }

    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
        self.strict_orientar = False
    
    def connect_db(self):
        logger.info('connecting to db')
        result_db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        conn = sqlite3.connect(result_db)
        return conn
    
    def run_ddl(self, conn):
        logger.info('running DDL script if necessary')
        conn.executescript(SQL_PROCESSA_CONSOLIDADO)
    
    def load_click(self, r):
        logger.info('loading click data model')
        
        evts = r.load_events()
        start_dt, end_dt = r.get_period()
        
        incsrv = n4_models.IncidentService()
        self.process_expurgos(incsrv)
        self.process_recategorizacoes(incsrv)
        self.process_ofertas(r, incsrv)

        click = n4_models.ClickN4(incsrv=incsrv, strict_orientar=self.strict_orientar)
        
        for i, evt in enumerate(evts):
            if (i + 1) % 10000 == 0:
                logger.info("%d events loaded so far", i+1)
            click.update(evt)
        logger.info("%d events loaded in total", len(evts))
        pesquisas_df = r.get_surveys()
        pesquisas = models.Pesquisa.from_df(pesquisas_df)
        for pesq in pesquisas:
            click.add_pesquisa(pesq)
        evts_df = models.Event.to_df(evts)
        return incsrv, click, evts_df, start_dt, end_dt
    
    def process_expurgos(self, incsrv):
        logger.info('processing expurgos')
        expurgos = util.read_expurgos(self.dir_apuracao)
        for id_chamado in expurgos:
            incsrv.add_expurgo(id_chamado)

    def process_recategorizacoes(self, incsrv):
        logger.info('processing recategorization')
        categorias = util.read_categorias(self.dir_apuracao)
        for id_chamado, categoria in sorted(categorias.items()):
            logger.info("recategorizing incident %s as %s", id_chamado, categoria)
            incsrv.set_override_categoria(id_chamado, categoria)
    
    def process_ofertas(self, r, incsrv):
        logger.info('processing offering switching')
        # list of all offering saved within table OFERTAS
        for row in r.read_ofertas().itertuples():
            incsrv.add_oferta_catalogo(row.oferta, row.prazo)
        # list of offering overrides within dir_apuracao
        ofertas = util.read_ofertas(self.dir_apuracao)
        for id_chamado, oferta in sorted(ofertas.items()):
            logger.info("switching offering incident %s to %s", id_chamado, oferta)
            incsrv.set_override_oferta(id_chamado, oferta)

    
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

    def compute_prp(self, conn, click, xw, start_dt, end_dt, incsrv, summary):
        logger.info('computing PRP')
        prp = Prp(incsrv)
        prp.evaluate(click, start_dt, end_dt)
        prp.update_summary(summary)
        prp_details_df = prp.get_details()
                
        logger.info('writing KPI details')
        prp_details_df.to_excel(xw, sheet_name="PRP", index=False)
        prp_details_df.to_sql("PRP", conn, if_exists="replace", index=False)

    def compute_peso30(self, conn, click, xw, start_dt, end_dt, incsrv, summary):
        logger.info('computing PESO30')
        peso30 = Peso30(incsrv)
        peso30.evaluate(click, start_dt, end_dt)
        peso30.update_summary(summary)
        peso30_df = peso30.get_details()
        peso30_df.to_excel(xw, sheet_name="PESO30", index=False)
        peso30_df.to_sql("PESO30", conn, if_exists="replace", index=False)
            
    def compute_pro(self, conn, click, xw, start_dt, end_dt, incsrv, summary):
        logger.info('computing PRO')
        pro = Pro(incsrv)
        pro.evaluate(click, start_dt, end_dt)
        pro.update_summary(summary)
        pro_details_df = pro.get_details()
        pro_details_df.to_excel(xw, sheet_name="PRO", index=False)
        pro_details_df.to_sql("PRO", conn, if_exists="replace", index=False)
        
        for mesa, sigla in self.MESAS.items():
            pro.reset()
            pro.evaluate(click, start_dt, end_dt, mesa)
            pro.update_summary(summary, sigla)

    def compute_prc(self, conn, click, xw, start_dt, end_dt, incsrv, summary):
        logger.info('computing PRC')
        prc = Prc(incsrv)
        prc.evaluate(click, start_dt, end_dt)
        prc.update_summary(summary)
        prc_details_df = prc.get_details()
        prc_details_df.to_excel(xw, sheet_name="PRC", index=False)
        prc_details_df.to_sql("PRC", conn, if_exists="replace", index=False)

        for mesa, sigla in self.MESAS.items():
            prc.reset()
            prc.evaluate(click, start_dt, end_dt, mesa)
            prc.update_summary(summary, sigla)
            
    def compute_prs(self, conn, click, xw, start_dt, end_dt, incsrv, summary):
        logger.info('computing PRS')
        prs = Prs(incsrv)
        prs.evaluate(click, start_dt, end_dt)
        prs.update_summary(summary)
        prs_details_df = prs.get_details()
        prs_details_df.to_excel(xw, sheet_name="PRS", index=False)
        prs_details_df.to_sql("PRS", conn, if_exists="replace", index=False)
        
        for mesa, sigla in self.MESAS.items():
            prs.reset()
            prs.evaluate(click, start_dt, end_dt, mesa)
            prs.update_summary(summary, sigla)
            
    def compute_ids(self, conn, click, xw, start_dt, end_dt, incsrv, summary):
        logger.info('computing IDS')
        ids = Ids(incsrv)
        ids.evaluate(click, start_dt, end_dt)
        ids.update_summary(summary)
        ids_details_df = ids.get_details()
        ids_details_df.to_excel(xw, sheet_name="IDS", index=False)
        ids_details_df.to_sql("IDS", conn, if_exists="replace", index=False)

        for mesa, sigla in self.MESAS_COM_PESO35.items():
            ids.reset()
            ids.evaluate(click, start_dt, end_dt, mesa)
            ids.update_summary(summary, sigla)
            
    def compute_aging(self, conn, click, xw, start_dt, end_dt, incsrv, summary):
        logger.info('computing AGING')
        aging60 = Aging(incsrv, 60, 90)
        aging90 = Aging(incsrv, 90, 9999999)
                
        aging60.evaluate(click, start_dt, end_dt)
        aging60.update_summary(summary)
        aging60_details_df = aging60.get_details()
        aging60_details_df.to_excel(xw, sheet_name="AGING60", index=False)
        aging60_details_df.to_sql("AGING60", conn, if_exists="replace", index=False)

        for mesa, sigla in self.MESAS_COM_PESO35.items():
            aging60.reset()
            aging60.evaluate(click, start_dt, end_dt, mesa)
            aging60.update_summary(summary, sigla)
        
        aging90.evaluate(click, start_dt, end_dt)
        aging90.update_summary(summary)
        aging90_details_df = aging90.get_details()
        aging90_details_df.to_excel(xw, sheet_name="AGING90", index=False)
        aging90_details_df.to_sql("AGING90", conn, if_exists="replace", index=False)

        for mesa, sigla in self.MESAS_COM_PESO35.items():
            aging90.reset()
            aging90.evaluate(click, start_dt, end_dt, mesa)
            aging90.update_summary(summary, sigla)
        
    def compute_csat(self, conn, click, xw, start_dt, end_dt, incsrv, summary):
        logger.info('computing CSAT')
        
        csat = Csat(incsrv)
        csat.evaluate(click, start_dt, end_dt)
        csat.update_summary(summary)
        csat_details_df, csat_tecnicos_det_df = csat.get_details()
        csat_details_df.to_excel(xw, sheet_name="CSAT", index=False)
        csat_details_df.to_sql("CSAT", conn, if_exists="replace", index=False)        
        csat_tecnicos_det_df.to_excel(xw, sheet_name="CSAT_TECNICOS", index=False)
        csat_tecnicos_det_df.to_sql("CSAT_TECNICOS", conn, if_exists="replace", index=False)

        for mesa, sigla in self.MESAS_COM_PESO35.items():
            csat.reset()
            csat.evaluate(click, start_dt, end_dt, mesa)
            csat.update_summary(summary, sigla)
        
        csat_periodo = CsatPeriodo(incsrv)
        csat_periodo.evaluate(click, start_dt, end_dt)
        csat_periodo.update_summary(summary)
        csat_periodo_details_df, csat_periodo_tecnicos_det_df = csat_periodo.get_details()
        csat_periodo_details_df.to_excel(xw, sheet_name="CSAT_PERIODO", index=False)
        csat_periodo_details_df.to_sql("CSAT_PERIODO", conn, if_exists="replace", index=False)        
        csat_periodo_tecnicos_det_df.to_excel(xw, sheet_name="CSAT_PERIODO_TECNICOS", index=False)
        csat_periodo_tecnicos_det_df.to_sql("CSAT_PERIODO_TECNICOS", conn, if_exists="replace", index=False)
        
        for mesa, sigla in self.MESAS_COM_PESO35.items():
            csat_periodo.reset()
            csat_periodo.evaluate(click, start_dt, end_dt, mesa)
            csat_periodo.update_summary(summary, sigla)
        
    def compute_estoque(self, conn, click, xw, start_dt, end_dt, incsrv, summary):
        logger.info('computing ESTOQUE')
        estoque = Estoque(incsrv)
        estoque.evaluate(click, start_dt, end_dt)
        estoque.update_summary(summary)
        estoque_details_df = estoque.get_details()
        estoque_details_df.to_excel(xw, sheet_name="ESTOQUE", index=False)
        estoque_details_df.to_sql("ESTOQUE", conn, if_exists="replace", index=False)

        for mesa, sigla in self.MESAS_COM_PESO35.items():
            estoque.reset()
            estoque.evaluate(click, start_dt, end_dt, mesa)
            estoque.update_summary(summary, sigla)

    def compute_encerrados(self, conn, click, xw, start_dt, end_dt, incsrv, summary):
        logger.info('computing ENCERRADOS')
        encerrados = Encerrados(incsrv)
        encerrados.evaluate(click, start_dt, end_dt)
        encerrados.update_summary(summary)
        encerrados_df = encerrados.get_details()
        encerrados_df.to_excel(xw, sheet_name="ENCERRADOS", index=False)
        encerrados_df.to_sql("ENCERRADOS", conn, if_exists="replace", index=False)

        for mesa, sigla in self.MESAS_COM_PESO35.items():
            encerrados.reset()
            encerrados.evaluate(click, start_dt, end_dt, mesa)
            encerrados.update_summary(summary, sigla)

    def compute_cancelados(self, conn, click, xw, start_dt, end_dt, incsrv, summary):
        logger.info('computing CANCELADOS')
        cancelados = Cancelados(incsrv)
        cancelados.evaluate(click, start_dt, end_dt)
        cancelados.update_summary(summary)
        cancelados_df = cancelados.get_details()
        cancelados_df.to_excel(xw, sheet_name="CANCELADOS", index=False)
        cancelados_df.to_sql("CANCELADOS", conn, if_exists="replace", index=False)

        for mesa, sigla in self.MESAS_COM_PESO35.items():
            cancelados.reset()
            cancelados.evaluate(click, start_dt, end_dt, mesa)
            cancelados.update_summary(summary, sigla)
            
    def compute_kpis(self, conn, click, xw, start_dt, end_dt, incsrv):
        logger.info('calculating KPI\'s')
        summary = { 
            'INDICADOR' : [], 
            'MESA'      : [],
            'VALOR'     : [], 
            'SLA'       : [], 
            'OBS'       : [] 
        }
        self.compute_prp(conn, click, xw, start_dt, end_dt, incsrv, summary)
        self.compute_peso30(conn, click, xw, start_dt, end_dt, incsrv, summary)
        self.compute_pro(conn, click, xw, start_dt, end_dt, incsrv, summary)
        self.compute_prc(conn, click, xw, start_dt, end_dt, incsrv, summary)
        self.compute_prs(conn, click, xw, start_dt, end_dt, incsrv, summary)
        self.compute_ids(conn, click, xw, start_dt, end_dt, incsrv, summary)
        self.compute_aging(conn, click, xw, start_dt, end_dt, incsrv, summary)
        self.compute_csat(conn, click, xw, start_dt, end_dt, incsrv, summary)
        self.compute_estoque(conn, click, xw, start_dt, end_dt, incsrv, summary)
        self.compute_encerrados(conn, click, xw, start_dt, end_dt, incsrv, summary)
        self.compute_cancelados(conn, click, xw, start_dt, end_dt, incsrv, summary)
        
        summary[ 'INDICADOR' ].append('INÍCIO PERÍODO')
        summary[ 'MESA'      ].append("")
        summary[ 'VALOR'     ].append(start_dt)   
        summary[ 'SLA'       ].append("N/A")
        summary[ 'OBS'       ].append("Hora Início do Período de Apuração")
        
        summary[ 'INDICADOR' ].append('FIM PERÍODO')
        summary[ 'MESA'      ].append("")
        summary[ 'VALOR'     ].append(end_dt)   
        summary[ 'SLA'       ].append("N/A")
        summary[ 'OBS'       ].append("Hora Fim do Período de Apuração")

        summary[ 'INDICADOR' ].append('EXPURGOS')
        summary[ 'MESA'      ].append("")
        summary[ 'VALOR'     ].append(len(click.expurgos))   
        summary[ 'SLA'       ].append("N/A")
        summary[ 'OBS'       ].append("Número de expurgos lançados")
        
        logger.info('writing summary table')
        df_summary = pd.DataFrame(summary)
        df_summary.to_excel(xw, sheet_name="INDICADORES", index=False)
        df_summary.to_sql("INDICADORES", conn, if_exists="replace", index=False)
        
    def run(self):
        try:
            logger.info('starting geração indicadores - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            self.run_ddl(conn)
            r = repo.RepoN4(conn)
            incsrv, click, events_df, start_dt, end_dt = self.load_click(r)
            df_rel_medicao = self.load_relatorio_medicao(r)
            with self.open_spreadsheet() as xw:
                self.compute_kpis(conn, click, xw, start_dt, end_dt, incsrv)
                events_df.to_excel(xw, sheet_name="EVENTOS_MEDICAO", index=False)
                incsrv.get_expurgos().to_excel(xw, sheet_name="EXPURGOS", index=False)
                incsrv.get_overrides_categoria().to_excel(xw, sheet_name="CATEGORIAS", index=False)
                incsrv.get_overrides_oferta().to_excel(xw, sheet_name="OFERTAS", index=False)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--strict-orientar', action='store_true', help='categorização estrita de orientar')
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao)
    app.run()
    