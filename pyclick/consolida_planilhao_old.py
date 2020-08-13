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

import pyclick.ranges as ranges
import pyclick.util as util
import pyclick.config as config
from pyclick.repo import Repo

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('consolida_planilhao')

SQL_REL_MEDICAO_SELECT      = util.get_query("CONSOLIDA__REL_MEDICAO_SELECT")
SQL_REL_MEDICAO_DDL         = util.get_query("CONSOLIDA__REL_MEDICAO_DDL")
SQL_REL_MEDICAO_UPSERT      = util.get_query("CONSOLIDA__REL_MEDICAO_UPSERT")
SQL_UPDATE_MESA_ATUAL       = util.get_query("CONSOLIDA__UPDATE_MESA_ATUAL")
#SQL_DROP_UNACTIONED_EVTS    = util.get_query("CONSOLIDA__DROP_UNACTIONED_EVTS")
SQL_UPDATE_USER_STATUS      = util.get_query("CONSOLIDA__UPDATE_ACAO_USER_STATUS")
#SQL_UPDATE_PENDENCIA        = util.get_query("CONSOLIDA__UPDATE_PENDENCIA")
SQL_CARGA_REL_MEDICAO       = util.get_query("CONSOLIDA__CARGA_REL_MEDICAO")
SQL_CHECK_IMPORTACAO        = util.get_query("CONSOLIDA__SQL_CHECK_IMPORTACAO")
SQL_LISTA_ACOES             = util.get_query("CONSOLIDA__LISTA_ACOES") 

WORK_DB = "__work.db"

