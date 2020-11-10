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

logger = util.get_logger('nbclassify')

SQL_FETCH_DATA = util.get_query('CORPUS__GENCLOUD')

class App(object):
    
    VERSION             = (0, 0, 0)
    MIN_OPEN_INCIDENTS  = 15
    
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
        logger.info(f'{qty} rows fetched')
        return texts_df
    
    def genwordcloud(self, idx, designado, texto_fechados, texto_abertos):
        designado = designado.replace(' ', '_')
        filename  = f'WC-{idx:03}-{designado}.png'
        path      = os.path.join(self.dir_cloud, filename)
        textos    = (texto_fechados + ' ' + texto_abertos).strip()
        textos, _ = re.subn('\s+', ' ', textos)
        words     = textos.split(' ')
        random.shuffle(words)
        random.shuffle(words)
        random.shuffle(words)
        textos    = ' '.join(words)
        wc.WordCloud(background_color='white', width=1024, height=768).generate(textos).to_file(path)
        
    def run(self):
        try:
            logger.info('starting word cloud generator - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            data_df = self.fetch_data(conn)
            for i, row in enumerate(data_df.itertuples()):
                if row.incidentes_abertos < self.MIN_OPEN_INCIDENTS:
                    logger.info(f'skiping word cloud #{i + 1} for {row.designado} due to too few open incidents')
                    continue
                logger.info(f'generating word cloud #{i + 1} for {row.designado} with {row.incidentes_abertos} open incidents')
                self.genwordcloud(i + 1, row.designado, row.texto_fechados, row.texto_abertos)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    parser.add_argument('dir_cloud', type=str, help='diretório de nuvem de palavras')
    parser.add_argument('--split-open')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.dir_cloud)
    app.run()
     