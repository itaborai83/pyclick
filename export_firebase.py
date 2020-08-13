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
    
    VERSION = (1, 0, 0)
    OUTPUT_SPREADSHEET = "export_kpis.xlsx"
    CSAT_SPREADSHEET = "__csat.xlsx"
    CSAT_ACC_SHEET = "CSAT"
    CSAT_SHEET = "CSAT - Mês"
    SLA_CSAT = "90"
    CAMPOS_QUADRO = [
        "PERIODO",
        "PRP", 
        "PESO30", 
        "PRO", 
        "PRO_PESO30", 
        "PRO_ABGE", 
        "PRO_PRAPO", 
        "PRO_CORP", 
        "PRO_FIN", 
        "PRO_GRC", 
        "PRO_PORTAL", 
        "PRO_SERV", 
        "PRC", 
        "PRC_PESO30",
        "PRC_ABGE", 
        "PRC_PRAPO", 
        "PRC_CORP", 
        "PRC_FIN", 
        "PRC_GRC", 
        "PRC_PORTAL", 
        "PRC_SERV", 
        "PRS", 
        "PRS_PESO30", 
        "PRS_ABGE", 
        "PRS_PRAPO", 
        "PRS_CORP", 
        "PRS_FIN", 
        "PRS_GRC", 
        "PRS_PORTAL", 
        "PRS_SERV", 
        "IDS", 
        "IDS_PESO35", 
        "IDS_PESO30", 
        "IDS_ABGE", 
        "IDS_PRAPO", 
        "IDS_CORP", 
        "IDS_FIN", 
        "IDS_GRC", 
        "IDS_PORTAL", 
        "IDS_SERV", 
        "AGING60", 
        "AGING60_PESO35", 
        "AGING60_PESO30", 
        "AGING60_ABGE", 
        "AGING60_PRAPO", 
        "AGING60_CORP", 
        "AGING60_FIN", 
        "AGING60_GRC", 
        "AGING60_PORTAL", 
        "AGING60_SERV", 
        "AGING90", 
        "AGING90_PESO35",
        "AGING90_PESO30",
        "AGING90_ABGE", 
        "AGING90_PRAPO", 
        "AGING90_CORP", 
        "AGING90_FIN", 
        "AGING90_GRC", 
        "AGING90_PORTAL", 
        "AGING90_SERV", 
        "CSAT_INDRA", 
        "CSAT_INDRA_PESO35",
        "CSAT_INDRA_PESO30",
        "CSAT_INDRA_ABGE", 
        "CSAT_INDRA_PRAPO", 
        "CSAT_INDRA_CORP", 
        "CSAT_INDRA_FIN", 
        "CSAT_INDRA_GRC", 
        "CSAT_INDRA_PORTAL", 
        "CSAT_INDRA_SERV", 
        "CSAT_GERENCIA",
        "CSAT_GERENCIA_PESO35",
        "CSAT_GERENCIA_PESO30",
        "CSAT_GERENCIA_ABGE",
        "CSAT_GERENCIA_PRAPO",
        "CSAT_GERENCIA_CORP",
        "CSAT_GERENCIA_FIN",
        "CSAT_GERENCIA_GRC",
        "CSAT_GERENCIA_GRCAC",
        "CSAT_GERENCIA_PORTAL",
        "CSAT_GERENCIA_SERV",
        "CSAT_GERENCIA_BW",
        "CSAT_GERENCIA_CE",
        "CSAT_GERENCIA_SATI",
        "CSAT_GERENCIA_DESENV",
        "ESTOQUE", 
        "ESTOQUE_PESO35", 
        "ESTOQUE_PESO30", 
        "ESTOQUE_ABGE", 
        "ESTOQUE_PRAPO", 
        "ESTOQUE_CORP", 
        "ESTOQUE_FIN", 
        "ESTOQUE_GRC", 
        "ESTOQUE_PORTAL", 
        "ESTOQUE_SERV", 
        "ENCERRADOS", 
        "ENCERRADOS_PESO35", 
        "ENCERRADOS_PESO30", 
        "ENCERRADOS_ABGE", 
        "ENCERRADOS_PRAPO", 
        "ENCERRADOS_CORP", 
        "ENCERRADOS_FIN",
        "ENCERRADOS_GRC",
        "ENCERRADOS_PORTAL",
        "ENCERRADOS_SERV",
        "CANCELADOS",
        "CANCELADOS_PESO35",
        "CANCELADOS_PESO30",
        "CANCELADOS_ABGE",
        "CANCELADOS_PRAPO",
        "CANCELADOS_CORP",
        "CANCELADOS_FIN",
        "CANCELADOS_GRC",
        "CANCELADOS_PORTAL",
        "CANCELADOS_SERV",
        #"INICIO_PERIODO",
        #"FIM_PERIODO",
        #"EXPURGOS",
    ]
    
    INDICADORES_MESAS = {
        "PERIODO"               : ("PERIODO", None),
        "PRP"                   : ("PRP", None),
        "PESO30"                : ("PESO30", None),
        "PRO"                   : ("PRO", None),
        "PRO_PESO30"            : ("PRO", "PESO30"),
        "PRO_ABGE"              : ("PRO", "ABGE"),
        "PRO_PRAPO"             : ("PRO", "PRAPO"),
        "PRO_CORP"              : ("PRO", "CORP"),
        "PRO_FIN"               : ("PRO", "FIN"),
        "PRO_GRC"               : ("PRO", "GRC"),
        "PRO_PORTAL"            : ("PRO", "PORTAL"),
        "PRO_SERV"              : ("PRO", "SERV"),
        "PRC"                   : ("PRC", None),
        "PRC_PESO30"            : ("PRC", "PESO30"),
        "PRC_ABGE"              : ("PRC", "ABGE"),
        "PRC_PRAPO"             : ("PRC", "PRAPO"),
        "PRC_CORP"              : ("PRC", "CORP"),
        "PRC_FIN"               : ("PRC", "FIN"),
        "PRC_GRC"               : ("PRC", "GRC"),
        "PRC_PORTAL"            : ("PRC", "PORTAL"),
        "PRC_SERV"              : ("PRC", "SERV"),
        "PRS"                   : ("PRS", None),
        "PRS_PESO30"            : ("PRS", "PESO30"),
        "PRS_ABGE"              : ("PRS", "ABGE"),
        "PRS_PRAPO"             : ("PRS", "PRAPO"),
        "PRS_CORP"              : ("PRS", "CORP"),
        "PRS_FIN"               : ("PRS", "FIN"),
        "PRS_GRC"               : ("PRS", "GRC"),
        "PRS_PORTAL"            : ("PRS", "PORTAL"),
        "PRS_SERV"              : ("PRS", "SERV"),
        "IDS"                   : ("IDS", None),
        "IDS_PESO35"            : ("IDS", "PESO35"),
        "IDS_PESO30"            : ("IDS", "PESO30"),
        "IDS_ABGE"              : ("IDS", "ABGE"),
        "IDS_PRAPO"             : ("IDS", "PRAPO"),
        "IDS_CORP"              : ("IDS", "CORP"),
        "IDS_FIN"               : ("IDS", "FIN"),
        "IDS_GRC"               : ("IDS", "GRC"),
        "IDS_PORTAL"            : ("IDS", "PORTAL"),
        "IDS_SERV"              : ("IDS", "SERV"),
        "AGING60"               : ("AGING 60", None),
        "AGING60_PESO35"        : ("AGING 60", "PESO35"),
        "AGING60_PESO30"        : ("AGING 60", "PESO30"),
        "AGING60_ABGE"          : ("AGING 60", "ABGE"),
        "AGING60_PRAPO"         : ("AGING 60", "PRAPO"),
        "AGING60_CORP"          : ("AGING 60", "CORP"),
        "AGING60_FIN"           : ("AGING 60", "FIN"),
        "AGING60_GRC"           : ("AGING 60", "GRC"),
        "AGING60_PORTAL"        : ("AGING 60", "PORTAL"),
        "AGING60_SERV"          : ("AGING 60", "SERV"),
        "AGING90"               : ("AGING 90", None),
        "AGING90_PESO35"        : ("AGING 90", "PESO35"),
        "AGING90_PESO30"        : ("AGING 90", "PESO30"),
        "AGING90_ABGE"          : ("AGING 90", "ABGE"),
        "AGING90_PRAPO"         : ("AGING 90", "PRAPO"),
        "AGING90_CORP"          : ("AGING 90", "CORP"),
        "AGING90_FIN"           : ("AGING 90", "FIN"),
        "AGING90_GRC"           : ("AGING 90", "GRC"),
        "AGING90_PORTAL"        : ("AGING 90", "PORTAL"),
        "AGING90_SERV"          : ("AGING 90", "SERV"),
        "CSAT_INDRA"            : ("CSAT - Indra", None),
        "CSAT_INDRA_PESO35"     : ("CSAT - Indra", "PESO35"),
        "CSAT_INDRA_PESO30"     : ("CSAT - Indra", "PESO30"),
        "CSAT_INDRA_ABGE"       : ("CSAT - Indra", "ABGE"),
        "CSAT_INDRA_PRAPO"      : ("CSAT - Indra", "PRAPO"),
        "CSAT_INDRA_CORP"       : ("CSAT - Indra", "CORP"),
        "CSAT_INDRA_FIN"        : ("CSAT - Indra", "FIN"),
        "CSAT_INDRA_GRC"        : ("CSAT - Indra", "GRC"),
        "CSAT_INDRA_PORTAL"     : ("CSAT - Indra", "PORTAL"),
        "CSAT_INDRA_SERV"       : ("CSAT - Indra", "SERV"),        
        "CSAT_GERENCIA"         : ("CSAT - Gerência", None),
        "CSAT_GERENCIA_PESO35"  : ("CSAT - Gerência", "PESO35"  ),
        "CSAT_GERENCIA_PESO30"  : ("CSAT - Gerência", "PESO30"  ),
        "CSAT_GERENCIA_ABGE"    : ("CSAT - Gerência", "ABGE"    ),
        "CSAT_GERENCIA_PRAPO"   : ("CSAT - Gerência", "PRAPO"   ),
        "CSAT_GERENCIA_CORP"    : ("CSAT - Gerência", "CORP"    ),
        "CSAT_GERENCIA_FIN"     : ("CSAT - Gerência", "FIN"     ),
        "CSAT_GERENCIA_GRC"     : ("CSAT - Gerência", "GRC"     ),
        "CSAT_GERENCIA_GRCAC"   : ("CSAT - Gerência", "GRCAC"   ),
        "CSAT_GERENCIA_PORTAL"  : ("CSAT - Gerência", "PORTAL"  ),
        "CSAT_GERENCIA_SERV"    : ("CSAT - Gerência", "SERV"    ),
        "CSAT_GERENCIA_BW"      : ("CSAT - Gerência", "BW"      ),
        "CSAT_GERENCIA_CE"      : ("CSAT - Gerência", "CE"      ),
        "CSAT_GERENCIA_SATI"    : ("CSAT - Gerência", "SATI"    ),
        "CSAT_GERENCIA_DESENV"  : ("CSAT - Gerência", "DESENV"  ),
        "ESTOQUE"               : ("ESTOQUE", None),
        "ESTOQUE_PESO35"        : ("ESTOQUE", "PESO35"),
        "ESTOQUE_PESO30"        : ("ESTOQUE", "PESO30"),
        "ESTOQUE_ABGE"          : ("ESTOQUE", "ABGE"),
        "ESTOQUE_PRAPO"         : ("ESTOQUE", "PRAPO"),
        "ESTOQUE_CORP"          : ("ESTOQUE", "CORP"),
        "ESTOQUE_FIN"           : ("ESTOQUE", "FIN"),
        "ESTOQUE_GRC"           : ("ESTOQUE", "GRC"),
        "ESTOQUE_PORTAL"        : ("ESTOQUE", "PORTAL"),
        "ESTOQUE_SERV"          : ("ESTOQUE", "SERV"),
        "ENCERRADOS"            : ("ENCERRADOS", None),
        "ENCERRADOS_PESO35"     : ("ENCERRADOS", "PESO35"),
        "ENCERRADOS_PESO30"     : ("ENCERRADOS", "PESO30"),
        "ENCERRADOS_ABGE"       : ("ENCERRADOS", "ABGE"),
        "ENCERRADOS_PRAPO"      : ("ENCERRADOS", "PRAPO"),
        "ENCERRADOS_CORP"       : ("ENCERRADOS", "CORP"),
        "ENCERRADOS_FIN"        : ("ENCERRADOS", "FIN"),
        "ENCERRADOS_GRC"        : ("ENCERRADOS", "GRC"),
        "ENCERRADOS_PORTAL"     : ("ENCERRADOS", "PORTAL"),
        "ENCERRADOS_SERV"       : ("ENCERRADOS", "SERV"),
        "CANCELADOS"            : ("CANCELADOS", None),
        "CANCELADOS_PESO35"     : ("CANCELADOS", "PESO35"),
        "CANCELADOS_PESO30"     : ("CANCELADOS", "PESO30"),
        "CANCELADOS_ABGE"       : ("CANCELADOS", "ABGE"),
        "CANCELADOS_PRAPO"      : ("CANCELADOS", "PRAPO"),
        "CANCELADOS_CORP"       : ("CANCELADOS", "CORP"),
        "CANCELADOS_FIN"        : ("CANCELADOS", "FIN"),
        "CANCELADOS_GRC"        : ("CANCELADOS", "GRC"),
        "CANCELADOS_PORTAL"     : ("CANCELADOS", "PORTAL"),
        "CANCELADOS_SERV"       : ("CANCELADOS", "SERV"),
        #"INICIO_PERIODO"        : ("INÍCIO PERÍODO", None),
        #"FIM_PERIODO"           : ("FIM PERÍODO", None),
        #"EXPURGOS"              : ("EXPURGOS", None),
    }
    LAST_CSAT_INDRA = 'CSAT_INDRA_SERV'
    CSAT_SPLICED_ENTRIES = [ 
        "CSAT_GERENCIA"         , 
        "CSAT_GERENCIA_PESO35"  , 
        "CSAT_GERENCIA_PESO30"  , 
        "CSAT_GERENCIA_ABGE"    , 
        "CSAT_GERENCIA_PRAPO"   , 
        "CSAT_GERENCIA_CORP"    , 
        "CSAT_GERENCIA_FIN"     , 
        "CSAT_GERENCIA_GRC"     , 
        "CSAT_GERENCIA_GRCAC"   , 
        "CSAT_GERENCIA_PORTAL"  , 
        "CSAT_GERENCIA_SERV"    , 
        "CSAT_GERENCIA_BW"      , 
        "CSAT_GERENCIA_CE"      , 
        "CSAT_GERENCIA_SATI"    , 
        "CSAT_GERENCIA_DESENV"
    ]

    def __init__(self, dir_n4, dir_csat, fb_conf, nocloud):
        self.dir_n4 = dir_n4
        self.dir_csat = dir_csat
        self.fb_conf = fb_conf
        self.nocloud = nocloud
    
    def import_firebase(self, cred, collection, key, value):
        if self.nocloud:
            logger.warning('skipping cloud sync')
            return
        logger.info('importing data to firebase')
        db = firestore.client()
        doc_ref = db.collection(collection).document(key)
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
    
    def retrieve_kpis(self, periodo, conn, csat_gerencia_df):
        logger.info("retrieving KPI's")
        sql = """
            SELECT  CASE WHEN INDICADOR = 'CSAT - Período' THEN 'CSAT - Indra'
                         ELSE INDICADOR END AS INDICADOR
            ,       MESA
            ,       COALESCE(CAST(VALOR AS REAL), 0) AS VALOR
            ,       SLA
            ,       OBS
            FROM    INDICADORES
            WHERE   INDICADOR NOT IN ( 'INÍCIO PERÍODO', 'FIM PERÍODO', 'EXPURGOS', '--CSAT')
        """
        df = pd.read_sql(sql, conn, index_col=None)
        data = df.to_dict('list')
        nan = float('NaN')
        indicador, mesa = self.INDICADORES_MESAS[ self.LAST_CSAT_INDRA ]
        csat_idx = data[ 'INDICADOR' ].index(indicador, 0)
        serv_idx = data[ 'MESA' ].index(mesa, csat_idx)
        start_idx = serv_idx + 1
        for i, campo in enumerate(self.CSAT_SPLICED_ENTRIES):
            indicador, mesa = self.INDICADORES_MESAS[ campo ]
            if mesa is None:
                csat_df = csat_gerencia_df[ ( csat_gerencia_df[ 'PERIODO'   ]   == periodo )    & 
                                            ( csat_gerencia_df[ 'INDICADOR' ]   == indicador )  & 
                                            ( ( csat_gerencia_df[ 'MESA'    ].isna() )          |
                                              ( csat_gerencia_df[ 'MESA'    ]   == ""  ) )      ]
            else:
                csat_df = csat_gerencia_df[ ( csat_gerencia_df[ 'PERIODO'   ]   == periodo )    & 
                                            ( csat_gerencia_df[ 'INDICADOR' ]   == indicador )  &
                                            ( csat_gerencia_df[ 'MESA'      ]   == mesa )       ]
                                            
            if len(csat_df) > 0:
                data[ 'INDICADOR'   ].insert(start_idx + i, indicador)
                data[ 'MESA'        ].insert(start_idx + i, mesa if mesa else "" )
                data[ 'VALOR'       ].insert(start_idx + i, csat_df[ 'VALOR' ].iat[ 0 ])
                data[ 'SLA'         ].insert(start_idx + i, csat_df[ 'SLA'   ].iat[ 0 ])
                data[ 'OBS'         ].insert(start_idx + i, csat_df[ 'OBS'   ].iat[ 0 ])
        return pd.DataFrame(data)
    
    def generate_table(self):
        return { campo: [] for campo in self.CAMPOS_QUADRO }
    
    def update_value(self, campo, quadro, df):
        indicador, mesa = self.INDICADORES_MESAS[ campo ]
        try:
            if not mesa: 
                valor = df[ df[ "INDICADOR" ] == indicador ][ 'VALOR' ].iat[ 0 ]
            else:
                valor = df[ ( df[ "INDICADOR" ] == indicador) & 
                            ( df[ "MESA" ]      == mesa) ][ 'VALOR' ].iat[ 0 ]
        except IndexError:
            valor = float('NaN')
        quadro[ campo ].append(valor)    
    
    def update_table(self, periodo, quadro, df):
        quadro[ "PERIODO" ].append(periodo)
        for campo in self.CAMPOS_QUADRO:
            if campo == "PERIODO":
                continue
            
            self.update_value(campo, quadro, df)
            if campo == "PRP" or campo == "PESO30":
                quadro[ campo ][ -1 ] = 100.0 - quadro[ campo ][ -1 ]
            
    def export_tables(self, cred, quadro, quadro_acc, xw):
        logger.info("exporting summary table")
        quadro_df = pd.DataFrame(quadro)
        logger.info("exporting summary table acc")
        quadro_acc_df = pd.DataFrame(quadro_acc)
        quadro_df.to_excel(xw, sheet_name="INDICADORES", index=False)
        quadro_acc_df.to_excel(xw, sheet_name="INDICADORES_ACC", index=False)
    
    def open_spreadsheet(self):
        logger.info("opening spreadsheet")
        ks = os.path.join(self.dir_n4, "__" + self.OUTPUT_SPREADSHEET)
        if os.path.exists(ks):
            logger.warning("spreadsheet already exists. Deleting it")
            os.unlink(ks)
        return pd.ExcelWriter(ks, datetime_format=None)   
    
    def process_csat(self, cred):
        logger.info('reading CSAT spreadsheet')
        path = os.path.join(self.dir_csat, self.CSAT_SPREADSHEET)
        
        csat_df = pd.read_excel(path, sheet_name=self.CSAT_SHEET, index_col=None)
        csat_data = csat_df.to_dict(orient="record")
        self.import_firebase(cred, 'csat', 'quadro_csat', { 
            "carga": util.now(), 
            "dados": csat_data,
            "ordem_campos": csat_df.columns.to_list()
        })        
        
        csat_acc_df = pd.read_excel(path, sheet_name=self.CSAT_ACC_SHEET, index_col=None)        
        csat_acc_data = csat_acc_df.to_dict(orient="record")
        self.import_firebase(cred, 'csat', 'quadro_csat_acc', { 
            "carga": util.now(), 
            "dados": csat_acc_data,
            "ordem_campos": csat_acc_df.columns.to_list()
        })
    
        mesas = [
            'N4-SAP-SUSTENTACAO-PRIORIDADE',
            'N4-SAP-SUSTENTACAO-ESCALADOS',
            'N4-SAP-SUSTENTACAO-ABAST_GE',
            'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',
            'N4-SAP-SUSTENTACAO-CORPORATIVO',
            'N4-SAP-SUSTENTACAO-FINANCAS',
            'N4-SAP-SUSTENTACAO-GRC',
            'N4-SAP_APOIO_E_CORRECAO-GRC',
            'N4-SAP-SUSTENTACAO-PORTAL',
            'N4-SAP-SUSTENTACAO-SERVICOS',
            'N4-SAP-SUSTENTACAO-BI',
            'N4-SAP-SUSTENTACAO-CE',
            'N4-SAP-SUSTENTACAO-SATI',
            'N4-SAP-SUSTENTACAO-DESENV',
        ]
        mesa_mapping = {
            'N4-SAP-SUSTENTACAO-PRIORIDADE'     : 'PESO35',
            'N4-SAP-SUSTENTACAO-ESCALADOS'      : 'PESO30',
            'N4-SAP-SUSTENTACAO-ABAST_GE'       : 'ABGE',
            'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' : 'PRAPO',
            'N4-SAP-SUSTENTACAO-CORPORATIVO'    : 'CORP',
            'N4-SAP-SUSTENTACAO-FINANCAS'       : 'FIN',
            'N4-SAP-SUSTENTACAO-GRC'            : 'GRC',
            'N4-SAP_APOIO_E_CORRECAO-GRC'       : 'GRCAC',
            'N4-SAP-SUSTENTACAO-PORTAL'         : 'PORTAL',
            'N4-SAP-SUSTENTACAO-SERVICOS'       : 'SERV',
            'N4-SAP-SUSTENTACAO-BI'             : 'BW',
            'N4-SAP-SUSTENTACAO-CE'             : 'CE',
            'N4-SAP-SUSTENTACAO-SATI'           : 'SATI',
            'N4-SAP-SUSTENTACAO-DESENV'         : 'DESENV',
        }
        meses = [ 'JAN', 'FEV', 'MAR', 'ABR', 'MAIO', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ' ]
        periodo_mapping = {
            'JAN'   : '2020-01', 
            'FEV'   : '2020-02', 
            'MAR'   : '2020-03', 
            'ABR'   : '2020-04', 
            'MAIO'  : '2020-05', 
            'JUN'   : '2020-06', 
            'JUL'   : '2020-07', 
            'AGO'   : '2020-08', 
            'SET'   : '2020-09', 
            'OUT'   : '2020-10', 
            'NOV'   : '2020-11', 
            'DEZ'   : '2020-12'
        }
        csat_gerencia = { 
            'PERIODO' : [], 'INDICADOR' : [], 'MESA' : [], 'VALOR' : [], 'SLA' : [], 'OBS' : [] 
        }        
        for mes in meses:
            periodo = periodo_mapping[ mes ]
            valor = csat_df[ csat_df[ 'MESA' ].isna() ][ mes ].iat[0]
            if not pd.isna(valor):
                qtd = csat_df[ csat_df[ 'MESA' ].isna() ][ mes + " Qtd" ].iat[0]
                non_breached = int(valor/100.0 * qtd)
                breached = int((100.0-valor)/100.0 * qtd)
                obs = f'1.0 - ({breached} violações / {non_breached + breached})'
                csat_gerencia[ 'PERIODO' ].append(periodo)
                csat_gerencia[ 'INDICADOR' ].append('CSAT - Gerência')
                csat_gerencia[ 'MESA' ].append("")
                csat_gerencia[ 'VALOR' ].append(valor)
                csat_gerencia[ 'SLA' ].append(self.SLA_CSAT)
                csat_gerencia[ 'OBS' ].append(obs)
            
            periodo_acc = periodo + "-ACC"
            valor_acc = csat_acc_df[ csat_acc_df[ 'MESA' ].isna() ][ mes ].iat[0]
            if not pd.isna(valor):
                qtd_acc = csat_acc_df[ csat_acc_df[ 'MESA' ].isna() ][ mes + " Qtd" ].iat[0]
                non_breached_acc = int(valor_acc/100.0 * qtd_acc)
                breached_acc = int((100.0-valor_acc)/100.0 * qtd_acc)
                obs_acc = f'1.0 - ({breached} violações / {non_breached + breached})'
                csat_gerencia[ 'PERIODO' ].append(periodo_acc)
                csat_gerencia[ 'INDICADOR' ].append('CSAT - Gerência')
                csat_gerencia[ 'MESA' ].append("")
                csat_gerencia[ 'VALOR' ].append(valor_acc)
                csat_gerencia[ 'SLA' ].append(self.SLA_CSAT)
                csat_gerencia[ 'OBS' ].append(obs_acc)
            
            for mesa in mesas:
                valor = csat_df[ csat_df[ 'MESA' ] == mesa ][ mes ].iat[0]
                if not pd.isna(valor):
                    qtd = csat_df[ csat_df[ 'MESA' ] == mesa ][ mes + " Qtd" ].iat[0]
                    non_breached = int(valor/100.0 * qtd)
                    breached = int((100.0-valor)/100.0 * qtd)
                    obs = f'1.0 - ({breached} violações / {non_breached + breached})'
                    csat_gerencia[ 'PERIODO' ].append(periodo)
                    csat_gerencia[ 'INDICADOR' ].append('CSAT - Gerência')
                    csat_gerencia[ 'MESA' ].append(mesa_mapping[ mesa ])
                    csat_gerencia[ 'VALOR' ].append(valor)
                    csat_gerencia[ 'SLA' ].append(self.SLA_CSAT)
                    csat_gerencia[ 'OBS' ].append(obs)
                
                periodo_acc = periodo + "-ACC"
                valor_acc = csat_acc_df[ csat_acc_df[ 'MESA' ] == mesa ][ mes ].iat[0]
                if not pd.isna(valor):
                    qtd_acc = csat_acc_df[ csat_acc_df[ 'MESA' ] == mesa ][ mes + " Qtd" ].iat[0]
                    non_breached_acc = int(valor_acc/100.0 * qtd_acc)
                    breached_acc = int((100.0-valor_acc)/100.0 * qtd_acc)
                    obs_acc = f'1.0 - ({breached_acc} violações / {non_breached_acc + breached_acc})'
                    csat_gerencia[ 'PERIODO' ].append(periodo_acc)
                    csat_gerencia[ 'INDICADOR' ].append('CSAT - Gerência')
                    csat_gerencia[ 'MESA' ].append(mesa_mapping[ mesa ])
                    csat_gerencia[ 'VALOR' ].append(valor_acc)
                    csat_gerencia[ 'SLA' ].append(self.SLA_CSAT)
                    csat_gerencia[ 'OBS' ].append(obs_acc)
                periodo_acc = periodo + "-ACC"
        #print(csat_gerencia)
        return pd.DataFrame(csat_gerencia)
    
    def parse_periodo(self, dir_apuracao):
        parts = dir_apuracao.split("-")
        num_parts = len(parts)
        assert 2 <= num_parts <= 3
        ano, mes = int(num_parts[0]), int(num_parts[1])
        if num_parts == 3:
            assert num_parts[2] == 'ACC'
            acc = True
        else:
            acc = False
        return ano, mes, acc
        
    def run(self):
        try:
            logger.info('export_firebase - versão %d.%d.%d', *self.VERSION)
            cred = credentials.Certificate(self.fb_conf)
            firebase_admin.initialize_app(cred)
            dirs_apuracoes = self.get_dirs_apuracoes()
            quadro = self.generate_table()
            quadro_acc = self.generate_table()
            #self.extract_csat_gerencia(quadro, acc=False)
            #self.extract_csat_gerencia(quadro_acc, acc=True)            
            csat_gerencia_df = self.process_csat(cred)
            for dir_apuracao in dirs_apuracoes:
                _, periodo = os.path.split(dir_apuracao)
                logger.info(f'processing {periodo}')
                #ano, mes, acc = self.parse_periodo(periodo)
                conn = self.connect_db(dir_apuracao)
                kpis_df = self.retrieve_kpis(periodo, conn, csat_gerencia_df)
                data = kpis_df.to_dict(orient='record')
                self.import_firebase(cred, 'indicadores', periodo, { "periodo": periodo, "indicadores": data, "carga": util.now() } )
                if not periodo.endswith("-ACC"):
                    self.update_table(periodo, quadro, kpis_df)
                else:
                    self.update_table(periodo, quadro_acc, kpis_df)
                del conn
            with self.open_spreadsheet() as xw:                
                self.export_tables(cred, quadro, quadro_acc, xw)
                
            logger.info("finished")
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nocloud', action="store_true", help='skip cloud sync')
    parser.add_argument('dir_n4', type=str, help='diretório n4')
    parser.add_argument('dir_csat', type=str, help='diretório CSAT')
    parser.add_argument('cred_json', type=str, help='json credential file for firebase')
    args = parser.parse_args()
    app = App(args.dir_n4, args.dir_csat, args.cred_json, args.nocloud)
    app.run()
    