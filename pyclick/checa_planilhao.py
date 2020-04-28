# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import glob
import shutil
import argparse
import logging
import datetime as dt
import pandas as pd
import sqlite3

import pyclick.util as util
import pyclick.config as config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('checa_planilhao')

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, import_dir, start_date, end_date, inc_file, out_file):
        self.import_dir = import_dir
        self.start_date = start_date
        self.end_date = end_date
        self.inc_file = inc_file
        self.out_file = out_file
        
    """
    def update_open_acc(self, df_open_acc, df_open, df_closed):
        logger.info('updating open incident accumulator')
        ids_open_acc = set(df_open_acc.id_chamado.to_list())
        ids_open = set(df_open.id_chamado.to_list())
        ids_closed = set(df_closed.id_chamado.to_list())
        
        # same incident can't be open and closed in the same file
        ids_open_and_closed = ids_open.intersection(ids_closed)
        if len(ids_open_and_closed) > 0:
            logger.error('there are incidents marked as open and closed at the same time\n\t%s', repr(ids_open_and_closed))
            assert len(ids_open_and_closed) == 0 
        
        # if the incident is on the open accumulator and appears as closed, mark it for removal
        ids_to_remove_from_acc = ids_open_acc.intersection(ids_closed)
        
        # if the incidente is on the open list and it is in the open accumulator, it has new actions
        ids_to_update_acc = ids_open_acc.intersection(ids_open)
        
        # if the incident is on the open list but not in the open accumulator, mark it for insertion
        ids_to_add_to_acc = ids_open.difference(ids_open_acc)
        
        # nothing to be done in the following case. Opened and closed on the same day or it is a bug in the  extraction query
        # ids_closed.difference(open_acc)
        
        # remove everything marked for removal and for updating
        ids_to_remove_or_update_from_acc = ids_to_remove_from_acc.union(ids_to_update_acc)
        df_new_open_acc = df_open_acc[ ~(df_open_acc.id_chamado.isin(ids_to_remove_or_update_from_acc)) ]
        
        # add everything marked for insertion and for updating
        ids_to_add_or_update_acc = ids_to_add_to_acc.union(ids_to_update_acc)
        df_to_add = df_open[ df_open.id_chamado.isin(ids_to_add_or_update_acc) ]
        df_open_acc = df_new_open_acc.append(df_to_add, ignore_index=True, verify_integrity=True)
        
        # sort and return new version
        util.sort_rel_medicao(df_open_acc)
        
        ids_open_acc = set(df_open_acc.id_chamado.to_list())
        logger.info('%d events open with %d actions associated', len(ids_open_acc), len(df_open_acc))
        return df_open_acc

    def process_ids(self, df):
        def conv(value):
            if pd.isna(value):
                return value
            else:
                return str(value)
        df[ 'id_chamado' ] = df['id_chamado'].apply(conv)
        df[ 'chamado_pai' ] = df['chamado_pai'].apply(conv)
        df[ 'id_acao'  ] = pd.to_numeric( df[ 'id_acao' ], errors='coerce' )
        df.dropna(subset = [ 'id_acao' ], inplace=True)
    
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
    
    def check_row_splits(self, df):
        last_column = config.EXPECTED_COLUMNS[ -1 ]
        split_rows_df = df[ df[ last_column  ].isna() ]
        return len(split_rows_df) > 0

    def rename_columns(self, df_original):
        logger.debug('renomeando columns')
        df_renamed = df_original.rename(mapper=config.COLUMN_MAPPING, axis='columns')
        headers = df_renamed.columns.to_list()
        if headers != config.RENAMED_COLUMNS:
            logger.info('renamed columns mismatch ')
            self.report_file_mismatch(headers, config.RENAMED_COLUMNS)
            sys.exit(config.EXIT_RENAMED_MISMATCH)
        return df_renamed

    def read_staging_file(self, fullpath):
        logger.info('lendo arquivo de staging %s', fullpath)
        path, filename = os.path.split(fullpath)
        currdir = os.getcwd()
        try:
            os.chdir(path)
            df = pd.read_csv(
                filename, 
                sep             = config.CSV_SEPARATOR,
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
        finally:
            os.chdir(currdir)
            
    def handle_filename(self, filename):
        orig_filename = filename
        if not orig_filename.startswith(config.INPUT_FILENAME_PREFIX):
            return orig_filename
        filename = filename[ len(config.INPUT_FILENAME_PREFIX) : ]
        day, month, year_ext = filename.split("-")
        year, ext = year_ext.split(".")
        assert ext == "csv"
        new_name = year + "-" + month + "-" + day + "." + ext
        logger.warning("moving staging file from %s to %s in dir %s", orig_filename, new_name, os.getcwd())
        shutil.move(orig_filename, new_name)
        return new_name
    
    def preprocess_staging_file(self, fullpath):
        logger.info('pré-processando arquivo de staging %s', fullpath)
        currdir = os.getcwd()
        path, filename = os.path.split(fullpath)
        try:
            os.chdir(path)
            filename = self.handle_filename(filename)
            with open(filename, encoding="latin-1") as fh:
                line = fh.readline()
                if not line.startswith(config.SEPARATOR_HEADER):
                    return os.path.join(path, filename)
                logger.info('removing separator header')
                filename_tmp = filename + ".tmp"
                with open(filename_tmp, "w", encoding="latin-1") as fh2:
                    logger.warning("removing separator line from staging file")
                    for line in fh:
                        fh2.write(line)
            logger.warning("moving staging file from %s to %s", filename_tmp, fullpath)
            shutil.move(filename_tmp, filename)
            return os.path.join(path, filename)
        finally:
            os.chdir(currdir)

    def split_open_events(self, df):
        logger.info('separando eventos abertos de fechados')
        df_open = df[ (df.data_resolucao_chamado.isna()) | (df.status_de_evento == "Aberto") ]
        df_closed = df[ ~((df.data_resolucao_chamado.isna()) | (df.status_de_evento == "Aberto")) ]
        return df_open.copy(), df_closed.copy()
        
    def replace_tabs_enters(self, df):
        logger.info('removendo tabs e enters')
        return
        substs = {
            '\t': '<<TAB>>',
            '\r\n': '<<ENTER>>',
            '\n': '<<ENTER>>',
        }
        df.replace(substs, regex=True, inplace=True)
    
    def save(self, df, db_name):
        logger.info('salvando dataframe como %s', db_name)
        conn = sqlite3.connect(db_name)
        df.to_sql(config.INCIDENT_TABLE, conn, index=False, if_exists="replace")
        conn.commit()
        conn.execute("VACUUM")
        conn.close()
        del conn
        logger.info('compressing...')
        util.compress(db_name)
        
    def read_open_acc(self):
        assert self.open_acc is not None
        if self.open_acc.endswith('.gz'):
            decompressed_name = util.decompress(self.open_acc)
            conn = sqlite3.connect(decompressed_name)
        else:
            conn = sqlite3.connect(self.open_acc)
        sql = "SELECT * FROM " + config.INCIDENT_TABLE
        df = pd.read_sql(sql, conn)
        util.sort_rel_medicao(df)
        conn.close()
        if self.open_acc.endswith('.gz'):
            decompressed_name = util.compress(decompressed_name)
        return df
    """
    def read_incidents(self):
        with open(self.inc_file) as f:
            result = []
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                result.append(line)
            return set(result)
    
    def get_dump_files(self):
        logger.info("retrieving daily dump files of closed incidents")
        currdir = os.getcwd()
        os.chdir(self.import_dir)
        try:
            closed_start_file = config.IMPORT_CLOSED_MASK.format(self.start_date) 
            closed_end_file = config.IMPORT_CLOSED_MASK.format(self.end_date) 
            open_start_file = config.IMPORT_CLOSED_MASK.format(self.start_date) 
            open_end_file = config.IMPORT_CLOSED_MASK.format(self.end_date)             
            all_closed_files = sorted(glob.iglob(config.IMPORT_CLOSED_GLOB))
            all_open_files = sorted(glob.iglob(config.IMPORT_OPEN_GLOB))
            closed_files = list([ f for f in all_closed_files if closed_start_file <= f <= closed_end_file ])
            open_files = list([ f for f in all_open_files if open_start_file <= f <= open_end_file ])
            return closed_files, open_files
        finally:
            os.chdir(currdir)
    
    def process(self, filename):
        currdir = os.getcwd()
        decompressed_name = None
        try:
            logger.info("processing %s", filename)
            os.chdir(self.import_dir)
            decompressed_name = util.decompress(filename)
            conn = sqlite3.connect(decompressed_name)
            sql = "SELECT DISTINCT {} AS ARQ, ID_CHAMADO FROM REL_MEDICAO ORDER BY ID_CHAMADO".format(repr(filename))
            df = pd.read_sql(sql, conn)
            conn.close()
            return df
        finally:
            if decompressed_name is not None:
                util.compress(decompressed_name)
            os.chdir(currdir)
            
    def run(self):
        try:
            logger.info('começando a checagem do planilhao - versão %d.%d.%d', *self.VERSION)
            incs = self.read_incidents()
            closed_files, open_files = self.get_dump_files()
            dfs = []
            for closed_file in closed_files:
                df = self.process(closed_file)
                df = df[ df.id_chamado.isin(incs) ].copy()
                dfs.append(df)
            for open_file in open_files:
                df = self.process(open_file)
                df = df[ df.id_chamado.isin(incs) ].copy()
                dfs.append(df)
            df = pd.concat(dfs)
            df.to_excel(self.out_file, index=False)
            """
            fullpath = self.preprocess_staging_file(self.staging_file)
            df = self.read_staging_file(fullpath)
            df = self.rename_columns(df)
            self.replace_tabs_enters(df)
            self.process_ids(df)
            if self.open_acc is None:
                df_open_acc = pd.DataFrame(columns=df.columns)
            else:
                df_open_acc = self.read_open_acc()
            df_open, df_closed = self.split_open_events(df)
            df_open_acc = self.update_open_acc(df_open_acc, df_open, df_closed)
            util.sort_rel_medicao(df_closed)
            util.sort_rel_medicao(df_open)
            path, filename_ext = os.path.split(fullpath)
            if filename_ext.endswith('.gz'):
                filename, ext, gz = filename_ext.split('.')
            else:
                filename, ext = filename_ext.split('.')
            open_filename = os.path.join(self.import_dir, filename + "-OPEN.db")
            closed_filename = os.path.join(self.import_dir, filename + "-CLOSED.db")
            self.save(df_open_acc, open_filename)
            self.save(df_closed, closed_filename)
            if filename_ext.endswith('.gz'):
                util.compress(filename + '.' + ext)                
            """
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('import_dir', type=str, help='diretório de importação')
    parser.add_argument('start_date', type=str, help='data inicio apuração')
    parser.add_argument('end_date', type=str, help='data fim apuração')
    parser.add_argument('inc_file', type=str, help='incident listing file')
    parser.add_argument('out_file', type=str, help='out file')
    args = parser.parse_args()
    app = App(args.import_dir, args.start_date, args.end_date, args.inc_file, args.out_file)
    app.run() 