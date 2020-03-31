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
    
    def __init__(self, dir_apuracao, dir_import, start_date, end_date):
        self.dir_apuracao   = dir_apuracao
        self.dir_import     = dir_import
        self.start_date     = start_date
        self.end_date       = end_date
                
    def read_csv(self, arq_planilha):
        path = util.get_input_dir(self.dir_apuracao)
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
        if self.check_row_splits(df):
            logger.error('file has row splits')
            sys.exit(config.EXIT_SPLIT_ROW)
        return df
    
    def concat_planilhas(self, dfs):
        logger.info('concatenando planilhão - versão %d.%d.%d', *self.VERSION)
        df_planilhao = pd.concat(dfs)
        self.drop_duplicated_actions(df_planilhao)        
        return df_planilhao
        
    def drop_duplicated_actions(self, df):
        logger.info('dropando ações duplidadas (Comparando status_de_evento)')
        statuses = set(df.status_de_evento.to_list())
        assert 'Resolvido' in statuses
        assert 'Fechado' in statuses
        assert len(statuses) == 2
        df.sort_values(by=[ 'id_acao', 'status_de_evento' ], inplace=True, kind='mergesort', ignore_index=True)
        # keep Resolvido if it exists
        df.drop_duplicates(subset=[ 'id_acao' ], keep='first', inplace=True, ignore_index=True)
    
    def apply_cutoff_date(self, df_open, df_closed):
        logger.info('filtrando eventos encerrados após a data de corte %s', self.cutoff_date)
        df_open = df_open[ df_open.data_abertura_chamado < self.cutoff_date ]
        df_closed = df_closed[ df_closed.data_resolucao_chamado < self.cutoff_date ]
        return df_open, df_closed
    
    def save_planilhao(self, df):
        logger.info('salvando planilhão')
        currdir = os.getcwd()
        os.chdir(util.get_consolidated_dir(self.dir_apuracao))
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
        os.chdir(util.get_consolidated_dir(self.dir_apuracao))
        try:
            df.to_excel("MESA_" + mesa + ".xlsx", index=False)
            os.chdir(currdir)
        except:
            logger.exception("could not export mesa %s !!! ... skipping", orig_mesa)
            os.chdir(currdir)
            
    def read_planilhas(self):
        logger.info('listando arquivos do planilhao')
        currdir = os.getcwd()
        try:
            path = util.get_input_dir(self.dir_apuracao)
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
        os.chdir(util.get_consolidated_dir(self.dir_apuracao))
        with open("mapa_mesa_evento.tsv", "w") as fh:
            print("mesa", "evento", sep='\t', file=fh)
            for mesa, eventos in sorted(mesa_evt_mapping.items()):
                for evento in eventos:
                    print(mesa, evento, sep='\t', file=fh)
        os.chdir(currdir)
        
    def read_mesas(self):
        logger.info('recuperando a listagem de mesas para apuração')
        return util.read_mesas(self.dir_apuracao)
        
    def run(self):
        try:
            logger.info('começando a consolidação do planilhão - versão %d.%d.%d', *self.VERSION)
            mesas = self.read_mesas()
            print(mesas)
            """
            dfs_in = []
            mesa_evt_mapping = {}
            logger.info('iniciando loop de parsing')
            df_open_acc = None
            for arq_planilha in arq_planilhas:
                logger.info('processsando planilha %s', arq_planilha)
                df = self.read_csv(arq_planilha)
                df = self.rename_columns(df)
                self.replace_tabs_enters(df)
                self.process_ids(df)                
                df_open, df_closed = self.split_open_events(df)
                df_open, df_closed = self.apply_cutoff_date(df_open, df_closed)
                if df_open_acc is None:
                    df_open_acc = pd.DataFrame(columns=df.columns)                
                df_open_acc = self.update_open_acc(df_open_acc, df_open, df_closed)
                self.update_event_mapping(mesa_evt_mapping, df_closed)
                #self.update_event_mapping(mesa_evt_mapping, df_open)
                dfs_in.append(df_closed)
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
            os.chdir(util.get_consolidated_dir(self.dir_apuracao))
            df.to_excel("consolidado_gustavo.xlsx", index=False)
            os.chdir(currdir)
            del df
            
            logger.info('iniciando loop de particionamento')
            for mesa, eventos in sorted(mesa_evt_mapping.items()):
                if mesa in config.MESAS_TEMPORIZADAS:
                    logger.info('particionando mesa %s', mesa)
                    df = df_planilhao[ df_planilhao.id_chamado.isin(eventos) ]
                    self.save_planilha_mesa(df, mesa)
            """
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    parser.add_argument('dir_import', type=str, help='diretório de importação')
    parser.add_argument('start_date', type=str, help='data inicio apuração')
    parser.add_argument('end_date', type=str, help='data fim apuração')
    
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.dir_import, args.start_date, args.end_date)
    app.run()