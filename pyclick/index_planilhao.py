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
import concurrent.futures

import pyclick.ranges as ranges
import pyclick.util as util
import pyclick.config as config
from pyclick.repo import Repo

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('index_planilhao')

SQL_REL_MEDICAO_SELECT = util.get_query("CONSOLIDA__REL_MEDICAO_SELECT")

class App(object):
        
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_work, dir_import, dump_file, cutoff_date):
        assert dump_file.endswith('.db.gz')
        self.dir_work = dir_work
        self.dir_import = dir_import
        self.dump_file = dump_file
        self.cutoff_date = cutoff_date
        dump_file_without_db_gz = self.dump_file[ :-6 ]
        self.index_file = dump_file_without_db_gz + ".idx"
        
        
    def read_dump(self):
        filename = os.path.join(self.dir_import, self.dump_file)
        dump_file_without_gz = self.dump_file[ :-3 ]
        decompressed_filename = os.path.join(self.dir_work, "$WORK-" + dump_file_without_gz)
        logger.info('lendo arquivo %s', filename)
        util.decompress_to(filename, decompressed_filename)
        conn = sqlite3.connect(decompressed_filename)
        df = pd.read_sql(SQL_REL_MEDICAO_SELECT, conn)
        util.sort_rel_medicao(df)
        del conn
        os.unlink(decompressed_filename)
        return df
    
    def apply_cutoff_date_closed(self, df):
        logger.info('filtrando eventos encerrados após a data de corte %s', self.cutoff_date)
        df = df[ df.data_resolucao_chamado < self.cutoff_date ]
        return df.copy()

    def apply_cutoff_date_open(self, df):
        logger.info('filtrando eventos abertos após a data de corte %s', self.cutoff_date)
        df = df[ df.data_abertura_chamado < self.cutoff_date ]
        return df.copy()
        
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
    
    def validate_filename(self):
        logger.info(f'validating filename {self.dump_file}')
        is_open = 'OPEN' in self.dump_file
        is_closed = 'CLOSED' in self.dump_file
        is_db_gz = self.dump_file.endswith('.db.gz')
        if not is_db_gz or (not is_open and not is_closed):
            logger.error(f'invalid filename {self.dump_file}')
            sys.exit(1)
        return is_open
            
    def run(self):
        try:
            logger.info('started dump file indexing - version %d.%d.%d', *self.VERSION)
            is_open = self.validate_filename()
            df = self.read_dump()
            if is_open:
                df = self.apply_cutoff_date_open(df)
            else:
                df = self.apply_cutoff_date_closed(df)
            mesa_evt_mapping = {}
            self.update_event_mapping(mesa_evt_mapping, df)
            index_path = os.path.join(self.dir_work, self.index_file)
            with open(index_path, "w") as fh:
                for mesa, events in sorted(mesa_evt_mapping.items()):
                    for event in sorted(events):
                        print(mesa, event, sep='\t', file=fh)
            logger.info("finished")
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_work', type=str, help='diretório de trabalho')
    parser.add_argument('dir_import', type=str, help='diretório importação')
    parser.add_argument('dump_file', type=str, help='arquivo planilhão')
    parser.add_argument('cutoff_date', type=str, help='data de corte')
    args = parser.parse_args()
    app = App(args.dir_work, args.dir_import, args.dump_file, args.cutoff_date)
    app.run()
    
    