import os
import shutil
import argparse
import sys
import pandas as pd
import sqlite3
import logging

FORMAT = '%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d\n\t%(message)s\n'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger('loader_planilhao')

EXIT_FILE_MISMATCH      = 1
EXIT_RENAMED_MISMATCH   = 2

EXPECTED_COLUMNS = [
    'data_abertura_chamado',
    'data_resolucao_chamado',
    'id_chamado',
    'chamado_pai',
    'origem_chamado',
    'usuario_afetado',
    'nome_do_usuario_afetado',
    'usuario_informante',
    'nome_do_usuario_informante',
    'organizacao_cliente',
    'departamento_cliente',
    'estado',
    'site',
    'fcr',
    'status_de_evento',
    'categoria_maior',
    'resumo',
    'descricao_detalhada',
    'servico_catalogo',
    'classe_de_produto_de_servico',
    'produto_de_servico',
    'item_de_servico',
    'categoria',
    'oferta_catalogo',
    'classe_generica_b',
    'classe_de_produto_b',
    'produto_b',
    'fabricante_b',
    'item_modelo_b',
    'item_b',
    'categoria_causa',
    'classe_generica_causa',
    'classe_de_produto_causa',
    'produto_causa',
    'fabricante_causa',
    'item_modelo_causa',
    'item_causa',
    'resolucao',
    'id_acao',
    'data_inicio_acao',
    'ultima_acao',
    'data_fim_acao',
    'tempo_total_da_acao_h',
    'tempo_total_da_acao_m',
    'ultima_acao_nome',
    'motivo_pendencia',
    'campos_alterados',
    'itens_alterados',
    'nome_do_ca',
    'contrato',
    'mesa',
    'designado',
    'grupo_default',
    'prioridade_do_ca',
    'descricao_da_prioridade_do_ca',
    'prazo_prioridade_ans_m',
    'prazo_prioridade_ans_h',
    'prazo_prioridade_ano_m',
    'prazo_prioridade_ano_h',
    'prazo_prioridade_ca_m',
    'prazo_prioridade_ca_h',
    'tempo_total_evento_m',
    'tempo_total_evento_h',
    'tempo_util_evento_m',
    'tempo_util_evento_h',
    'tempo_util_atribuicao_mesa_m',
    'tempo_util_atribuicao_mesa_h',
    'tempo_util_atribuicao_ca_m',
    'tempo_util_atribuicao_ca_h',
    'vinculo',
    'vinculo_com_incidente_grave',
    'incidente_grave'
]

KEEP_COLUMNS = [ 
    'data_abertura_chamado',
    'data_resolucao_chamado',
    'id_chamado',
    'chamado_pai',
    #'origem_chamado',
    #'usuario_afetado',
    #'nome_do_usuario_afetado',
    #'usuario_informante',
    #'nome_do_usuario_informante',
    #'organizacao_cliente',
    #'departamento_cliente',
    #'estado',
    #'site',
    #'fcr',
    'status_de_evento',
    'categoria_maior',
    #'resumo',
    #'descricao_detalhada',
    'servico_catalogo',
    'classe_de_produto_de_servico',
    #'produto_de_servico',
    #'item_de_servico',
    'categoria',
    'oferta_catalogo',
    #'classe_generica_b',
    #'classe_de_produto_b',
    'produto_b',
    #'fabricante_b',
    #'item_modelo_b',
    'item_b',
    'categoria_causa',
    #'classe_generica_causa',
    #'classe_de_produto_causa',
    'produto_causa',
    #'fabricante_causa',
    #'item_modelo_causa',
    #'item_causa',
    #'resolucao',
    'id_acao',
    'data_inicio_acao',
    'ultima_acao',
    'data_fim_acao',
    #'tempo_total_da_acao_h',
    #'tempo_total_da_acao_m',
    'ultima_acao_nome',
    #'motivo_pendencia',
    #'campos_alterados',
    #'itens_alterados',
    'nome_do_ca',
    'contrato',
    'mesa',
    'designado',
    #'grupo_default',
    'prioridade_do_ca',
    #'descricao_da_prioridade_do_ca',
    'prazo_prioridade_ans_m',
    #'prazo_prioridade_ans_h',
    'prazo_prioridade_ano_m',
    #'prazo_prioridade_ano_h',
    'prazo_prioridade_ca_m',
    #'prazo_prioridade_ca_h',
    'tempo_total_evento_m',
    #'tempo_total_evento_h',
    'tempo_util_evento_m',
    #'tempo_util_evento_h',
    'tempo_util_atribuicao_mesa_m',
    #'tempo_util_atribuicao_mesa_h',
    'tempo_util_atribuicao_ca_m',
    #'tempo_util_atribuicao_ca_h',
    'vinculo',
    'vinculo_com_incidente_grave',
    'incidente_grave'
]

