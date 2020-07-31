# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import glob
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

SQL_REL_MEDICAO_SELECT = util.get_query("CONSOLIDA__REL_MEDICAO_SELECT")

logger = util.get_logger('consolidator')

class ConsolidatorSrv(object):

    def __init__(self, dir_import, dir_staging, dir_apuracao, dir_work):
        self.dir_import = dir_import 
        self.dir_staging = dir_staging
        self.dir_apuracao = dir_apuracao
        self.dir_work = dir_work
    
    def _read_dump(self, dir_import, dump_file):
        filename = os.path.join(dir_import, dump_file)
        dump_file_without_gz = dump_file[ :-3 ]
        decompressed_filename = os.path.join(self.dir_work, "$WORK-" + dump_file_without_gz)
        util.decompress_to(filename, decompressed_filename)
        conn = sqlite3.connect(decompressed_filename)
        df = pd.read_sql(SQL_REL_MEDICAO_SELECT, conn)
        util.sort_rel_medicao(df)
        del conn
        os.unlink(decompressed_filename)
        return df
        
    def read_dump(self, dump_file):
        return self._read_dump(self.dir_import, dump_file)

    def read_filtered_dump(self, dump_file):
        return self._read_dump(self.dir_work, dump_file)
        
    def apply_cutoff_date(self, df, cutoff_date, closed):
        if closed:
            return df[ df.data_resolucao_chamado < cutoff_date ].copy()
        else:
            return df[ df.data_abertura_chamado < cutoff_date ].copy()
        
    def update_event_mapping(self, mesa_evt_mapping, df):
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
    
    def validate_filename(self, dump_file):
        is_open = 'OPEN' in dump_file
        is_closed = 'CLOSED' in dump_file
        is_db_gz = dump_file.endswith('.db.gz')
        if not is_db_gz or (not is_open and not is_closed):
            raise ValueError(f'invalid filename {dump_file}')
        return is_open

    def read_index_files(self):
        currdir = os.getcwd()
        try:
            os.chdir(self.dir_work)
            files = sorted(glob.glob("*.idx"))
            paths = [ os.path.join(self.dir_work, f) for f in files ]
            return list(paths)
        finally:
            os.chdir(currdir)
        
    def process_index_file(self, set_mesas, all_events, index_file):
        with open(index_file) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                if '\t' not in line:
                    continue
                mesa, inc = line.split('\t')
                if mesa in set_mesas:
                    all_events.add(inc)

    def write_index_file(self, agg_index_file, all_events):
        currdir = os.getcwd()
        try:
            os.chdir(self.dir_work)
            with open(agg_index_file, 'w') as fh:
                for event in sorted(all_events):
                    print(event, file=fh)
        finally:
            os.chdir(currdir)
    
    def read_index(self, agg_index_file):
        currdir = os.getcwd()
        try:
            os.chdir(self.dir_work)
            with open(agg_index_file) as fh:
                result = []
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    elif line.startswith("#"):
                        continue
                    inc = line
                    result.append(inc)
            return set(result)
        finally:
            os.chdir(currdir)
    
    def filter_events(self, df, all_events):
        return df[ df.id_chamado.isin(all_events) ].copy()

    def save(self, df, db_name, vacuum=False):
        conn = sqlite3.connect(db_name)
        df.to_sql(config.INCIDENT_TABLE, conn, index=False)
        conn.commit()
        if vacuum:
            conn.execute("VACUUM")
        conn.close()
        del conn
        logger.info('compressing...')
        util.compress_to(db_name, db_name + '.gz')
        os.unlink(db_name)
    
    def get_filtered_planilhoes(self, glob_open, glob_closed):
        currdir = os.getcwd()
        try:
            os.chdir(self.dir_work)
            open = glob.glob(glob_open)
            closed = sorted(glob.glob(glob_closed))
            assert len(open) == 1
            return open[ 0 ], closed
        finally:
            os.chdir(currdir)

    def _drop_duplicated_actions(self, df):
        statuses = set(df.status_de_evento.to_list())
        assert (len(statuses) == 2 and 'Resolvido' in statuses and 'Fechado' in statuses) or \
               (len(statuses) == 1 and ('Resolvido' in statuses or 'Fechado' in statuses))
        df.sort_values(by=[ 'id_acao', 'status_de_evento' ], inplace=True, kind='mergesort', ignore_index=True)
        # keep Resolvido if it exists
        df.drop_duplicates(subset=[ 'id_acao' ], keep='first', inplace=True, ignore_index=True)

    def concat_planilhoes(self, open_df, closed_dfs):
        closed_df = pd.concat(closed_dfs)
        self._drop_duplicated_actions(closed_df)
        df = pd.concat([ closed_df, open_df ])
        return df
