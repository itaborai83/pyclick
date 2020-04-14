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
import sqlite3

import pyclick.util as util
import pyclick.config as config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('consolida_planilhao')

SQL_CARGA_REL_MEDICAO = util.get_query("CARGA_REL_MEDICAO")
SQL_CHECK_IMPORTACAO = util.get_query("SQL_CHECK_IMPORTACAO")

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao, dir_import, start_date, end_date, datafix, dropflat):
        self.dir_apuracao       = dir_apuracao
        self.dir_import         = dir_import
        self.start_date         = start_date
        self.end_date           = end_date
        self.cutoff_date        = util.next_date(end_date)
        self.datafix            = datafix
        self.dropflat           = dropflat
            
    def read_dump(self, dump_file):
        filename = os.path.join(self.dir_import, dump_file)
        logger.info('lendo arquivo %s', filename)
        conn = sqlite3.connect(filename)
        sql = "SELECT * FROM " + config.INCIDENT_TABLE
        df = pd.read_sql(sql, conn)
        util.sort_rel_medicao(df)
        return df
    
    def concat_planilhas(self, df_open , dfs_closed):
        logger.info('concatenando planilhão')
        df_closed = pd.concat(dfs_closed)
        self.drop_duplicated_actions(df_closed)        
        df_planilhao = pd.concat([ df_closed, df_open ])
        return df_planilhao
        
    def drop_duplicated_actions(self, df):
        logger.info('dropando ações duplicadas (Comparando status_de_evento)')
        statuses = set(df.status_de_evento.to_list())
        assert 'Resolvido' in statuses
        assert 'Fechado' in statuses
        assert len(statuses) == 2
        df.sort_values(by=[ 'id_acao', 'status_de_evento' ], inplace=True, kind='mergesort', ignore_index=True)
        # keep Resolvido if it exists
        df.drop_duplicates(subset=[ 'id_acao' ], keep='first', inplace=True, ignore_index=True)
    
    def apply_cutoff_date_closed(self, df):
        logger.info('filtrando eventos encerrados após a data de corte %s', self.cutoff_date)
        df = df[ df.data_resolucao_chamado < self.cutoff_date ]
        return df.copy()

    def apply_cutoff_date_open(self, df):
        logger.info('filtrando eventos abertos após a data de corte %s', self.cutoff_date)
        df = df[ df.data_abertura_chamado < self.cutoff_date ]
        return df.copy()
        
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
    
    def read_ofertas(self):
        logger.info('recuperando a listagem de ofertas de serviços') # Assistente de Relatórios > Catálogo de Serviços > Criar Relatório (Catálogo Completo e Prazos)
        currdir = os.getcwd()
        try:
            os.chdir(self.dir_apuracao)
            df = pd.read_excel(config.OFFERINGS_SPREADSHEET)
            data = {
                'oferta' : df[ 'Oferta' ],
                'prazo' : df[ 'Prazo' ].mul(60)
            }
            return pd.DataFrame(data)
        finally:
            os.chdir(currdir)
    
    def add_dados_oferta(self, df, df_ofertas):
        logger.info('adicionando dados da oferta')
        ofertas_mapping = df_ofertas.groupby('oferta').prazo.last().to_dict()
        ofertas = df.oferta_catalogo.to_list()
        prazo_oferta = [ ofertas_mapping.get(oferta, None) for oferta in ofertas ]
        df.insert(len(df.columns), "prazo_oferta_m", prazo_oferta)
        return df
        
    def get_dump_files(self):
        logger.info("retrieving daily dump files of closed incidents")
        currdir = os.getcwd()
        os.chdir(self.dir_import)
        try:
            closed_start_file = config.IMPORT_CLOSED_MASK.format(self.start_date) 
            closed_end_file = config.IMPORT_CLOSED_MASK.format(self.end_date) 
            all_closed_files = sorted(glob.iglob(config.IMPORT_CLOSED_GLOB))
            closed_files = list([ f for f in all_closed_files if closed_start_file <= f <= closed_end_file ])
            open_file = config.IMPORT_OPEN_MASK.format(self.end_date)
            return closed_files, open_file
        finally:
            os.chdir(currdir)
    
    def process_begin_sql(self, conn):
        if not os.path.exists(config.BEGIN_SQL):
            return
        logger.warning('running BEGIN HOOK SQL SCRIPT')
        sql = open(config.BEGIN_SQL).read()
        conn.executescript(sql)
            
    def process_before_load_sql(self, conn):
        if not os.path.exists(config.BEFORE_LOAD_SQL):
            return
        logger.warning('running BEFORE LOAD HOOK SQL SCRIPT')
        sql = open(config.BEFORE_LOAD_SQL).read()
        conn.executescript(sql)
            
    def process_after_load_sql(self, conn):        
        if not os.path.exists(config.AFTER_LOAD_SQL):
            return
        logger.warning('running AFTER LOAD HOOK SQL SCRIPT')
        sql = open(config.AFTER_LOAD_SQL).read()
        conn.executescript(sql)
            
    def process_end_sql(self, conn):
        if not os.path.exists(config.END_SQL):
            return
        logger.warning('running END HOOK SQL SCRIPT')
        sql = open(config.END_SQL).read()
        conn.executescript(sql)
    
    def save_consolidado(self, df):
        logger.info('salvando planilhão como %s', config.CONSOLIDATED_DB)
        currdir = os.getcwd()
        os.chdir(self.dir_apuracao)
        try:
            if os.path.exists(config.CONSOLIDATED_DB):
                logger.warning("removing older version of the consolidated database")
                os.unlink(config.CONSOLIDATED_DB)
            conn = sqlite3.connect(config.CONSOLIDATED_DB)
            self.process_begin_sql(conn)
            df.to_sql(config.INCIDENT_TABLE, conn, index=False, if_exists="replace")
            conn.commit()
            if self.datafix:
                logger.warning("STOPING LOADING PROCEDURE FOR A DATAFIX TO BE APPLIED")
                conn.close()
                while True:
                    ans = input('type "ok" to continue or ctrl-c to abort > ').strip()
                    if ans == "ok":
                        conn = sqlite3.connect(config.CONSOLIDATED_DB)
                        break
            self.process_before_load_sql(conn)
            logger.info("loading data model")
            conn.executescript(SQL_CARGA_REL_MEDICAO)
            cursor = conn.execute(SQL_CHECK_IMPORTACAO)
            self.process_after_load_sql(conn)
            logger.info("running sanity check")
            result = cursor.fetchone()[ 0 ]
            if result != "OK":
                logger.error("falha na checagem da consolidação do relatório de medição")
                sys.exit(config.EXIT_CONSOLIDATION_ERROR)
            if self.dropflat:
                logger.warning("dropping flat data tabel -> %s", config.INCIDENT_TABLE)
                conn.execute("DROP TABLE " + config.INCIDENT_TABLE)
            conn.execute("VACUUM")
            self.process_end_sql(conn)
            conn.commit()
            conn.close()
        finally:
            os.chdir(currdir)
    
    def run(self):
        try:
            logger.info('começando a consolidação do planilhão - versão %d.%d.%d', *self.VERSION)
            mesas = self.read_mesas()
            df_ofertas = self.read_ofertas()
            mesa_evt_mapping = {}
            closed_dumps, open_dump = self.get_dump_files()
            df_open = self.read_dump(open_dump)
            df_open = self.apply_cutoff_date_open(df_open)
            self.update_event_mapping(mesa_evt_mapping, df_open)
            dfs_closed = [ ]
            logger.info('iniciando loop de parsing')
            for closed_dump in closed_dumps:
                logger.info('processsando %s', closed_dump)
                df = self.read_dump(closed_dump)
                df = self.apply_cutoff_date_closed(df)
                df = self.add_dados_oferta(df, df_ofertas)
                self.update_event_mapping(mesa_evt_mapping, df)
                dfs_closed.append(df)
            
            logger.info('concatenando planilhão')
            df_planilhao = self.concat_planilhas(df_open, dfs_closed)
            del dfs_closed # release memory
            del df_open # release memory
            
            logger.info('ordenando planilhão')
            util.sort_rel_medicao(df_planilhao)
                        
            #logger.info('relatório consolidado')
            #df = df_planilhao[ df_planilhao.ultima_acao_nome.isin(['Atribuir ao Fornecedor', 'Resolver', 'Encerrar']) ]
            #currdir = os.getcwd()
            #os.chdir(util.get_consolidated_dir(self.dir_apuracao))
            #df.to_excel("consolidado_gustavo.xlsx", index=False)
            #os.chdir(currdir)
            #del df
            
            logger.info('iniciando loop de particionamento')
            all_events = set()
            for mesa, events in sorted(mesa_evt_mapping.items()):
                if mesa in mesas:
                    logger.info('particionando mesa %s com %d eventos', mesa, len(events))
                    all_events.update(events)
            logger.info("consolidando planilhão com %d eventos", len(all_events))
            df = df_planilhao[ df_planilhao.id_chamado.isin(all_events) ]
            logger.info("consolidando planilhão com %d linhas", len(df))
            self.save_consolidado(df)
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    parser.add_argument('dir_import', type=str, help='diretório de importação')
    parser.add_argument('start_date', type=str, help='data inicio apuração')
    parser.add_argument('end_date', type=str, help='data fim apuração')
    parser.add_argument('--datafix', action='store_true', default=False, help='interrompe o processo de carga para manipular o consolidado')
    parser.add_argument('--dropflat', action='store_true', default=False, help='dropa a tabela rel_medicao após carga')
    
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.dir_import, args.start_date, args.end_date, args.datafix, args.dropflat)
    app.run()
    