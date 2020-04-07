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

logger = util.get_logger('processa_consolidado')

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
        self.mesas = None
        
    def read_consolidated_db(self):
        filename = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        logger.info('lendo arquivo %s', filename)
        conn = sqlite3.connect(filename)
        sql = "SELECT * FROM " + config.INCIDENT_TABLE
        df = pd.read_sql(sql, conn)
        util.sort_rel_medicao(df)
        return df
    
    def drop_internal_demands(self, df):
        rows = len(df[ df.categoria_maior == "Demandas Internas" ])
        logger.info('dropping internal demands - %d rows', rows)
        return df[ df.categoria_maior != "Demandas Internas" ]
    
    def split_open_events(self, df):
        rows = len(df[ df.status_de_evento == "Aberto" ])
        logger.info('dropping open events - %d rows', rows) 
        df_open = df[ df.status_de_evento == "Aberto" ].copy()
        df_closed = df[ df.status_de_evento != "Aberto" ].copy()
        return df_open, df_closed
    
    def drop_tasks_with_no_parents(self, df):
        rows = len(df[ (df.categoria_maior == "Tarefa") & (df.chamado_pai.isna()) ])
        logger.info('dropping tasks with no parents - %d rows', rows) 
        return df[ ~((df.categoria_maior == "Tarefa") & (df.chamado_pai.isna())) ].copy()
    
    def extract_services(self, df):
        logger.info('extracting services/tasks')
        df_services = df[ df.categoria_maior == "Solicitações de Serviço" ].copy()
        df_tasks    = df[ df.categoria_maior == "Tarefa" ].copy()
        df_others   = df[ df.categoria_maior == "Incidentes" ].copy()
        return df_services, df_tasks, df_others
    
    def split_corrections_from_user_instructions(self, df_others):
        logger.info('matching service requests to their tasks and vice versa')
        df_corrections = df_others[ df_others.categoria.isin(n4_config.CORRECTION_CATEGORIES) ].copy()
        df_user_instructions = df_others[ ~(df_others.categoria.isin(n4_config.CORRECTION_CATEGORIES)) ].copy()
        return df_corrections, df_user_instructions
        
    def match_services_tasks(self, df_services, df_tasks):
        logger.info('matching service requests to their tasks and vice versa')
        orig_serv_count = len(df_services)
        orig_task_count = len(df_tasks)
        # filter tasks by service requests
        services_ids    = df_services.id_chamado.to_list()
        df_tasks        = df_tasks[ df_tasks.chamado_pai.isin(services_ids) ]
        # filter service requests by tasks
        service_ids     = df_tasks.chamado_pai.to_list()
        df_services     = df_services[ df_services.id_chamado.isin(service_ids) ]
        # compute delta
        act_serv_count      = len(df_services)
        act_task_count      = len(df_tasks)
        delta_serv_count    = orig_serv_count - act_serv_count
        delta_task_count    = orig_task_count - act_task_count
        # report deltas
        logger.info('%d service requests rows and %d task rows dropped due to matching errors', delta_serv_count, delta_task_count)
        return df_services, df_tasks
    
    def consolidate_dfs(self, df_services, df_tasks, df_corrections, df_user_instructions):
        logger.info('concatenating data frames')
        df_services.insert(len(df_services.columns), "tipo", [ "REALIZAR" ] * df_services.shape[ 0 ])
        df_tasks.insert(len(df_tasks.columns), "tipo", [ "REALIZAR - TAREFA" ] * df_tasks.shape[ 0 ])
        df_corrections.insert(len(df_corrections.columns), "tipo", [ "CORRIGIR" ] * df_corrections.shape[ 0 ])
        df_user_instructions.insert(len(df_user_instructions.columns), "tipo", [ "ORIENTAR" ] * df_user_instructions.shape[ 0 ])
        return pd.concat([ df_corrections, df_user_instructions, df_services, df_tasks ])
    
    def fill_last_mesa(self, df):
        mesas_invalidas = n4_config.MESAS_INVALIDAS.union( 
            set( [ 'N4-SAP-SUSTENTACAO-PRIORIDADE', 'N4-SAP-SUSTENTACAO-ESCALADOS' ] )
        )
        df_validas = df[ ~((df.mesa.isin(mesas_invalidas)) | (df.mesa.isna())) ].copy()
        last_mesas_mapping = df_validas.groupby('id_chamado').mesa.last().to_dict()
        id_chamados = df.id_chamado.to_list()
        last_mesas = [ last_mesas_mapping.get(id_chamado, None) for id_chamado in id_chamados ]
        df.insert(len(df.columns), "ultima_mesa", last_mesas)      
        return df
        
    def fill_peso(self, df):
        def compute_peso(value):
            if value == 'N4-SAP-SUSTENTACAO-PRIORIDADE':
                return 35
            elif value == 'N4-SAP-SUSTENTACAO-ESCALADOS':
                return 30
            elif value in set(self.mesas):
                return 1
            else:
                return 0
        df_validas = df[ ~((df.mesa.isin(n4_config.MESAS_INVALIDAS)) | (df.mesa.isna())) ].copy()
        last_mesas_mapping = df_validas.groupby('id_chamado').mesa.last().to_dict()
        id_chamados = df.id_chamado.to_list()
        pesos = [ compute_peso(last_mesas_mapping.get(id_chamado, None)) for id_chamado in id_chamados ]
        df.insert(len(df.columns), "peso", pesos)
        return df  
        
    def sum_durations(self, df):
        df_durations = df[ df.mesa.isin(self.mesas) ]
        duration_mapping = df_durations.groupby('id_chamado').tempo_util_atribuicao_mesa_m.sum().to_dict()
        id_chamados = df.id_chamado.to_list()
        durations_mesa = [ duration_mapping.get(id_chamado, None) for id_chamado in id_chamados ]
        df.insert(len(df.columns), "soma_duracoes_chamado", durations_mesa)
        return df

    def fill_sla(self, df):
        def compute_sla(row):
            if row.peso == 0:
                return -99999999999
            elif row.tipo == 'ORIENTAR' and row.peso in (1, 30):
                return 27 * 60
            elif row.tipo == 'ORIENTAR' and row.peso == 35:
                return 9 * 60
            elif row.tipo == 'CORRIGIR' and row.peso in (1, 30):
                return 135 * 60
            elif row.tipo == 'CORRIGIR' and row.peso == 35:
                return 9 * 60
            elif row.tipo == 'REALIZAR - TAREFA':
                return 0
            elif row.tipo == 'REALIZAR' and row.peso in (1, 30, 35):
                return row.prazo_prioridade_ans_m
            else:
                logger.error('unexpected combination >> tipo \'%s\', peso \'%s\' ... exiting', row.tipo, row.peso)
                assert 1 == 2
        slas = []
        for row in df.itertuples():
            sla = compute_sla(row)
            slas.append(sla)
        df.insert(len(df.columns), "prazo", slas)
        return df
        
    def save_df(self, df):
        result_spreadsheet = os.path.join(self.dir_apuracao, n4_config.RESULT_SPREADSHEET)
        result_db = os.path.join(self.dir_apuracao, n4_config.RESULT_DB)
        logger.info('saving dataframe as %s', result_spreadsheet)
        df.to_excel(result_spreadsheet, index=False)
        logger.info('exporting to SQLITE3 as %s', result_db)
        conn = sqlite3.connect(result_db)
        df.to_sql("rel_medicao_stg", conn, index=False, if_exists="replace")
        conn.execute("VACUUM")
        
    def run(self):
        try:
            logger.info('starting planilhao loader - version %d.%d.%d', *self.VERSION)
            self.mesas = util.read_mesas(self.dir_apuracao)
            df = self.read_consolidated_db()
            df = self.drop_internal_demands(df)
            df = self.drop_tasks_with_no_parents(df)
            df_open, df_closed = self.split_open_events(df)
            # process closed
            df_services, df_tasks, df_others = self.extract_services(df_closed)
            df_services, df_tasks = self.match_services_tasks(df_services, df_tasks)
            df_corrections, df_user_instructions = self.split_corrections_from_user_instructions(df_others)
            df_closed = self.consolidate_dfs(df_services, df_tasks, df_corrections, df_user_instructions)
            df_closed = self.fill_last_mesa(df_closed)
            df_closed = self.sum_durations(df_closed)
            df_closed = self.fill_peso(df_closed)
            df_closed = self.fill_sla(df_closed)
            # process open
            df_services, df_tasks, df_others = self.extract_services(df_open)
            df_services, df_tasks = self.match_services_tasks(df_services, df_tasks)
            df_corrections, df_user_instructions = self.split_corrections_from_user_instructions(df_others)
            df_open = self.consolidate_dfs(df_services, df_tasks, df_corrections, df_user_instructions)
            df_open = self.fill_last_mesa(df_open)
            df_open = self.sum_durations(df_open)
            df_open = self.fill_peso(df_open)
            df_open = self.fill_sla(df_open)
            # concatenate and save
            self.save_df(df_closed)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.service_offerings)
    app.run()