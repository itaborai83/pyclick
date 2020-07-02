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
    CUTTOF_DURACOES_H = 10 * 9
    
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
            'P50' : 0.50, 'P55' : 0.55, 'P60' : 0.60, 
            'P65' : 0.65, 'P70' : 0.70, 'P75' : 0.75, 
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
        p85 = x.quantile(0.85)
        ax2 = ax.twinx()
        n, bins, patches = ax.hist(x, bins=35, cumulative=False, density=False)
        
        x2 = sorted(x)
        y2 = x.cumsum() / x.sum()
        ax2.plot(x2, y2, 'r-')
        
        ax.set_xlabel(label_x)
        ax.set_ylabel('Qtd. Incidentes', color='b')
        ax2.set_ylabel('CDF', color='r')
        
        """
        #plt.figure(num=None, figsize=(8, 4), dpi=80, facecolor='w', edgecolor='k')
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
        
        ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
        ax2.hist(x, density=True, bins=35, label=label_x, cumulative=True, histtype='step')
        ax2.grid(color='blue', linestyle='dotted', linewidth=0.5)
        """
        
    def make_histograms(self, incs_df):
        # https://stackoverflow.com/questions/33203645/how-to-plot-a-histogram-using-matplotlib-in-python-with-a-list-of-data
        
        logger.info("making histograms")
        # ORIENTAR
        plt.close('all')
        gridspec_kw = {  }
        fig, ax = plt.subplots(1, sharex=False, gridspec_kw=gridspec_kw, figsize=(8, 4))        
        fig.suptitle('Orientar - Peso 30')
        categoria_df = incs_df[ (incs_df.CATEGORIA == 'ORIENTAR') ]
        x = categoria_df[ 'TEMPO_M' ] / 60
        x = x[ x < self.CUTTOF_DURACOES_H ]
        self._make_histogram(ax, x, "Tempo(HN)", "Tempo Total Orientar Peso 30 em H.N.")        
        plt.show()
        fig.savefig('orientar.png')

        # CORRIGIR
        plt.close('all')
        gridspec_kw = {  }
        fig, ax = plt.subplots(1, sharex=False, gridspec_kw=gridspec_kw, figsize=(8, 4))        
        fig.suptitle('Corrigir - Peso 30')
        categoria_df = incs_df[ (incs_df.CATEGORIA == 'CORRIGIR') ]
        x = categoria_df[ 'TEMPO_M' ] / 60
        x = x[ x < self.CUTTOF_DURACOES_H ]
        self._make_histogram(ax, x, "Tempo(HN)", "Tempo Total Corrigir Peso 30 em H.N.")
        plt.show()
        fig.savefig('corrigir.png')
        
        # REALIZAR
        plt.close('all')
        gridspec_kw = {  }
        fig, ax = plt.subplots(1, sharex=False, gridspec_kw=gridspec_kw, figsize=(8, 4))        
        fig.suptitle('Realizar - Peso 30')
        categoria_df = incs_df[ (incs_df.CATEGORIA == 'CORRIGIR') ]
        x = categoria_df[ 'TEMPO_M' ] / 60
        x = x[ x < self.CUTTOF_DURACOES_H ]
        self._make_histogram(ax, x, "Tempo(HN)", "Tempo Total Realizar Peso 30 em H.N.")
        plt.show()
        fig.savefig('realizar.png')
        
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
    