import re
import os
import argparse
import logging
import sqlite3
from unidecode import unidecode

import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt


from sklearn.naive_bayes import ComplementNB, MultinomialNB
from sklearn import metrics
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler, MaxAbsScaler, QuantileTransformer
from sklearn.model_selection import cross_validate

import pyclick.util as util
import pyclick.config as config
import pyclick.assyst.config as click_config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('nbclassify')

SQL_FETCH_DATA = util.get_query('CORPUS__CLASSIFIER_DATA')

class App(object):
    
    VERSION = (1, 0, 0)
    
    def __init__(self, dir_apuracao):
        self.dir_apuracao = dir_apuracao
    
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
    
    def train_classifier(self, data_df):
        logger.info('munging data for training')
        vectorizer = TfidfVectorizer()
        classifier = ComplementNB()
        bow = vectorizer.fit_transform(data_df[ 'texto' ].array)
        labels = data_df[ 'categoria' ].array
        classifier.fit(bow, labels)
        return vectorizer, classifier
    
    def analyze_class(self, vectorizer, classifier, class_name):
        idx = -1
        for idx, name in enumerate(classifier.classes_):
            if name == class_name:
                class_idx = idx
        assert idx >= 0
        class_count = classifier.class_count_[ class_idx ]
        print(class_name, class_idx, class_count)
        
        
        
    def run(self):
        try:
            logger.info('starting aging naive bayes classifier - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            data_df = self.fetch_data(conn)
            vectorizer, nb_classifier = self.train_classifier(data_df)
            vocabulary = vectorizer.vocabulary_
            num_features = len(vocabulary)
            identitiy = np.identity(num_features)
            classifications = nb_classifier.predict_proba(identitiy)
            
            term     = []
            prob_ok  = []
            prob_a60 = []
            for single_term_doc, classification in zip(identitiy, classifications):
                terms = vectorizer.inverse_transform(single_term_doc)
                assert len(terms) == 1
                term.append(terms[0][0])
                prob_ok.append(classification[0])
                prob_a60.append(classification[1])
                #print(terms[0], classification[0], classification[1], classification[2], classification[3])
            terms_df = pd.DataFrame({
                'term'      : term,
                'prob_ok'   : prob_ok,
                'prob_a60'  : prob_a60,
            })
            terms_df.to_excel('terms.xlsx', index=False)
            """
            acc_terms = {}
            chamado_terms = {}
            chamados = {}
            for row in texts_df.itertuples():
                chamado_terms = self.index_incident(row.ID_CHAMADO, row.TEXTO, acc_terms, stop_words)
                chamados[ row.ID_CHAMADO ] = chamado_terms
            logger.info('pruning terms')
            self.prune_terms(chamados, acc_terms)
            logger.info('clearing terms')
            self.clear_terms(conn)
            logger.info('storing terms')
            for id_chamado, chamado_terms in chamados.items():
                self.save_terms(conn, id_chamado, chamado_terms)
            conn.commit()
            """
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório de apuração')
    args = parser.parse_args()
    app = App(args.dir_apuracao)
    app.run()
     