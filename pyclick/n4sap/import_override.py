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
import pyclick.n4sap.config as n4_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('consolida_planilhao')

SQL_UPSERT = util.get_query("UPSERT_INCIDENTES_OVERRIDE")

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao, truncate):
        self.dir_apuracao = dir_apuracao
        self.truncate = truncate
    
    def read_override_spreadsheet(self):
        def conv(value):
            if pd.isna(value):
                return value
            else:
                return str(value)
        
        logger.info("reading override spreadsheet")
        filename = os.path.join(self.dir_apuracao, n4_config.OVERRIDE_SPREADSHEET)
        df = pd.read_excel(filename, index_col=False)
        headers = df.columns.to_list()
        if headers != n4_config.OVERRIDE_COLUMNS:
            util.report_file_mismatch(logger, headers, n4_config.OVERRIDE_COLUMNS)
            sys.exit(config.EXIT_FILE_MISMATCH)
        df[ 'ID_CHAMADO' ] = df['ID_CHAMADO'].apply(conv)
        self.validate_override_data(df)
        return df
    
    def validate_override_data(self, df):
        logger.info('validandos dados antes da importação')
        error = False
        for i, row in enumerate(df.itertuples(index=False)):
            line = i + 2
            if not row.ID_CHAMADO:
                logger.error("ID_CHAMADO não preenchido na linha %d", line)
                error = True
                continue
            if not row.ESTORNO:
                logger.error("ESTORNO não preenchido na linha %d", line)
                error = True
                continue
            if row.ESTORNO not in ('S', 'N'):
                logger.error("ESTORNO preenchido incorretamente na linha %d. Favor usar apenas 'S' ou 'N'", line)
                error = True
                continue
            if row.ESTORNO == 'S':
                continue
            if not row.OBS_OVERRIDE:
                logger.error("Favor preencher uma observação para a linha %d da planilha de override", line)
                error = True
                continue
            if row.CATEGORIA and row.CATEGORIA not in ('REALIZAR', 'ORIENTAR', 'CORRIGIR'):
                logger.error("CATEGORIA inválida na linha %d", line)
                error = True
                continue
            if row.PESO >= 0 and row.PESO not in (0, 1, 30, 35):
                logger.error("Peso inválido inválida na linha %d. Favor usar apenas 0, 1, 30 ou 35", line)
                error = True
                continue                
        if error:
            logger.error("processamento interrompido devido a existência de erros na planilha de override")
            sys.exit(config.EXIT_DATA_ERROR)
        
    def get_db_connection(self):
        logger.info('conectando à base de apuração')
        db_out = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        if not os.path.exists(db_out):
            logger.error('base de dados de apuração %s não existe', db_out)
            sys.exit(EXIT_DB_DOES_NOT_EXIST)
        conn = sqlite3.connect(db_out)
        return conn
        
    def import_override_spreadsheet(self, df, conn):
        if self.truncate:
            conn.execute("DELETE FROM INCIDENTES_OVERRIDE")
        cursor = conn.cursor()
        for i, row in enumerate(df.itertuples(index=False)):
            logger.info("upsert override incidente %s", row.ID_CHAMADO)
            cursor.execute(SQL_UPSERT, row)
        conn.commit()
            
    def run(self):
        try:
            logger.info('começando importação da planilha de override - versão %d.%d.%d', *self.VERSION)
            df = self.read_override_spreadsheet()
            conn = self.get_db_connection()
            self.validate_override_data(df)
            self.import_override_spreadsheet(df, conn)
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--truncate', action="store_true", default=False, help='limpa tabela de override antes da carga')
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.truncate)
    app.run()