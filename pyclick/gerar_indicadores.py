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

logger = util.get_logger('gerar_indicadores')

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, arq_planilhao, arq_processado, db_medicao):
        assert db_medicao.endswith(".db")
        self.arq_planilhao  = arq_planilhao
        self.arq_processado = arq_processado
        self.db_medicao     = db_medicao
        
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