DROP_COLUMNS = list([ col for col in EXPECTED_COLUMNS if col not in set(KEEP_COLUMNS) ])

MESAS_TEMPORIZADAS = set([
    'N4-SAP-SUSTENTACAO-ABAST_GE',
    'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',
    'N4-SAP-SUSTENTACAO-CORPORATIVO',
    'N4-SAP-SUSTENTACAO-ESCALADOS',
    'N4-SAP-SUSTENTACAO-FINANCAS',
    'N4-SAP-SUSTENTACAO-PRIORIDADE',
    'N4-SAP-SUSTENTACAO-SERVICOS',
    'N4-SAP-SUSTENTACAO-GRC',
    'N4-SAP-SUSTENTACAO-PORTAL'
])

MESAS_INVALIDAS = set([
    'A DEFINIR',
    'Atendimento de RH',
    'Mesa Padrão',
    'SVD Manager Template',
    'Usuários Finais',
])

CORRECTION_CATEGORIES = [
    'CORRIGIR-NÃO EMERGENCIAL',
    'CORRIGIR-PESO30',
    'CORRIGIR-PESO35',
    'CORRIGIR-SEVERIDADE1',
    'CORRIGIR-SEVERIDADE2',
    'REPARAR FALHA',
]

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, arq_planilhao, arq_processado, db_medicao):
        assert db_medicao.endswith(".db")
        self.arq_planilhao  = arq_planilhao
        self.arq_processado = arq_processado
        self.db_medicao     = db_medicao
        
    def report_file_mismatch(self, headers, expected_columns):
        set_expected    = set(expected_columns)
        set_actual      = set(headers)
        #set_common      = set_expected.intersection(set_actual)
        set_missing     = set_expected.difference(set_actual)
        set_unexpected  = set_actual.difference(set_expected)
        missing_cols    = list([ col for col in expected_columns if col in set_missing ])
        unexpected_cols = list([ col for col in headers if col in set_unexpected ])
        logger.error('the input file does not match the expected format')
        logger.error('missing columns >> %s', str(missing_cols))
        logger.error('unexpected_cols columns >> %s', str(unexpected_cols))
        for i, (c1, c2) in enumerate(zip(EXPECTED_COLUMNS, headers)):
            i += 1
            if c1 != c2:
                logger.error('column on position %d is the first mismatch >> %s != %s', i, repr(c1), repr(c2))
                break
        
    def read_excel(self):
        logger.info('reading excel file %s', self.arq_planilhao)
        df = pd.read_excel(self.arq_planilhao, verbose=False)
        headers = df.columns.to_list()
        if headers != EXPECTED_COLUMNS:
            self.report_file_mismatch(headers, EXPECTED_COLUMNS)
            sys.exit(EXIT_FILE_MISMATCH)
        return df
        
    def drop_columns(self, df_renamed):
        logger.info('dropping columns')
        for col in DROP_COLUMNS:
            del df_renamed[ col ]
        
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
        df_corrections = df_others[ df_others.categoria.isin(CORRECTION_CATEGORIES) ]
        df_user_instructions = df_others[ ~(df_others.categoria.isin(CORRECTION_CATEGORIES)) ]
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
        df_services.insert(len(df_services.columns), "tipo", [ "EXECUTAR" ] * df_services.shape[ 0 ])
        df_tasks.insert(len(df_tasks.columns), "tipo", [ "EXECUTAR - TAREFA" ] * df_tasks.shape[ 0 ])
        df_corrections.insert(len(df_corrections.columns), "tipo", [ "CORRIGIR" ] * df_corrections.shape[ 0 ])
        df_user_instructions.insert(len(df_user_instructions.columns), "tipo", [ "ORIENTAR" ] * df_user_instructions.shape[ 0 ])
        return pd.concat([ df_corrections, df_user_instructions, df_services, df_tasks ])
    
    def fill_last_mesa(self, df):
        mesas_invalidas = MESAS_INVALIDAS.union( 
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
            elif value in set(MESAS_TEMPORIZADAS):
                return 1
            else:
                return 0
        df_validas = df[ ~(df.mesa.isin(MESAS_INVALIDAS)) ]
        last_mesas_mapping = df_validas.groupby('id_chamado').mesa.last().to_dict()
        id_chamados = df.id_chamado.to_list()
        pesos = [ compute_peso(last_mesas_mapping.get(id_chamado, None)) for id_chamado in id_chamados ]
        df.insert(len(df.columns), "peso", pesos)      
        return df  
        
    def sum_durations(self, df):
        df_durations = df[ df.mesa.isin(MESAS_TEMPORIZADAS) ]
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
            elif row.tipo == 'EXECUTAR - TAREFA':
                return 0
            elif row.tipo == 'EXECUTAR' and row.peso in (1, 30, 35):
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
            self.drop_columns(df)
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