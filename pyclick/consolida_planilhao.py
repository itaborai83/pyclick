import sys
import os
import os.path
import glob
import argparse
import logging
import datetime as dt
import pandas as pd

import pyclick.util as util


logger = util.get_logger('loader_planilhao')

EXIT_FILE_MISMATCH      = 1
EXIT_RENAMED_MISMATCH   = 2

EXPECTED_COLUMNS = [
    'Data Abertura Chamado',
    'Data Resolução Chamado',
    'ID Chamado',
    'Chamado Pai',
    'Origem Chamado',
    'Usuário Afetado',
    'Nome do Usuário Afetado',
    'Usuário Informante',
    'Nome do Usuário Informante',
    'Organização Cliente',
    'Departamento Cliente',
    'Estado',
    'Site',
    'FCR',
    'Status de evento',
    'Categoria Maior',
    'Resumo',
    'Descrição Detalhada',
    'Serviço Catálogo',
    'Classe de Produto de Serviço',
    'Produto de Serviço',
    'Item de Serviço',
    'Categoria',
    'Oferta Catálogo',
    'Classe Genérica B',
    'Classe de Produto B',
    'Produto B',
    'Fabricante B',
    'Item Modelo B',
    'Item B',
    'Categoria Causa',
    'Classe Genérica Causa',
    'Classe de Produto Causa',
    'Produto Causa',
    'Fabricante Causa',
    'Item Modelo Causa',
    'Item Causa',
    'Resolução',
    'ID Ação',
    'Data Inicio Ação',
    'Ultima Ação',
    'Data Fim Ação',
    'Tempo Total da Ação (h)',
    'Tempo Total da Ação (M)',
    'Ultima Ação Nome',
    'Motivo Pendencia',
    'Campos alterados',
    'Itens alterados',
    'Nome do CA',
    'Contrato',
    'Mesa',
    'Designado',
    'Grupo Default',
    'Prioridade do CA',
    'Descrição da Prioridade do CA',
    'Prazo Prioridade ANS (m)',
    'Prazo Prioridade ANS (h)',
    'Prazo Prioridade ANO (m)',
    'Prazo Prioridade ANO (h)',
    'Prazo Prioridade CA (m)',
    'Prazo Prioridade CA (h)',
    'Tempo Total Evento (m)',
    'Tempo Total Evento (h)',
    'Tempo Util Evento (m)',
    'Tempo Util Evento (h)',
    'Tempo Util Atribuição Mesa (m)',
    'Tempo Util Atribuição Mesa (h)',
    'Tempo Util Atribuição CA (m)',
    'Tempo Util Atribuição CA (h)',
    'Vinculo',
    'Vinculo com Incidente Grave?',
    'Incidente Grave?',
]
   
