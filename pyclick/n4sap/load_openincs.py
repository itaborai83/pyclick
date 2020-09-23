import os
import shutil
import argparse
import sys
import pandas as pd
import sqlite3
import logging
import requests

import pyclick.models as models
import pyclick.util as util
import pyclick.config as config
import pyclick.n4sap.repo as repo

import pyclick.n4sap.config as n4_config
import pyclick.n4sap.models as n4_models
from pyclick.n4sap.status import Estoque, Encerrados, Cancelados


assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('load_openincs')



class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao, periodo_apuracao, portal, user, password):
        self.dir_apuracao       = dir_apuracao
        self.periodo_apuracao   = periodo_apuracao
        self.portal             = portal
        self.user               = user
        self.password           = password 
    def connect_db(self):
        logger.info('connecting to db')
        result_db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        conn = sqlite3.connect(result_db)
        return conn
    
    def generate_payload(self, openincs_df):
        data = {
            'period': self.periodo_apuracao
        ,   'incidents': []            
        }
        for row in openincs_df.itertuples():
            openinc = {
                'incident_id'       : row.incident_id
            ,   'parent_id'         : row.parent_id
            ,   'group'             : row.group_
            ,   'category'          : row.category
            ,   'pending'           : row.pending == 'Y'
            ,   'created_at'        : row.created_at
            ,   'last_action'       : row.last_action
            ,   'last_action_date'  : row.last_action_date
            ,   'handler_name'      : ('N/A' if not row.handler_name else row.handler_name)
            ,   'client'            : row.client
            ,   'client_name'       : row.client_name
            ,   'orgunit'           : row.orgunit
            ,   'duration_m'        : row.duration_m
            ,   'pending_m'         : row.pending_m
            ,   'aging'             : row.aging
            ,   'aging_n4'          : row.aging_n4
            ,   'aging_last_action' : row.aging_last_action
            }
            data[ 'incidents' ].append(openinc)
        return data
    
    def logon(self):
        logger.info('logging on to %s with user %s', self.portal, self.user)
        url = f'{self.portal}/security/logonUser'
        payload = { 'user': self.user, 'password': self.password }
        r = requests.post(url, json=payload)
        response_payload = r.json()
        if not response_payload[ 'result' ]:
            logger.error('could not connect to the portal')
            logger.error(f'code : { response_payload[ "status" ][ "code" ] }')
            logger.error(f'type : { response_payload[ "status" ][ "type" ] }')
            logger.error(f'msg  : { response_payload[ "status" ][ "msg" ]  }')
            sys.exit(1)
        token = response_payload[ 'result' ][ 'token' ]
        logger.info(f'logged on successfully. token {token} received')
        return token 

    def load_openincs(self, token, payload):
        logger.info('loading open incidents to %s', self.portal)
        url = f'{self.portal}/measurement/loadOpenIncidents'
        headers = {'X-N4SAP-SECURITY-TOKEN': token}
        r = requests.post(url, headers=headers, json=payload)
        response_payload = r.json()
        if not response_payload[ 'result' ]:
            logger.error('could load incidents from the portal')
            logger.error(f'code : { response_payload[ "status" ][ "code" ] }')
            logger.error(f'type : { response_payload[ "status" ][ "type" ] }')
            logger.error(f'msg  : { response_payload[ "status" ][ "msg" ]  }')
            sys.exit(1)
        else:
            logger.info('incidents loaded')
            logger.info(f'code : { response_payload[ "status" ][ "code" ] }')
            logger.info(f'type : { response_payload[ "status" ][ "type" ] }')
            logger.info(f'msg  : { response_payload[ "status" ][ "msg" ]  }')
        
        logger.info(f'incidents loaded su')
        return token 
        
    def logoff(self, token):
        logger.info('logging off from %s with user %s', self.portal, self.user)
        url = f'{self.portal}/security/logoffUser'
        payload = { 'token': token }
        headers = {'X-N4SAP-SECURITY-TOKEN': token}
        r = requests.post(url, headers=headers, json=payload)
        response_payload = r.json()
        if not response_payload[ 'result' ]:
            logger.error('could logoff from the portal')
            logger.error(f'error code: { response_payload[ "status" ][ "code" ] }')
            logger.error(f'error code: { response_payload[ "status" ][ "type" ] }')
            logger.error(f'error code: { response_payload[ "status" ][ "msg" ]  }')
            sys.exit(1)
        logger.info(f'logged on successfully. token {token} disposed')
        return token 
                     
    def run(self):
        try:
            logger.info('starting to load aging dashboard - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            r = repo.RepoN4(conn)
            logger.info('fetching dashboard data')
            openincs_df = r.get_aging_dashboard_data()
            payload = self.generate_payload(openincs_df)
            try:
                token = self.logon()
                self.load_openincs(token, payload)                
            finally:
                self.logoff(token)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    parser.add_argument('periodo_apuracao', type=str, help='período de apuração')
    parser.add_argument('portal', type=str, help='endereço portal')
    parser.add_argument('user', type=str, help='usuário portal')
    parser.add_argument('password', type=str, help='senha portal')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.periodo_apuracao, args.portal, args.user, args.password)
    app.run()
    
