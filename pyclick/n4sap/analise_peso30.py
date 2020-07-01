# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import datetime as dt
import math
import shutil
import argparse
import logging
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st

import pyclick.util as util
import pyclick.config as config


assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('peso30')

SQL_ANALISE_PESO30 = util.get_query('N4SAP__ANALISE_PESO30')

class App():
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_apuracao, output):
        self.dir_apuracao = dir_apuracao
        self.output = output

    def connect_db(self):
        logger.info('connecting to db')
        result_db = os.path.join(self.dir_apuracao, config.CONSOLIDATED_DB)
        conn = sqlite3.connect(result_db)
        return conn
    
    def get_incidents(self, conn):
        logger.info('querying incidents')
        return pd.read_sql(SQL_ANALISE_PESO30, conn)        
    
    def open_spreadsheet(self):
        logger.info("opening KPI spreadsheet")
        assert self.output.endswith(".xlsx")
        if os.path.exists(self.output):
            logger.warning("output spreadsheet already exists. Deleting it")
            os.unlink(self.output)
        return pd.ExcelWriter(self.output, datetime_format=None)
    
    def get_categories_df(self, incs_df):
        logger.info("calculating percentages by category")
        categ_group = incs_df.groupby("CATEGORIA")
        return categ_group.describe()
    
    def get_last_mesas_df(self, incs_df):
        logger.info("calculating percentages by category")
        last_mesas_group = incs_df.groupby("ULTIMA_MESA")
        last_mesas_qty = last_mesas_group[ "ULTIMA_MESA" ].count()
        df = pd.DataFrame({ 'MESA': last_mesas_qty.index, 'QTD': last_mesas_qty.values })
        df.sort_values( 'QTD', inplace=True, ascending=False)
        df.reset_index(drop=True, inplace=True)
        return df
    
    def get_percentiles_df(self, incs_df):
        logger.info("calculating percentiles")
        data = {
            'CATEGORIA' : [],
            'QTD'       : [],
            'MEDIDA'    : [],
            'P05'       : [],
            'P10'       : [],
            'P15'       : [],
            'P20'       : [],
            'P25'       : [],
            'P30'       : [],
            'P35'       : [],
            'P40'       : [],
            'P45'       : [],
            'P50'       : [],
            'P55'       : [],
            'P60'       : [],
            'P65'       : [],
            'P70'       : [],
            'P75'       : [],
            'P80'       : [],
            'P85'       : [],
            'P90'       : [],
            'P95'       : [],
        }
        categorias = [ 'CORRIGIR', 'ORIENTAR', 'REALIZAR' ]
        percentis = {
            'P05' : 0.05, 'P10' : 0.10, 'P15' : 0.15, 
            'P20' : 0.20, 'P25' : 0.25, 'P30' : 0.30, 
            'P35' : 0.35, 'P40' : 0.40, 'P45' : 0.45, 
            'P50' : 0.50, 'P55' : 0.65, 'P60' : 0.60, 
            'P65' : 0.75, 'P70' : 0.70, 'P75' : 0.75, 
            'P80' : 0.80, 'P85' : 0.85, 'P90' : 0.90, 
            'P95' : 0.95, 
        }
        for categoria in categorias:                
            categoria_df = incs_df[ incs_df.CATEGORIA == categoria ]
            # DURACAO_HN
            data[ 'CATEGORIA' ].append(categoria)
            data[ 'QTD' ].append(len(categoria_df))
            data[ 'MEDIDA' ].append('DURACAO_HN')
            for column, pct in percentis.items():
                value = categoria_df[ 'DURACAO_M' ].quantile(pct) / 60.0
                data[ column ].append(value)
            # PENDENCIA
            data[ 'CATEGORIA' ].append(categoria)
            data[ 'QTD' ].append(len(categoria_df))
            data[ 'MEDIDA' ].append('PENDENCIA_HN')
            for column, pct in percentis.items():
                value = categoria_df[ 'PENDENCIA_M' ].quantile(pct) / 60.0
                data[ column ].append(value)
            # TEMPO
            data[ 'CATEGORIA' ].append(categoria)
            data[ 'QTD' ].append(len(categoria_df))
            data[ 'MEDIDA' ].append('TEMPO_HN')
            for column, pct in percentis.items():
                value = categoria_df[ 'TEMPO_M' ].quantile(pct) / 60.0
                data[ column ].append(value)
        df = pd.DataFrame(data)
        df.sort_values([ 'MEDIDA', 'CATEGORIA' ], inplace=True)
        return df
    
    def _make_histogram(self, ax, x, label_x, title):
        #plt.figure(num=None, figsize=(8, 4), dpi=80, facecolor='w', edgecolor='k')
        ax.hist(x, density=True, bins=35, label=label_x, cumulative=True, histtype='step')
        ax.hist(x, density=True, bins=35, label=label_x, cumulative=False)
        ax.grid(color='gray', linestyle='dotted', linewidth=0.5)
        #mn, mx = ax.xlim()
        #ax.xlim(mn, mx)
        kde_xs = np.linspace(x.min(), x.max(), 50)
        kde = st.gaussian_kde(x)
        ax.plot(kde_xs, kde.pdf(kde_xs), label="PDF")
        #ax.legend(loc="upper left")
        #ax.set(ylabel='Prob.', xlabel=label_x, title=title)
        ax.set(ylabel='Prob.', xlabel=label_x)
        
    def make_histograms(self, incs_df):
        # https://stackoverflow.com/questions/33203645/how-to-plot-a-histogram-using-matplotlib-in-python-with-a-list-of-data
        
        logger.info("making histograms")
        # ORIENTAR
        plt.close('all')
        gridspec_kw = { "hspace": 0.2, "wspace": 0.2 }
        fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=False, gridspec_kw=gridspec_kw, figsize=(10, 12))
        
        fig.suptitle('Orientar - Peso 30')
        
        # ORIENTAR - Duração
        categoria_df = incs_df[ incs_df.CATEGORIA == 'ORIENTAR' ]
        duracao_mn = np.log1p(incs_df[ 'DURACAO_M' ]) / math.log(2.0)
        x = duracao_mn
        self._make_histogram(ax1, x, "log2(Duração(mn))", "Duração Orientar Peso 30 em H.N.")

        # ORIENTAR - Pendência
        categoria_df = incs_df[ incs_df.CATEGORIA == 'ORIENTAR' ]
        pendencia_mn = np.log1p(incs_df[ 'PENDENCIA_M' ]) / math.log(2.0)
        x = pendencia_mn
        self._make_histogram(ax2, x, "log2(Pendência(mn))", "Pendência Orientar Peso 30 em H.N.")
        
        # ORIENTAR - Tempo
        categoria_df = incs_df[ incs_df.CATEGORIA == 'ORIENTAR' ]
        tempo_mn = np.log1p(incs_df[ 'TEMPO_M' ]) / math.log(2.0)
        x = tempo_mn
        self._make_histogram(ax3, x, "log2(Tempo(mn))", "Tempo Total Orientar Peso 30 em H.N.")        
        
        plt.show()
        """
        plt.close('all')
        plt.figure(num=None, figsize=(8, 4), dpi=80, facecolor='w', edgecolor='k')
        plt.hist(x, density=True, bins=20, label="Duração(hn)")
        mn, mx = plt.xlim()
        plt.xlim(mn, mx)
        kde_xs = np.linspace(mn, mx, 50)
        kde = st.gaussian_kde(x)
        plt.plot(kde_xs, kde.pdf(kde_xs), label="PDF")
        plt.legend(loc="upper right")
        plt.ylabel('Prob.')
        plt.xlabel('Duração(hn)')
        plt.title("Duração Orientar Peso 30 em H.N.");
        plt.show()
        """
    def run(self):
        try:
            logger.info('starting análise peso 30 - version %d.%d.%d', *self.VERSION)
            conn = self.connect_db()
            with self.open_spreadsheet() as xw:
                incs_df = self.get_incidents(conn)
                incs_df.to_excel(xw, sheet_name="INCIDENTES", index=False)
                print(incs_df)
                categories_df = self.get_categories_df(incs_df)
                categories_df.to_excel(xw, sheet_name="CATEGORIAS")
                print(categories_df)
                last_mesas_df = self.get_last_mesas_df(incs_df)
                last_mesas_df.to_excel(xw, sheet_name="ULTIMAS_MESAS", index=False)
                print(last_mesas_df)
                pcts_df = self.get_percentiles_df(incs_df)
                pcts_df.to_excel(xw, sheet_name="PERCENTIS", index=False)
                self.make_histograms(incs_df)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_apuracao', type=str, help='diretório apuração')
    parser.add_argument('output', type=str, help='planilha de saída')
    args = parser.parse_args()
    app = App(args.dir_apuracao, args.output)
    app.run()            
    