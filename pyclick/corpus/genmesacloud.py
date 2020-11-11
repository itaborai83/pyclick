import re
import os
import argparse
import logging
import sqlite3
import pandas as pd
import wordcloud as wc
import os.path
import random

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('genmesacloud')

SQL_FETCH_DATA = util.get_query('CORPUS__GENCLOUD_MESAS')
SQL_FETCH_FREQS = util.get_query('CORPUS__GENCLOUD_MESAS_FREQS')

class App(object):
    
    VERSION     = (0, 0, 0)
    WC_BG       = 'white'
    WC_WIDTH    = 1024
    WC_HEIGHT   = 768
    FREQS_SPREADSHEET = 'term_freqs.xlsx'
    
    def __init__(self, dir_apuracao, dir_cloud):
        self.dir_apuracao = dir_apuracao
        self.dir_cloud = dir_cloud
    
    def connect_db(self):
        logger.info('connecting to  db')
        result_db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        conn = sqlite3.connect(result_db)
        return conn
    
    def fetch_data(self, conn):
        logger.info('fetching incident terms')
        texts_df = pd.read_sql(SQL_FETCH_DATA, conn, index_col=None)
        qty = len(texts_df)
        logger.info(f'{qty} texts fetched')
        freqs_df = pd.read_sql(SQL_FETCH_FREQS, conn, index_col=None)
        qty = len(freqs_df)
        logger.info(f'{qty} frequencies fetched')
        return texts_df, freqs_df
        
    def genwordcloud(self, idx, mesa, categoria, texto_fechados, texto_abertos):
        filename  = f'WC-{idx:03}-{mesa}-{categoria}.png'
        path      = os.path.join(self.dir_cloud, filename)
        textos    = (texto_fechados + ' ' + texto_abertos).strip()
        textos, _ = re.subn('\s+', ' ', textos)
        words     = textos.split(' ')
        random.shuffle(words)
        random.shuffle(words)
        random.shuffle(words)
        textos    = ' '.join(words)
        wc.WordCloud(
            background_color =self.WC_BG, 
            width            =self.WC_WIDTH, 
            height           =self.WC_HEIGHT,
            include_numbers  = True
        ).generate(textos).to_file(path)
        
    def run(self):
        try:
            logger.info('starting word cloud generator for mesas - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            data_df, freqs_df = self.fetch_data(conn)
            for i, row in enumerate(data_df.itertuples()):
                logger.info(f'generating word cloud #{i + 1} for {row.mesa} / {row.categoria} with {row.incidentes_abertos} open incidents')
                self.genwordcloud(i + 1, row.mesa, row.categoria, row.texto_fechados, row.texto_abertos)
            logger.info('saving term frequency spreadsheet')
            filename = os.path.join(self.dir_cloud, self.FREQS_SPREADSHEET)
            freqs_df.to_excel(filename, index=False)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    parser.add_argument('dir_cloud', type=str, help='diretório de nuvem de palavras')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.dir_cloud)
    app.run()
     