COLUMN_MAPPING = {
    'Data Abertura Chamado':            'data_abertura_chamado',
    'Data Resolução Chamado':           'data_resolucao_chamado',
    'ID Chamado':                       'id_chamado',
    'Chamado Pai':                      'chamado_pai',
    'Origem Chamado':                   'origem_chamado',
    'Usuário Afetado':                  'usuario_afetado',
    'Nome do Usuário Afetado':          'nome_do_usuario_afetado',
    'Usuário Informante':               'usuario_informante',
    'Nome do Usuário Informante':       'nome_do_usuario_informante',
    'Organização Cliente':              'organizacao_cliente',
    'Departamento Cliente':             'departamento_cliente',
    'Estado':                           'estado',
    'Site':                             'site',
    'FCR':                              'fcr',
    'Status de evento':                 'status_de_evento',
    'Categoria Maior':                  'categoria_maior',
    'Resumo':                           'resumo',
    'Descrição Detalhada':              'descricao_detalhada',
    'Serviço Catálogo':                 'servico_catalogo',
    'Classe de Produto de Serviço':     'classe_de_produto_de_servico',
    'Produto de Serviço':               'produto_de_servico',
    'Item de Serviço':                  'item_de_servico',
    'Categoria':                        'categoria',
    'Oferta Catálogo':                  'oferta_catalogo',
    'Classe Genérica B':                'classe_generica_b',
    'Classe de Produto B':              'classe_de_produto_b',
    'Produto B':                        'produto_b',
    'Fabricante B':                     'fabricante_b',
    'Item Modelo B':                    'item_modelo_b',
    'Item B':                           'item_b',
    'Categoria Causa':                  'categoria_causa',
    'Classe Genérica Causa':            'classe_generica_causa',
    'Classe de Produto Causa':          'classe_de_produto_causa',
    'Produto Causa':                    'produto_causa',
    'Fabricante Causa':                 'fabricante_causa',
    'Item Modelo Causa':                'item_modelo_causa',
    'Item Causa':                       'item_causa',
    'Resolução':                        'resolucao',
    'ID Ação':                          'id_acao',
    'Data Inicio Ação':                 'data_inicio_acao',
    'Ultima Ação':                      'ultima_acao',
    'Data Fim Ação':                    'data_fim_acao',
    'Tempo Total da Ação (h)':          'tempo_total_da_acao_h',
    'Tempo Total da Ação (M)':          'tempo_total_da_acao_m',
    'Ultima Ação Nome':                 'ultima_acao_nome',
    'Motivo Pendencia':                 'motivo_pendencia',
    'Campos alterados':                 'campos_alterados',
    'Itens alterados':                  'itens_alterados',
    'Nome do CA':                       'nome_do_ca',
    'Contrato':                         'contrato',
    'Mesa':                             'mesa',
    'Designado':                        'designado',
    'Grupo Default':                    'grupo_default',
    'Prioridade do CA':                 'prioridade_do_ca',
    'Descrição da Prioridade do CA':    'descricao_da_prioridade_do_ca',
    'Prazo Prioridade ANS (m)':         'prazo_prioridade_ans_m',
    'Prazo Prioridade ANS (h)':         'prazo_prioridade_ans_h',
    'Prazo Prioridade ANO (m)':         'prazo_prioridade_ano_m',
    'Prazo Prioridade ANO (h)':         'prazo_prioridade_ano_h',
    'Prazo Prioridade CA (m)':          'prazo_prioridade_ca_m',
    'Prazo Prioridade CA (h)':          'prazo_prioridade_ca_h',
    'Tempo Total Evento (m)':           'tempo_total_evento_m',
    'Tempo Total Evento (h)':           'tempo_total_evento_h',
    'Tempo Util Evento (m)':            'tempo_util_evento_m',
    'Tempo Util Evento (h)':            'tempo_util_evento_h',
    'Tempo Util Atribuição Mesa (m)':   'tempo_util_atribuicao_mesa_m',
    'Tempo Util Atribuição Mesa (h)':   'tempo_util_atribuicao_mesa_h',
    'Tempo Util Atribuição CA (m)':     'tempo_util_atribuicao_ca_m',
    'Tempo Util Atribuição CA (h)':     'tempo_util_atribuicao_ca_h',
    'Vinculo':                          'vinculo',
    'Vinculo com Incidente Grave?':     'vinculo_com_incidente_grave',
    'Incidente Grave?':                 'incidente_grave',
}

RENAMED_COLUMNS = list([ COLUMN_MAPPING[ col ] for col in EXPECTED_COLUMNS ])

