# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import argparse
import logging
import datetime as dt
import sqlite3

import pandas as pd

import pyclick.config as config
import pyclick.util as util
import pyclick.models as models
import pyclick.n4sap.repo as repo
import pyclick.n4sap.config as n4_config
import pyclick.n4sap.prp as prp
import pyclick.n4sap.peso30 as peso30
import pyclick.n4sap.pro as pro
import pyclick.n4sap.prc as prc

import firebase_admin
from firebase_admin import credentials, firestore

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('firebase')

class App(object):
    
    VERSION = (0, 0, 0)
    OUTPUT_SPREADSHEET = "export_kpis.xlsx"
    CAMPOS_QUADRO = [
        "PERIODO",
        "PRP", 
        "PESO30", 
        "PRO", 
        "PRO_ABGE", 
        "PRO_PRAPO", 
        "PRO_CORP", 
        "PRO_FIN", 
        "PRO_GRC", 
        "PRO_PORTAL", 
        "PRO_SERV", 
        "PRC", 
        "PRC_ABGE", 
        "PRC_PRAPO", 
        "PRC_CORP", 
        "PRC_FIN", 
        "PRC_GRC", 
        "PRC_PORTAL", 
        "PRC_SERV", 
        "PRS", 
        "PRS_ABGE", 
        "PRS_PRAPO", 
        "PRS_CORP", 
        "PRS_FIN", 
        "PRS_GRC", 
        "PRS_PORTAL", 
        "PRS_SERV", 
        "IDS", 
        "IDS_ABGE", 
        "IDS_PRAPO", 
        "IDS_CORP", 
        "IDS_FIN", 
        "IDS_GRC", 
        "IDS_PORTAL", 
        "IDS_SERV", 
        "AGING60", 
        "AGING60_ABGE", 
        "AGING60_PRAPO", 
        "AGING60_CORP", 
        "AGING60_FIN", 
        "AGING60_GRC", 
        "AGING60_PORTAL", 
        "AGING60_SERV", 
        "AGING90", 
        "AGING90_ABGE", 
        "AGING90_PRAPO", 
        "AGING90_CORP", 
        "AGING90_FIN", 
        "AGING90_GRC", 
        "AGING90_PORTAL", 
        "AGING90_SERV", 
        "CSAT", 
        "CSAT_ABGE", 
        "CSAT_PRAPO", 
        "CSAT_CORP", 
        "CSAT_FIN", 
        "CSAT_GRC", 
        "CSAT_PORTAL", 
        "CSAT_SERV", 
        "CSAT_PERIODO", 
        "CSAT_PERIODO_ABGE", 
        "CSAT_PERIODO_PRAPO", 
        "CSAT_PERIODO_CORP", 
        "CSAT_PERIODO_FIN", 
        "CSAT_PERIODO_GRC", 
        "CSAT_PERIODO_PORTAL", 
        "CSAT_PERIODO_SERV",
        "ESTOQUE",
        "ESTOQUE_ABGE",
        "ESTOQUE_PRAPO",
        "ESTOQUE_CORP",
        "ESTOQUE_FIN",
        "ESTOQUE_GRC",
        "ESTOQUE_PORTAL",
        "ESTOQUE_SERV",
        "ENCERRADOS",
        "ENCERRADOS_ABGE",
        "ENCERRADOS_PRAPO",
        "ENCERRADOS_CORP",
        "ENCERRADOS_FIN",
        "ENCERRADOS_GRC",
        "ENCERRADOS_PORTAL",
        "ENCERRADOS_SERV",
        "CANCELADOS",
        "CANCELADOS_ABGE",
        "CANCELADOS_PRAPO",
        "CANCELADOS_CORP",
        "CANCELADOS_FIN",
        "CANCELADOS_GRC",
        "CANCELADOS_PORTAL",
        "CANCELADOS_SERV",
        #"INICIO_PERIODO",
        #"FIM_PERIODO",
        "EXPURGOS",
    ]
    
    INDICADORES_MESAS = {
        "PERIODO"               : ("PERIODO", None),
        "PRP"                   : ("PRP", None),
        "PESO30"                : ("PESO30", None),
        "PRO"                   : ("PRO", None),
        "PRO_ABGE"              : ("PRO", "ABGE"),
        "PRO_PRAPO"             : ("PRO", "PRAPO"),
        "PRO_CORP"              : ("PRO", "CORP"),
        "PRO_FIN"               : ("PRO", "FIN"),
        "PRO_GRC"               : ("PRO", "GRC"),
        "PRO_PORTAL"            : ("PRO", "PORTAL"),
        "PRO_SERV"              : ("PRO", "SERV"),
        "PRC"                   : ("PRC", None),
        "PRC_ABGE"              : ("PRC", "ABGE"),
        "PRC_PRAPO"             : ("PRC", "PRAPO"),
        "PRC_CORP"              : ("PRC", "CORP"),
        "PRC_FIN"               : ("PRC", "FIN"),
        "PRC_GRC"               : ("PRC", "GRC"),
        "PRC_PORTAL"            : ("PRC", "PORTAL"),
        "PRC_SERV"              : ("PRC", "SERV"),
        "PRS"                   : ("PRS", None),
        "PRS_ABGE"              : ("PRS", "ABGE"),
        "PRS_PRAPO"             : ("PRS", "PRAPO"),
        "PRS_CORP"              : ("PRS", "CORP"),
        "PRS_FIN"               : ("PRS", "FIN"),
        "PRS_GRC"               : ("PRS", "GRC"),
        "PRS_PORTAL"            : ("PRS", "PORTAL"),
        "PRS_SERV"              : ("PRS", "SERV"),
        "IDS"                   : ("IDS", None),
        "IDS_PRAPO"             : ("IDS", "PRAPO"),
        "IDS_ABGE"              : ("IDS", "ABGE"),
        "IDS_CORP"              : ("IDS", "CORP"),
        "IDS_FIN"               : ("IDS", "FIN"),
        "IDS_GRC"               : ("IDS", "GRC"),
        "IDS_PORTAL"            : ("IDS", "PORTAL"),
        "IDS_SERV"              : ("IDS", "SERV"),
        "AGING60"               : ("AGING 60", None),
        "AGING60_ABGE"          : ("AGING 60", "ABGE"),
        "AGING60_PRAPO"         : ("AGING 60", "PRAPO"),
        "AGING60_CORP"          : ("AGING 60", "CORP"),
        "AGING60_FIN"           : ("AGING 60", "FIN"),
        "AGING60_GRC"           : ("AGING 60", "GRC"),
        "AGING60_PORTAL"        : ("AGING 60", "PORTAL"),
        "AGING60_SERV"          : ("AGING 60", "SERV"),
        "AGING90"               : ("AGING 90", None),
        "AGING90_ABGE"          : ("AGING 90", "ABGE"),
        "AGING90_PRAPO"         : ("AGING 90", "PRAPO"),
        "AGING90_CORP"          : ("AGING 90", "CORP"),
        "AGING90_FIN"           : ("AGING 90", "FIN"),
        "AGING90_GRC"           : ("AGING 90", "GRC"),
        "AGING90_PORTAL"        : ("AGING 90", "PORTAL"),
        "AGING90_SERV"          : ("AGING 90", "SERV"),
        "CSAT"                  : ("CSAT", None),
        "CSAT_ABGE"             : ("CSAT", "ABGE"),
        "CSAT_PRAPO"            : ("CSAT", "PRAPO"),
        "CSAT_CORP"             : ("CSAT", "CORP"),
        "CSAT_FIN"              : ("CSAT", "FIN"),
        "CSAT_GRC"              : ("CSAT", "GRC"),
        "CSAT_PORTAL"           : ("CSAT", "PORTAL"),
        "CSAT_SERV"             : ("CSAT", "SERV"),
        "CSAT_PERIODO"          : ("CSAT", None),
        "CSAT_PERIODO_ABGE"     : ("CSAT - Período", "ABGE"),
        "CSAT_PERIODO_PRAPO"    : ("CSAT - Período", "PRAPO"),
        "CSAT_PERIODO_CORP"     : ("CSAT - Período", "CORP"),
        "CSAT_PERIODO_FIN"      : ("CSAT - Período", "FIN"),
        "CSAT_PERIODO_GRC"      : ("CSAT - Período", "GRC"),
        "CSAT_PERIODO_PORTAL"   : ("CSAT - Período", "PORTAL"),
        "CSAT_PERIODO_SERV"     : ("CSAT - Período", "SERV"),
        "ESTOQUE"               : ("ESTOQUE", None),
        "ESTOQUE_ABGE"          : ("ESTOQUE", "ABGE"),
        "ESTOQUE_PRAPO"         : ("ESTOQUE", "PRAPO"),
        "ESTOQUE_CORP"          : ("ESTOQUE", "CORP"),
        "ESTOQUE_FIN"           : ("ESTOQUE", "FIN"),
        "ESTOQUE_GRC"           : ("ESTOQUE", "GRC"),
        "ESTOQUE_PORTAL"        : ("ESTOQUE", "PORTAL"),
        "ESTOQUE_SERV"          : ("ESTOQUE", "SERV"),
        "ENCERRADOS"            : ("ENCERRADOS", None),
        "ENCERRADOS_ABGE"       : ("ENCERRADOS", "ABGE"),
        "ENCERRADOS_PRAPO"      : ("ENCERRADOS", "PRAPO"),
        "ENCERRADOS_CORP"       : ("ENCERRADOS", "CORP"),
        "ENCERRADOS_FIN"        : ("ENCERRADOS", "FIN"),
        "ENCERRADOS_GRC"        : ("ENCERRADOS", "GRC"),
        "ENCERRADOS_PORTAL"     : ("ENCERRADOS", "PORTAL"),
        "ENCERRADOS_SERV"       : ("ENCERRADOS", "SERV"),
        "CANCELADOS"            : ("CANCELADOS", None),
        "CANCELADOS_ABGE"       : ("CANCELADOS", "ABGE"),
        "CANCELADOS_PRAPO"      : ("CANCELADOS", "PRAPO"),
        "CANCELADOS_CORP"       : ("CANCELADOS", "CORP"),
        "CANCELADOS_FIN"        : ("CANCELADOS", "FIN"),
        "CANCELADOS_GRC"        : ("CANCELADOS", "GRC"),
        "CANCELADOS_PORTAL"     : ("CANCELADOS", "PORTAL"),
        "CANCELADOS_SERV"       : ("CANCELADOS", "SERV"),
        #"INICIO_PERIODO"        : ("INÍCIO PERÍODO", None),
        #"FIM_PERIODO"           : ("FIM PERÍODO", None),
        "EXPURGOS"              : ("EXPURGOS", None),
    }
    
    def __init__(self, dir_n4, fb_conf, nocloud):
        self.dir_n4 = dir_n4
        self.fb_conf = fb_conf
        self.nocloud = nocloud
        
    """
    def process_expurgos(self, click):
        logger.info('processing expurgos')
        expurgos = util.read_expurgos(self.dir_apuracao)
        for id_chamado in expurgos:
            click.add_expurgo(id_chamado)
        return expurgos
    
    def load_click(self, r):
        logger.info('loading click data model')
        click = models.Click()
        expurgos = self.process_expurgos(click)
        evts = r.load_events()
        start_dt, end_dt = r.get_period()
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
        expurgos_df = pd.DataFrame({ "expurgo": expurgos })
        return click, evts_df, expurgos_df, start_dt, end_dt
            
    def inc2json(self, inc):
        if inc.categoria.startswith('S'):
            categoria = 'REALIZAR'
        elif inc.categoria.startswith('T'):
            categoria = 'REALIZAR - TAREFA'
        elif 'CORRIGIR' in inc.categoria:
            categoria = 'CORRIGIR'
        else:
            categoria = 'ORIENTAR'
        mesa = inc.mesa_atual
        status = inc.status
        
        if mesa == 'N4-SAP-SUSTENTACAO-PRIORIDADE':
            duracao_m   = inc.calc_duration_mesas( [ 'N4-SAP-SUSTENTACAO-PRIORIDADE' ] )
            pendencia_m = inc.calc_pendencia_mesas( [ 'N4-SAP-SUSTENTACAO-PRIORIDADE' ] )
        elif mesa == 'N4-SAP-SUSTENTACAO-ESCALADOS':
            duracao_m   = inc.calc_duration_mesas( [ 'N4-SAP-SUSTENTACAO-ESCALADOS' ] )
            pendencia_m = inc.calc_pendencia_mesas( [ 'N4-SAP-SUSTENTACAO-ESCALADOS' ] )
        else:
            duracao_m   = inc.calc_duration_mesas( n4_config.MESAS_NAO_PRIORITARIAS )
            pendencia_m = inc.calc_pendencia_mesas( n4_config.MESAS_NAO_PRIORITARIAS )
        
        if mesa == 'N4-SAP-SUSTENTACAO-PRIORIDADE':
            prazo_m = prp.Prp.PRAZO_M
        elif mesa == 'N4-SAP-SUSTENTACAO-ESCALADOS' and categoria in ('REALIZAR', 'REALIZAR - TAREFA'):
            prazo_m = peso30.Peso30.PRAZO_REALIZAR_M
        elif mesa == 'N4-SAP-SUSTENTACAO-ESCALADOS' and categoria == 'CORRIGIR':
            prazo_m = peso30.Peso30.PRAZO_CORRIGIR_M
        elif mesa == 'N4-SAP-SUSTENTACAO-ESCALADOS' and categoria == 'CORRIGIR':
            prazo_m = peso30.Peso30.PRAZO_ORIENTAR_M
        elif categoria == 'ORIENTAR':
            prazo_m = pro.Pro.PRAZO_M
        elif categoria == 'CORRIGIR':
            prazo_m = prc.Prc.PRAZO_M
        elif categoria in ('REALIZAR', 'REALIZAR - TAREFA'):
            prazo_m = inc.prazo
        else:
            assert 1 == 2
        
        result = {
            'id_chamado'    : inc.id_chamado
        ,   'chamado_pai'   : inc.chamado_pai
        ,   'categoria'     : categoria
        ,   'mesa_atual'    : mesa
        ,   'status'        : status
        ,   'oferta'        : inc.oferta
        ,   'prazo'         : prazo_m
        ,   'duracao_m'     : duracao_m
        ,   'pendencia_m'   : pendencia_m
        ,   'acoes'         : []
        ,   'atribuicoes'   : []
        }
        for acao in inc.acoes:
            result[ 'acoes' ].append({
                'id_acao'       : acao.id_acao
            ,   'acao_nome'     : acao.acao_nome
            ,   'pendencia'     : acao.pendencia == 'S'
            ,   'mesa_atual'    : acao.mesa_atual
            ,   'data_acao'     : acao.data_acao
            ,   'data_fim_acao' : acao.data_fim_acao
            ,   'duracao_m'     : acao.duracao_m
            ,   'status'        : acao.status            
            })
        for atrib in inc.atribuicoes:
            result[ 'atribuicoes' ].append({
                'seq'               : atrib.seq
            ,   'mesa'              : atrib.mesa
            ,   'entrada'           : atrib.entrada
            ,   'status_entrada'    : atrib.status_entrada
            ,   'saida'             : atrib.saida
            ,   'status_saida'      : atrib.status_saida
            ,   'duracao_m'         : atrib.duracao_m
            ,   'pendencia_m'       : atrib.pendencia_m
            })
        return result
        
    def export_incidents(self, click):
        logger.info('exporting incidents')
        result = []
        for mesa_name in n4_config.MESAS:
            logger.info(f" -> {mesa_name}")
            mesa = click.get_mesa(mesa_name)
            result.append({ "name": mesa_name, "incidents": [] })
            for inc in mesa.get_incidentes():
                data = self.inc2json(inc)
                result[ -1 ][ "incidents" ].append(data)
        return result
    """
    
    def import_firebase(self, cred, key, value):
        if self.nocloud:
            logger.warn('skipping cloud sync')
            return
        logger.info('importing data to firebase')
        db = firestore.client()
        doc_ref = db.collection('indicadores').document(key)
        doc_ref.set(value)
    
    def get_dirs_apuracoes(self):
        logger.info('getting diretórios de apuração')
        result = []
        for d in os.listdir(self.dir_n4):
            path = os.path.join(self.dir_n4, d)
            if not os.path.isdir(path) or d.startswith('_'):
                continue
            result.append(path)
        result.sort()
        return result
    
    def connect_db(self, dir_apuracao):
        logger.info("connecting to the db")
        path = os.path.join(dir_apuracao, config.CONSOLIDATED_DB)
        return sqlite3.connect(path)
    
    def retrieve_kpis(self, conn):
        logger.info("retrieving KPI's")
        sql = """
            SELECT  INDICADOR
            ,       MESA
            ,       CAST(VALOR AS REAL) AS VALOR
            ,       SLA 
            ,       OBS
            FROM    INDICADORES
            WHERE   INDICADOR NOT IN ( 'INICIO_PERIODO', 'FIM_PERIODO' )
        """
        return pd.read_sql(sql, conn, index_col=None)
    
    def generate_table(self):
        return { campo: [] for campo in self.CAMPOS_QUADRO }
    
    def update_value(self, campo, quadro, df):
        indicador, mesa = self.INDICADORES_MESAS[ campo ]
        if not mesa: 
            valor = df[ df[ "INDICADOR" ] == indicador ][ 'VALOR' ].iat[ 0 ]
        else:
            valor = df[ ( df[ "INDICADOR" ] == indicador) & ( df[ "MESA" ] == mesa) ][ 'VALOR' ].iat[ 0 ]
        quadro[ campo ].append(valor)
        
    def update_table(self, periodo, quadro, df):
        quadro[ "PERIODO" ].append(periodo)
        for campo in self.CAMPOS_QUADRO:
            if campo == "PERIODO":
                continue
            self.update_value(campo, quadro, df)
            if campo == "PRP" or campo == "PESO30":
                quadro[ campo ][ -1 ] = 100.0 - quadro[ campo ][ -1 ]
                
    def format_floats(self, quadro):
        import locale
        for campo in self.CAMPOS_QUADRO:
            valores = []
            for valor in quadro[ campo ]:
                if isinstance(valor, float):
                    valor = valor.replace(".", ",")
                else:
                    valor_txt = valor
                valores.append(valor_txt)
            quadro[ campo ] = valores
            
    def export_tables(self, cred, quadro, quadro_acc):
        logger.info("exporting summary table")
        quadro_df = pd.DataFrame(quadro)
        quadro_data = quadro_df.to_dict(orient='record')
        self.import_firebase(cred, 'quadro_indicadores', { 
            "carga": util.now(), 
            "dados": quadro_data,
            "ordem_campos": self.CAMPOS_QUADRO
        })
        
        
        logger.info("exporting summary table acc")
        quadro_acc_df = pd.DataFrame(quadro_acc)
        quadro_acc_data = quadro_acc_df.to_dict(orient='record')
        self.import_firebase(cred, 'quadro_indicadores_acc', { 
            "carga": util.now(), 
            "dados": quadro_acc_data,
            "ordem_campos": self.CAMPOS_QUADRO
        })
        # export excel ... needs converting floats
        #self.format_floats(quadro)
        #quadro_df = pd.DataFrame(quadro)
        #quadro_data = quadro_df.to_dict(orient='record')
        
        #self.format_floats(quadro_acc)
        #quadro_acc_df = pd.DataFrame(quadro_acc)
        #quadro_acc_data = quadro_acc_df.to_dict(orient='record')

        with self.open_spreadsheet() as xw:
            quadro_df.to_excel(xw, sheet_name="INDICADORES", index=False)
            quadro_acc_df.to_excel(xw, sheet_name="INDICADORES_ACC", index=False)
    
    def open_spreadsheet(self):
        logger.info("opening spreadsheet")
        ks = os.path.join(self.dir_n4, "__" + self.OUTPUT_SPREADSHEET)
        if os.path.exists(ks):
            logger.warning("spreadsheet already exists. Deleting it")
            os.unlink(ks)
        return pd.ExcelWriter(ks, datetime_format=None)   

    def run(self):
        try:
            logger.info('export_firebase - versão %d.%d.%d', *self.VERSION)
            dirs_apuracoes = self.get_dirs_apuracoes()
            quadro = self.generate_table()
            quadro_acc = self.generate_table()
            cred = credentials.Certificate(self.fb_conf)
            firebase_admin.initialize_app(cred)
            for dir_apuracao in dirs_apuracoes:
                _, periodo = os.path.split(dir_apuracao)
                logger.info(f'processing {periodo}')
                conn = self.connect_db(dir_apuracao)
                kpis_df = self.retrieve_kpis(conn)
                data = kpis_df.to_dict(orient='record')
                self.import_firebase(cred, periodo, { "periodo": periodo, "indicadores": data, "carga": util.now() } )
                if not periodo.endswith("-ACC"):
                    self.update_table(periodo, quadro, kpis_df)
                else:
                    self.update_table(periodo, quadro_acc, kpis_df)
                del conn
            self.export_tables(cred, quadro, quadro_acc)
            logger.info("finished")
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nocloud', action="store_true", help='skip cloud sync')
    parser.add_argument('dir_n4', type=str, help='diretório n4')
    parser.add_argument('cred_json', type=str, help='json credential file for firebase')
    args = parser.parse_args()
    app = App(args.dir_n4, args.cred_json, args.nocloud)
    app.run()
    