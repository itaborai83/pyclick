# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import glob
import argparse
import logging
import datetime as dt
import pandas as pd

import pyclick.util as util
import pyclick.config as config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('consolida_planilhao')

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao, cutoff_date):
        self.dir_apuracao   = dir_apuracao
        self.cutoff_date    = cutoff_date

    def drop_unnanmed_columns(self, df):
        headers = df.columns.to_list()
        col_count = len(config.EXPECTED_COLUMNS)
        header_count = len(headers)
        if header_count <= col_count:
            return
        extra_headers = headers[ col_count : ]
        for extra_header in extra_headers:
            logger.warning('dropando coluna extra: %s', extra_header)
            del df[ extra_header ]
        
    
    def find_separator(self, filename):
        with open(filename, encoding='latin-1') as fh:
            headers_txt = fh.readline()
            fields1 = headers_txt.split(',')
            fields2 = headers_txt.split(';')
            return ',' if len(fields1) > len(fields2) else ';'
        
    def read_csv(self, arq_planilha):
        path = self.get_dir_planilhas()
        filename = os.path.join(path, arq_planilha)
        logger.info('lendo arquivo %s', filename)
        sep = self.find_separator(filename)
        df = pd.read_csv(
            filename, 
            sep             = sep,
            verbose         = True,
            header          = 0, 
            encoding        = "latin_1",
            error_bad_lines = True, 
            warn_bad_lines  = True,
            low_memory      = False
        )
        self.drop_unnanmed_columns(df)
        headers = df.columns.to_list()
        if headers != config.EXPECTED_COLUMNS:
            util.report_file_mismatch(logger, headers, config.EXPECTED_COLUMNS)
            sys.exit(config.EXIT_FILE_MISMATCH)
        return df

    def read_excel(self, arq_planilha):
        filename = os.path.join(self.dir_planilhao, arq_planilha)
        logger.info('lendo arquivo %s', filename)
        df = pd.read_excel(filename, verbose=False)
        self.drop_unnanmed_columns(df)
        headers = df.columns.to_list()
        if headers != config.EXPECTED_COLUMNS:
            util.report_file_mismatch(logger, headers, config.EXPECTED_COLUMNS)
            sys.exit(config.EXIT_FILE_MISMATCH)
        return df
    
    def concat_planilhas(self, dfs):
        logger.info('concatenando planilhão - versão %d.%d.%d', *self.VERSION)
        df_planilhao = pd.concat(dfs)
        return df_planilhao
    
    def rename_columns(self, df_original):
        logger.debug('renomeando columns')
        df_renamed = df_original.rename(mapper=config.COLUMN_MAPPING, axis='columns')
        headers = df_renamed.columns.to_list()
        if headers != config.RENAMED_COLUMNS:
            logger.info('renamed columns mismatch ')
            self.report_file_mismatch(headers, config.RENAMED_COLUMNS)
            sys.exit(config.EXIT_RENAMED_MISMATCH)
        return df_renamed

    def drop_columns(self, df_renamed):
        logger.debug('dropando colunas')
        for col in config.DROP_COLUMNS:
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
        return
        substs = {
            '\t': '<<TAB>>',
            '\r\n': '<<ENTER>>',
            '\n': '<<ENTER>>',
        }
        df.replace(substs, regex=True, inplace=True)
    
    def apply_cutoff_date(self, df):
        logger.info('filtrando eventos encerrados após a data de corte %s', self.cutoff_date)
        return df[ df.data_resolucao_chamado < self.cutoff_date ]
    
    def save_planilhao(self, df):
        logger.info('salvando planilhão')
        currdir = os.getcwd()
        os.chdir(self.get_output_dir())
        df.to_excel("consolidado_periodo.xlsx", index=False)
        os.chdir(currdir)

    def save_planilha_mesa(self, df, mesa):
        orig_mesa = mesa
        mesa = mesa.replace("/", "_").\
                    replace("\\", "_").\
                    replace(":", "_").\
                    replace("*", "_").\
                    replace("[", "_").\
                    replace("]", "_").\
                    replace(" ", "_")
        currdir = os.getcwd()
        os.chdir(self.get_output_dir())
        try:
            df.to_excel("MESA_" + mesa + ".xlsx", index=False)
            os.chdir(currdir)
        except:
            logger.exception("could not export mesa %s !!! ... skipping", orig_mesa)
            os.chdir(currdir)
    
    def get_dir_planilhas(self):
        return os.path.join(self.dir_apuracao, config.INPUT_DIR)

    def get_output_dir(self):
        return os.path.join(self.dir_apuracao, config.CONSOLIDATED_DIR)
        
    def read_planilhas(self):
        logger.info('listando arquivos do planilhao')
        currdir = os.getcwd()
        try:
            path = self.get_dir_planilhas()
            os.chdir(path)
            arquivos = list(sorted(glob.iglob(config.INPUT_FILES_GLOB)))      
            os.chdir(currdir)
            return arquivos
        finally:
            os.chdir(currdir)
            
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
        os.chdir(self.get_output_dir())
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
                df = self.read_csv(arq_planilha)
                df = self.rename_columns(df)
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
            os.chdir(self.get_output_dir())
            df.to_excel("consolidado_gustavo.xlsx", index=False)
            os.chdir(currdir)
            del df
            
            logger.info('iniciando loop de particionamento')
            for mesa, eventos in sorted(mesa_evt_mapping.items()):
                if mesa in config.MESAS_TEMPORIZADAS:
                    logger.info('particionando mesa %s', mesa)
                    df = df_planilhao[ df_planilhao.id_chamado.isin(eventos) ]
                    self.save_planilha_mesa(df, mesa)
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    parser.add_argument('cutoff_date', type=str, help='data de corte encerramento evento')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.cutoff_date)
    app.run()