KEEP_COLUMNS = [ 
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

DROP_COLUMNS = list([ col for col in set(RENAMED_COLUMNS) if col not in KEEP_COLUMNS ])

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_planilhao, dir_saida, cutoff_date):
        self.dir_planilhao  = dir_planilhao
        self.dir_saida      = dir_saida
        self.cutoff_date    = cutoff_date

    def report_file_mismatch(self, headers, expected_columns):
        set_expected    = set(expected_columns)
        set_actual      = set(headers)
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
    
    def drop_unnanmed_columns(self, df):
        headers = df.columns.to_list()
        col_count = len(EXPECTED_COLUMNS)
        header_count = len(headers)
        if header_count <= col_count:
            return
        extra_headers = headers[ col_count : ]
        for extra_header in extra_headers:
            logger.warning('dropando coluna extra: %s', extra_header)
            del df[ extra_header ]

    def read_excel(self, arq_planilha):
        filename = os.path.join(self.dir_planilhao, arq_planilha)
        logger.info('lendo arquivo %s', filename)
        df = pd.read_excel(filename, verbose=False)
        self.drop_unnanmed_columns(df)
        headers = df.columns.to_list()
        if headers != EXPECTED_COLUMNS:
            self.report_file_mismatch(headers, EXPECTED_COLUMNS)
            sys.exit(EXIT_FILE_MISMATCH)
        return df
    
    def concat_planilhas(self, dfs):
        logger.info('concatenando planilhão - versão %d.%d.%d', *self.VERSION)
        df_planilhao = pd.concat(dfs)
        return df_planilhao
    
    def rename_columns(self, df_original):
        logger.debug('renomeando columns')
        df_renamed = df_original.rename(mapper=COLUMN_MAPPING, axis='columns')
        headers = df_renamed.columns.to_list()
        if headers != RENAMED_COLUMNS:
            logger.info('renamed columns mismatch ')
            self.report_file_mismatch(headers, RENAMED_COLUMNS)
            sys.exit(EXIT_RENAMED_MISMATCH)
        return df_renamed

    def drop_columns(self, df_renamed):
        logger.debug('dropando colunas')
        for col in DROP_COLUMNS:
            del df_renamed[ col ]
    
    def convert_ids_to_string(self, df):
        def conv(value):
            if pd.isna(value):
                return value
            else:
                return str(value)
        df['id_chamado'] = df['id_chamado'].apply(conv)
        df['chamado_pai'] = df['chamado_pai'].apply(conv)

    def filter_out_open_events(self, df):
        logger.info('filtrado eventos ainda abertos')
        return df[ ~(df.data_resolucao_chamado.isna()) ]
    
    def replace_tabs_enters(self, df):
        logger.info('removendo tabs e enters')
        substs = {
            '\t': '<<TAB>>',
            '\n': '<<ENTER>>',
        }
        df.replace(substs, regex=True, inplace=True)
    
    def apply_cutoff_date(self, df):
        logger.info('filtrando eventos encerrados após a data de corte %s', self.cutoff_date)
        return df[ df.data_resolucao_chamado < self.cutoff_date ]
    
    def save_planilhao(self, df):
        logger.info('salvando planilhão')
        currdir = os.getcwd()
        os.chdir(self.dir_saida)
        df.to_excel("consolidado_periodo.xlsx", index=False)
        os.chdir(currdir)

    def save_planilha_mesa(self, df, mesa):
        mesa = mesa.replace("/", "_").replace("\\", "_")
        currdir = os.getcwd()
        os.chdir(self.dir_saida)
        df.to_excel("MESA - " + mesa + ".xlsx", index=False)
        os.chdir(currdir)
        
    def read_planilhas(self):
        logger.info('listando arquivos do planilhao')
        currdir = os.getcwd()
        os.chdir(self.dir_planilhao)
        arquivos = list(sorted(glob.iglob("202*.xlsx")))
        os.chdir(currdir)
        return arquivos
    
    def update_event_mapping(self, mesa_evt_mapping, df):
        logger.info('atualizando mapeamento evento mesa')
        df_mesas        = df[ ~(df.mesa.isna()) ]
        id_chamados     = df_mesas.id_chamado.to_list() # to allow ordering
        chamados_pai    = df_mesas.chamado_pai.to_list()
        mesas           = df_mesas.mesa.to_list()
        for id_chamado, chamado_pai, mesa in zip(id_chamados, chamados_pai, mesas):
            if mesa not in mesa_evt_mapping:
                mesa_evt_mapping[ mesa ] = set()
            mesa_evt_mapping[ mesa ].add(id_chamado)
            if not pd.isna(chamado_pai):
                mesa_evt_mapping[ mesa ].add(chamado_pai)
    
    def report_event_mapping(self, mesa_evt_mapping):
        currdir = os.getcwd()
        os.chdir(self.dir_saida)
        with open("mapa_mesa_evento.tsv", "w") as fh:
            print("mesa", "evento", sep='\t', file=fh)
            for mesa, eventos in sorted(mesa_evt_mapping.items()):
                for evento in eventos:
                    print(mesa, evento, sep='\t', file=fh)
        os.chdir(currdir)
    
    def run(self):
        try:
            logger.info('começando a consolidação do planilhão - versão %d.%d.%d', *self.VERSION)
            arq_planilhas = self.read_planilhas()
            dfs_in = []
            mesa_evt_mapping = {}
            dfs_out = {}
            logger.info('iniciando loop de parsing')
            for arq_planilha in arq_planilhas:
                logger.info('processsando planilha %s', arq_planilha)
                df = self.read_excel(arq_planilha)
                df = self.rename_columns(df)
                self.drop_columns(df)
                df = self.filter_out_open_events(df)
                df = self.apply_cutoff_date(df)
                self.replace_tabs_enters(df)
                self.convert_ids_to_string(df)
                self.update_event_mapping(mesa_evt_mapping, df)
                dfs_in.append(df)
            
            logger.info('concatenando planilhão')
            df_planilhao = self.concat_planilhas(dfs_in)
            del dfs_in # release memory
            
            logger.info('ordenando planilhão')
            df_planilhao.sort_values(by=[ "id_chamado", "chamado_pai", "data_inicio_acao", "id_acao" ], inplace=True, kind="mergesort", ignore_index=True)
            
            logger.info('exportando mapeamento mesa x eventos')
            self.report_event_mapping(mesa_evt_mapping)
            
            logger.info('relatório consolidado')
            df = df_planilhao[ df_planilhao.ultima_acao_nome.isin(['Atribuir ao Fornecedor', 'Resolver', 'Encerrar']) ]
            currdir = os.getcwd()
            os.chdir(self.dir_saida)
            df.to_excel("consolidado_gustavo.xlsx", index=False)
            os.chdir(currdir)
            del df
            
            logger.info('iniciando loop de particionamento')
            for mesa, eventos in sorted(mesa_evt_mapping.items()):
                logger.info('particionando mesa %s', mesa)
                df = df_planilhao[ df_planilhao.id_chamado.isin(eventos) ]
                self.save_planilha_mesa(df, mesa)
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_planilhao', type=str, help='diretorio planilhao')
    parser.add_argument('dir_saida', type=str, help='diretorio saida')
    parser.add_argument('cutoff_date', type=str, help='data de corte encerramento evento')
    args = parser.parse_args()
    app = App(args.dir_planilhao, args.dir_saida, args.cutoff_date)
    app.run()