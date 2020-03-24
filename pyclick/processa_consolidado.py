import os
import shutil
import argparse
import sys
import pandas as pd
import sqlite3
import logging

import pyclick.util as util
import pyclick.config as config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('processa_consolidado')

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, arq_planilhao, arq_processado, db_medicao):
        assert db_medicao.endswith(".db")
        self.arq_planilhao  = arq_planilhao
        self.arq_processado = arq_processado
        self.db_medicao     = db_medicao
        
    def read_excel(self):
        logger.info('reading excel file %s', self.arq_planilhao)
        df = pd.read_excel(self.arq_planilhao, verbose=False)
        headers = df.columns.to_list()
        if headers != config.RENAMED_COLUMNS:
            util.report_file_mismatch(logger, headers, config.RENAMED_COLUMNS)
            sys.exit(config.EXIT_FILE_MISMATCH)
        return df
            
    def drop_internal_demands(self, df):
        (rows, cols) = df[ df.categoria_maior == "Demandas Internas" ].shape
        logger.info('dropping internal demands - %d rows', rows)
        return df[ df.categoria_maior != "Demandas Internas" ]

    def drop_open_events(self, df):
        (rows, cols) = df[ df.status_de_evento == "Aberto" ].shape
        logger.info('dropping open events - %d rows', rows) 
        return df[ df.status_de_evento != "Aberto" ]

    def drop_tasks_with_no_parents(self, df):
        (rows, cols) = df[ (df.categoria_maior == "Tarefa") & (df.chamado_pai.isna()) ].shape
        logger.info('dropping tasks with no parents - %d rows', rows) 
        return df[ ~((df.categoria_maior == "Tarefa") & (df.chamado_pai.isna())) ]
    
    def extract_services(self, df):
        logger.info('extracting services/tasks')
        df_services = df[ df.categoria_maior == "Solicitações de Serviço" ]
        df_tasks    = df[ df.categoria_maior == "Tarefa" ]
        df_others   = df[ df.categoria_maior == "Incidentes" ]
        return df_services, df_tasks, df_others
    
    def split_corrections_from_user_instructions(self, df_others):
        logger.info('matching service requests to their tasks and vice versa')
        df_corrections = df_others[ df_others.categoria.isin(config.CORRECTION_CATEGORIES) ]
        df_user_instructions = df_others[ ~(df_others.categoria.isin(config.CORRECTION_CATEGORIES)) ]
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
        mesas_invalidas = config.MESAS_INVALIDAS.union( 
            set( [ 'N4-SAP-SUSTENTACAO-PRIORIDADE', 'N4-SAP-SUSTENTACAO-ESCALADOS' ] )
        )
        df_validas = df[ ~(df.mesa.isin(mesas_invalidas)) ]
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
            elif value in set(config.MESAS_TEMPORIZADAS):
                return 1
            else:
                return 0
        df_validas = df[ ~(df.mesa.isin(config.MESAS_INVALIDAS)) ]
        last_mesas_mapping = df_validas.groupby('id_chamado').mesa.last().to_dict()
        id_chamados = df.id_chamado.to_list()
        pesos = [ compute_peso(last_mesas_mapping.get(id_chamado, None)) for id_chamado in id_chamados ]
        df.insert(len(df.columns), "peso", pesos)      
        return df  
        
    def sum_durations(self, df):
        df_durations = df[ df.mesa.isin(config.MESAS_TEMPORIZADAS) ]
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
        logger.info('saving dataframe as %s', self.arq_processado)
        df.to_excel(self.arq_processado, index=False)
        logger.info('exporting to SQLITE3 as %s', self.db_medicao)
        conn = sqlite3.connect(self.db_medicao)
        df.to_sql("rel_medicao_stg", conn, index=False, if_exists="replace")
        
    def run(self):
        try:
            logger.info('starting planilhao loader - version %d.%d.%d', *self.VERSION)
            df = self.read_excel()
            df = self.drop_internal_demands(df)
            df_original = df
            df = self.drop_open_events(df)
            df = self.drop_tasks_with_no_parents(df)
            df_services, df_tasks, df_others = self.extract_services(df)
            df_services, df_tasks = self.match_services_tasks(df_services, df_tasks)
            df_corrections, df_user_instructions = self.split_corrections_from_user_instructions(df_others)
            df = self.consolidate_dfs(df_services, df_tasks, df_corrections, df_user_instructions)
            df = self.fill_last_mesa(df)
            df = self.fill_peso(df)
            df = self.sum_durations(df)
            df = self.fill_sla(df)
            self.save_df(df)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('arq_planilhao', type=str, help='arquivo planilhao')
    parser.add_argument('arq_processado', type=str, help='arquivo planilhao processado')
    parser.add_argument('db_medicao', type=str, help='nome base sqlite3 para exportação')
    args = parser.parse_args()
    app = App(args.arq_planilhao, args.arq_processado, args.db_medicao)
    app.run()