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

    def __init__(self, dir_apuracao, fb_conf):
        self.dir_apuracao = dir_apuracao
        self.fb_conf = fb_conf
        
    def connect_db(self):
        logger.info("connecting to the db")
        path = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        return sqlite3.connect(path)

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
        
    def import_firebase(self, data):
        logger.info('importing data to firebase')
        cred = credentials.Certificate(self.fb_conf)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        for mesa in data:
            doc_ref = db.collection('mesas').document(mesa[ 'name' ])
            doc_ref.set(mesa)            

    def run(self):
        try:
            logger.info('export_firebase - versão %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            r = repo.RepoN4(conn)
            click, events_df, expurgos_df, start_dt, end_dt = self.load_click(r)
            logger.info("finished")
            data = self.export_incidents(click)
            self.import_firebase(data)
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    parser.add_argument('cred_json', type=str, help='json credential file for firebase')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.cred_json)
    app.run()
    