class App(object):
    
    # FIXME: Needs a refactoring. Too much responsability being done here
    
    VERSION = (1, 0, 0)
    
    def __init__(self, dir_apuracao, dir_import, start_date, end_date, datafix):
        self.dir_apuracao       = dir_apuracao
        self.dir_import         = dir_import
        self.start_date         = start_date
        self.end_date           = util.prior_date(end_date)
        self.cutoff_date        = end_date
        self.datafix            = datafix

    def load_planilha_horarios(self):
        logger.info('carregando planilha de horários de mesas')
        fname = os.path.join(self.dir_apuracao, config.BUSINESS_HOURS_SPREADSHEET)
        if not os.path.exists(fname):
            logger.error('planilha de horários de mesas  %s não encontrado no diretório de apuração', config.BUSINESS_HOURS_SPREADSHEET)
            sys.exit(-1)
        return ranges.load_spreadsheet(fname)
        
    def read_dump(self, dump_file):
        filename = os.path.join(self.dir_import, dump_file)
        decompressed_filename = os.path.join(self.dir_apuracao, WORK_DB)
        logger.info('lendo arquivo %s', filename)
        util.decompress_to(filename, decompressed_filename)
        conn = sqlite3.connect(decompressed_filename)
        df = pd.read_sql(SQL_REL_MEDICAO_SELECT, conn)
        util.sort_rel_medicao(df)
        del conn
        os.unlink(decompressed_filename)
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
        assert (len(statuses) == 2 and 'Resolvido' in statuses and 'Fechado' in statuses) or \
               (len(statuses) == 1 and ('Resolvido' in statuses or 'Fechado' in statuses))
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
    
    def read_mesas(self):
        logger.info('recuperando a listagem de mesas para apuração')
        return util.read_mesas(self.dir_apuracao)
    
    def write_mesas(self, conn, mesas):
        logger.info('criando tabela MESAS com as mesas da consolidação')
        sql = 'CREATE TABLE MESAS(MESA TEXT PRIMARY KEY)'
        conn.execute(sql)
        sql = 'INSERT INTO MESAS(MESA) VALUES (?)'
        for mesa in mesas:
            conn.execute(sql, [ mesa ])
        conn.commit()
    
    def write_pesquisas(self, conn, df_pesquisas):
        logger.info('salvando pesquisas de satisfação')
        df_pesquisas.to_sql(config.SURVEY_TABLE, conn, index=False, if_exists="replace")
        conn.commit()
        
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

    def read_pesquisas(self):
        logger.info('recuperando dados da planilha de pesquisas de satisfação')
        currdir = os.getcwd()
        try:
            os.chdir(self.dir_apuracao)
            df = pd.read_excel(config.SURVEYS_SPREADSHEET)
            return df
        finally:
            os.chdir(currdir)
            
    def add_dados_oferta(self, df, df_ofertas):
        logger.info('adicionando dados da oferta')
        ofertas_mapping = df_ofertas.groupby('oferta').prazo.last().to_dict()
        ofertas = df.oferta_catalogo.to_list()
        df[ 'prazo_oferta_m' ] = [ ofertas_mapping.get(oferta, None) for oferta in ofertas ]
        return df
        
    def get_dump_files(self):
        logger.info("retrieving daily dump files of closed incidents")
        currdir = os.getcwd()
        os.chdir(self.dir_import)
        try:
            closed_start_file = config.IMPORT_CLOSED_MASK.format(self.start_date) 
            # Nasty bug: Need to use cutff date below because the dump files are D-1.
            closed_end_file = config.IMPORT_CLOSED_MASK.format(self.cutoff_date)
            all_closed_files = sorted(glob.iglob(config.IMPORT_CLOSED_GLOB))
            closed_files = list([ f for f in all_closed_files if closed_start_file <= f <= closed_end_file ])
            open_file = config.IMPORT_OPEN_MASK.format(self.end_date)
            return closed_files, open_file
        finally:
            os.chdir(currdir)
    
    def process_begin_sql(self, conn):
        currdir = os.getcwd()
        os.chdir(self.dir_apuracao)
        try:
            if not os.path.exists(config.BEGIN_SQL):
                return
            logger.warning('running BEGIN HOOK SQL SCRIPT')
            sql = open(config.BEGIN_SQL).read()
            conn.executescript(sql)
        finally:
            os.chdir(currdir)    
            
    def process_before_load_sql(self, conn):
        currdir = os.getcwd()
        os.chdir(self.dir_apuracao)
        try:
            if not os.path.exists(config.BEFORE_LOAD_SQL):
                return
            logger.warning('running BEFORE LOAD HOOK SQL SCRIPT')
            sql = open(config.BEFORE_LOAD_SQL).read()
            conn.executescript(sql)
        finally:
            os.chdir(currdir)    
            
    def process_after_load_sql(self, conn):        
        currdir = os.getcwd()
        os.chdir(self.dir_apuracao)
        try:
            if not os.path.exists(config.AFTER_LOAD_SQL):
                return
            logger.warning('running AFTER LOAD HOOK SQL SCRIPT')
            sql = open(config.AFTER_LOAD_SQL).read()
            conn.executescript(sql)
        finally:
            os.chdir(currdir)    
            
    def process_end_sql(self, conn):
        currdir = os.getcwd()
        os.chdir(self.dir_apuracao)
        try:
            if not os.path.exists(config.END_SQL):
                return
            logger.warning('running END HOOK SQL SCRIPT')
            sql = open(config.END_SQL).read()
            conn.executescript(sql)
        finally:
            os.chdir(currdir)    

    def filter_incidents(self, all_events, df_open, dfs_closed):
        logger.info("filtrando eventos pelo mapeamento de mesa")
        df_open = df_open[ df_open.id_chamado.isin(all_events) ].copy()
        for i in range(len(dfs_closed)):
            df_closed = dfs_closed[i]
            df_closed = df_closed[ df_closed.id_chamado.isin(all_events) ].copy()
            dfs_closed[i] = df_closed
        return df_open, dfs_closed
    
    def get_connection(self):
        logger.info('creating consolidated db')
        currdir = os.getcwd()
        os.chdir(self.dir_apuracao)
        try:
            if os.path.exists(config.CONSOLIDATED_DB):
                logger.warning("removing older version of the consolidated database")
                os.unlink(config.CONSOLIDATED_DB)
            conn = sqlite3.connect(config.CONSOLIDATED_DB)
            return conn
        finally:
            os.chdir(currdir)    
    
    def fill_table(self, conn, df):
        logger.info('preenchendo tabela REL_MEDICAO')
        conn.executescript(SQL_REL_MEDICAO_DDL)
        param_sets = list(df.itertuples(index=False))
        #df.to_sql(config.INCIDENT_TABLE, conn, index=False, if_exists="replace")
        conn.executemany(SQL_REL_MEDICAO_UPSERT, param_sets)
        conn.commit()
        logger.info('preenchend campo MESA_ATUAL da tabela REL_MEDICAO')
        conn.executescript(SQL_UPDATE_MESA_ATUAL)
        logger.info('preenchend campo USER_STATUS da tabela REL_MEDICAO')
        conn.executescript(SQL_UPDATE_USER_STATUS)
        #logger.info('preenchendo campo PENDENCIA da tabela REL_MEDICAO')
        #conn.executescript(SQL_UPDATE_PENDENCIA)
        conn.commit()
    
    def fill_pendencias(self, conn):
        logger.info('preenchend campo PENDENCIA da tabela REL_MEDICAO')
        repo = Repo(conn)
        df = repo.get_clock_actions()
        pendencias = []
        last_chamado = None
        clock_running = None
        for row in df.itertuples():
            if last_chamado != row.ID_CHAMADO:
                clock_running = True
            else:
                if row.ULTIMA_ACAO_NOME in config.START_CLOCK_ACTIONS:
                    clock_running = True
                elif row.ULTIMA_ACAO_NOME in config.STOP_CLOCK_ACTIONS:
                    clock_running = False
                else:
                    clock_running = clock_running # explicit is better than implicit
            pendencias.append(not clock_running)
            last_chamado = row.ID_CHAMADO
        df[ 'PENDENCIA' ] = pendencias
        repo.set_clock_actions(df)
        repo.commit()
        
    def do_datafix(self):
        logger.warning("STOPING LOADING PROCEDURE FOR A DATAFIX TO BE APPLIED")
        logger.warning("(remember to close the database after data analysis)")
        conn.close()
        while True:
            ans = input('type "ok" to continue or ctrl-c to abort > ').strip()
            if ans == "ok":
                conn.close()
                conn = self.get_connection()
                break
    
    def migrate_tables(self, conn):
        logger.info("migrando dados da tabela REL_MEDICAO para o modelo PyClick")
        logger.info("removing incidents closed before the start date")
        sql = "DELETE FROM REL_MEDICAO WHERE DATA_RESOLUCAO_CHAMADO < ?";
        args=(self.start_date, )
        conn.execute(sql, args)
        logger.info("loading data model")
        conn.execute(sql, args)        
        conn.executescript(SQL_CARGA_REL_MEDICAO)
        sql = "INSERT INTO PARAMS(PARAM, VALOR, OBS) VALUES ('HORA_INICIO_APURACAO', ?, 'Data Início da Apuração')"
        args = self.start_date + ' 00:00:00',
        conn.execute(sql, args)
        sql = "INSERT INTO PARAMS(PARAM, VALOR, OBS) VALUES ('HORA_FIM_APURACAO',    ?, 'Data Fim da Apuração')"
        args = self.end_date + ' 23:59:59',
        conn.execute(sql, args)
        conn.commit()

    def sanity_check(self, conn):
        cursor = conn.execute(SQL_CHECK_IMPORTACAO)
        logger.info("running sanity check")
        result = cursor.fetchone()[ 0 ]
        if result != "OK":
            logger.error("falha na checagem da consolidação do relatório de medição")
            sys.exit(config.EXIT_CONSOLIDATION_ERROR)        
    
    """
    def drop_unactioned_events(self, conn):
        logger.info('dropando incidentes que passaram pela mesa antes do período de apuração')
        conn.executescript(SQL_DROP_UNACTIONED_EVTS)        
        conn.commit()
    """    
    def fill_durations(self, conn, horarios_mesas):
        logger.info('calculando duração de ações')
        # retrieving actions
        df = pd.read_sql(SQL_LISTA_ACOES, conn)
        logger.info('%s ações recuperadas', len(df))
        # computing durations
        end_dt = self.end_date + ' 23:59:59'
        durations = []
        for i, row in enumerate(df.itertuples()):
            sched    = horarios_mesas.get(row.mesa_atual)
            on_hold  = False # row.pendencia == 'S'
            start    = row.data_inicio_acao
            end      = end_dt if row.DATA_PROXIMA_ACAO is None else row.DATA_PROXIMA_ACAO
            if end < start:
                logger.warning("chamado %s / acao %s não possui tempo monotonicamente crescente", row.id_chamado, row.id_acao)
                duration = 0
            elif row.ultima_acao_nome in config.UNTIMED_ACTIONS:
                duration = 0
            else:
                try:
                    duration = ranges.calc_duration(sched, on_hold, start, end)
                except:
                    logger.exception(
                        "erro ao calcular duração da ação %s do evento %s\n\tstart: %s / end: %s",
                        row.id_acao, row.id_chamado, start, end
                    )
                    sys.exit(1)
            item = duration, row.id_chamado, row.id_acao
            durations.append(item)
            if i % 10000 == 0 and i:
                logger.info('calculado %d ações', i)
        # updating durations
        sql = "UPDATE REL_MEDICAO SET DURACAO_M = ? WHERE ID_CHAMADO = ? AND ID_ACAO = ?"
        conn.executemany(sql, durations)
        logger.info('atualizando INCIDENTE_ACOES')
        sql = "UPDATE INCIDENTE_ACOES SET DURACAO_M = ? WHERE ID_CHAMADO = ? AND ID_ACAO = ?"
        conn.executemany(sql, durations)
        conn.commit()
    
    def write_business_hours(self, conn, mesas, horarios_mesas):
        logger.info("escrevendo as horas úteis das mesas")
        start_dt = util.parse_datetime(self.start_date + " 00:00:00")
        end_dt = util.parse_datetime(self.end_date + " 23:59:59")
        param_sets = []
        for mesa in mesas:
            sched = horarios_mesas.get(mesa)
            if not sched:
                continue
            bh = sched.get_business_hours(start_dt, end_dt)
            for bh_start_dt, bh_end_dt in bh:
                args = mesa, util.unparse_datetime(bh_start_dt), util.unparse_datetime(bh_end_dt)
                param_sets.append(args)
        sql = "INSERT INTO HORAS_UTEIS(MESA, HORA_INICIO, HORA_FIM) VALUES (?, ?, ?)"
        conn.executemany(sql, param_sets)
        conn.commit()
    
    def drop_rel_medicao(self, conn):
        logger.info("dropando tabela REL_MEDICAO")
        conn.execute("DROP TABLE REL_MEDICAO");
        conn.commit()
    
    def vacuum(self, conn):
        logger.info("compactando a base de dados")
        conn.execute("VACUUM");
        
    def run(self):
        try:
            mesa_evt_mapping = {}
            logger.info('começando a consolidação do planilhão - versão %d.%d.%d', *self.VERSION)
            mesas           = self.read_mesas()
            df_ofertas      = self.read_ofertas()
            df_pesquisas    = self.read_pesquisas()
            horarios_mesas  = self.load_planilha_horarios()
            
            closed_dumps, open_dump = self.get_dump_files()
            df_open = self.read_dump(open_dump)
            df_open = self.apply_cutoff_date_open(df_open)
            df_open = self.add_dados_oferta(df_open, df_ofertas)
            self.update_event_mapping(mesa_evt_mapping, df_open)
            
            #dfs_closed = [ ]
            logger.info('iniciando loop de parsing pela primeira vez') # to save memory
            for closed_dump in closed_dumps:
                logger.info('processsando %s', closed_dump)
                df = self.read_dump(closed_dump)
                df = self.apply_cutoff_date_closed(df)
                df = self.add_dados_oferta(df, df_ofertas)
                self.update_event_mapping(mesa_evt_mapping, df)
                #dfs_closed.append(df)

            logger.info('filtrando incidentes com base no mapeamento de mesas')
            all_events = set()
            for mesa, events in sorted(mesa_evt_mapping.items()):
                if mesa in mesas:
                    logger.info('particionando mesa %s com %d eventos', mesa, len(events))
                    all_events.update(events)
            
            dfs_closed = [ ]
            logger.info('iniciando loop de parsing pela segunda vez') # to save memory
            for closed_dump in closed_dumps:
                logger.info('processsando %s', closed_dump)
                df = self.read_dump(closed_dump)
                df = self.apply_cutoff_date_closed(df)
                df = self.add_dados_oferta(df, df_ofertas)
                df = df[ df.id_chamado.isin(all_events) ].copy()
                dfs_closed.append(df)
            
            # to speed up duplicated action removal
            df_open = df_open[ df_open.id_chamado.isin(all_events) ].copy()
            df_open, dfs_closed = self.filter_incidents(all_events, df_open, dfs_closed)
            
            logger.info('concatenando planilhão')
            df_planilhao = self.concat_planilhas(df_open, dfs_closed)
            del dfs_closed # release memory
            del df_open # release memory
            
            logger.info('ordenando planilhão')
            util.sort_rel_medicao(df_planilhao)
                        
            logger.info("consolidando planilhão com %d eventos", len(all_events))
            df = df_planilhao[ df_planilhao.id_chamado.isin(all_events) ] # not necessary
            logger.info("consolidando planilhão com %d linhas", len(df))
            
            #self.save_consolidado(df, horarios_mesas)
            conn = self.get_connection()
            self.write_mesas(conn, mesas)
            self.write_pesquisas(conn, df_pesquisas)
            self.process_begin_sql(conn)
            self.fill_table(conn, df)
            if self.datafix:
                self.do_datafix(conn)
            self.process_before_load_sql(conn)
            self.migrate_tables(conn)
            self.process_after_load_sql(conn)
            self.sanity_check(conn)
            #self.drop_unactioned_events(conn)
            self.write_business_hours(conn, mesas, horarios_mesas)
            self.fill_pendencias(conn)
            self.fill_durations(conn, horarios_mesas)
            self.drop_rel_medicao(conn)
            self.process_end_sql(conn)
            self.vacuum(conn)
            conn.close()
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
    
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.dir_import, args.start_date, args.end_date, args.datafix)
    app.run()
    
    