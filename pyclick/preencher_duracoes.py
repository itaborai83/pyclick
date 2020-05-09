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
import pyclick.config as config
import pyclick.util as util

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('consolida_planilhao')

SQL_LISTA_ACOES     = util.get_query('DURACAO__LISTA_ACOES')
SQL_UPDATE_DURACAO  = util.get_query('DURACAO__UPDATE_DURACAO')

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
        
    def load_planilha_horarios(self):
        logger.info('carregando planilha de horários de mesas')
        fname = os.path.join(self.dir_apuracao, config.BUSINESS_HOURS_SPREADSHEET)
        if not os.path.exists(fname):
            logger.error('planilha de horários de mesas  %s não encontrado no diretório de apuração', config.BUSINESS_HOURS_SPREADSHEET)
            sys.exit(-1)
        return ranges.load_spreadsheet(fname)

    def open_db(self):
        logger.info('abrindo base de dados %s', config.CONSOLIDATED_DB)
        currdir = os.getcwd()
        os.chdir(self.dir_apuracao)
        try:
            conn = sqlite3.connect(config.CONSOLIDATED_DB)
            return conn
        finally:
            os.chdir(currdir)
    
    def get_actions(self, conn):
        logger.info('recuperando listagem de ações')
        df = pd.read_sql(SQL_LISTA_ACOES, conn)
        logger.info('%s ações recuperadas', len(df))
        return df
    
    def compute_durations(self, df, horarios_mesas):
        logger.info('calculando durações')
        id_chamado_ant = None
        result = []
        for row in df.itertuples():
            sched    = horarios_mesas.get(row.mesa_atual)
            on_hold  = row.pendencia == 'S'
            start    = row.data_inicio_acao
            end      = row.DATA_PROXIMA_ACAO
            duration = ranges.calc_duration(sched, on_hold, start, end)
            item     = duration, row.id_chamado, row.id_acao
            result.append(item)
        return result
    
    def update_durations(self, conn, durations):
        logger.info('atualizando durações')
        args = []
        conn.executemany(SQL_UPDATE_DURACAO, durations)
        logger.info('commitando')
        conn.commit()
        
    def run(self):
        try:
            logger.info('começando preenchimento de durações das ações - versão %d.%d.%d', *self.VERSION)
            horarios_mesas = self.load_planilha_horarios()
            conn = self.open_db()
            df = self.get_actions(conn)
            durations = self.compute_durations(df, horarios_mesas)
            self.update_durations(conn, durations)
            conn.close()
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao)
    app.run()
    