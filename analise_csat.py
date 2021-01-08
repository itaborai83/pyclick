# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import argparse
import logging
import datetime as dt

import pandas as pd

import pyclick.config as config
import pyclick.util as util
import pyclick.models as models
import pyclick.n4sap.repo as repo
import pyclick.assyst.dump_surveys as dump_surveys
import pyclick.n4sap.kpis
from pyclick.n4sap.csat import Csat, CsatPeriodo

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('csat')

def build_ranges(end_date):
    year = int(end_date[:4])
    ranges = {
        "JAN":  (f'{year-1}-12-26 00:00:00',    f'{year}-01-25 23:59:59'),
        "FEV":  (f'{year}-01-26 00:00:00',      f'{year}-02-25 23:59:59'),
        "MAR":  (f'{year}-02-26 00:00:00',      f'{year}-03-25 23:59:59'),
        "ABR":  (f'{year}-03-26 00:00:00',      f'{year}-04-25 23:59:59'),
        "MAIO": (f'{year}-04-26 00:00:00',      f'{year}-05-25 23:59:59'),
        "JUN":  (f'{year}-05-26 00:00:00',      f'{year}-06-25 23:59:59'),
        "JUL":  (f'{year}-06-26 00:00:00',      f'{year}-07-25 23:59:59'),
        "AGO":  (f'{year}-07-26 00:00:00',      f'{year}-08-25 23:59:59'),
        "SET":  (f'{year}-08-26 00:00:00',      f'{year}-09-25 23:59:59'),
        "OUT":  (f'{year}-09-26 00:00:00',      f'{year}-10-25 23:59:59'),
        "NOV":  (f'{year}-10-26 00:00:00',      f'{year}-11-25 23:59:59'),
        "DEZ":  (f'{year}-11-26 00:00:00',      f'{year}-12-31 23:59:59'),
    }
    ranges_acc = {
        "JAN":  (f'{year-1}-12-26 00:00:00',     f'{year}-01-25 23:59:59'),
        "FEV":  (f'{year-1}-12-26 00:00:00',     f'{year}-02-25 23:59:59'),
        "MAR":  (f'{year-1}-12-26 00:00:00',     f'{year}-03-25 23:59:59'),
        "ABR":  (f'{year-1}-12-26 00:00:00',     f'{year}-04-25 23:59:59'),
        "MAIO": (f'{year-1}-12-26 00:00:00',     f'{year}-05-25 23:59:59'),
        "JUN":  (f'{year-1}-12-26 00:00:00',     f'{year}-06-25 23:59:59'),
        "JUL":  (f'{year-1}-12-26 00:00:00',     f'{year}-07-25 23:59:59'),
        "AGO":  (f'{year-1}-12-26 00:00:00',     f'{year}-08-25 23:59:59'),
        "SET":  (f'{year-1}-12-26 00:00:00',     f'{year}-09-25 23:59:59'),
        "OUT":  (f'{year-1}-12-26 00:00:00',     f'{year}-10-25 23:59:59'),
        "NOV":  (f'{year-1}-12-26 00:00:00',     f'{year}-11-25 23:59:59'),
        "DEZ":  (f'{year-1}-12-26 00:00:00',     f'{year}-12-31 23:59:59'),
    }
    return ranges, ranges_acc
    
class App(object):
    
    VERSION = (1, 0, 0)
    THRESHOLD_KPI = 4
    MENTOR_SURVEYS = "mentor.xlsx"
    CSAT_SPREADSHEET = "csat.xlsx"
    PERIODOS = [ "JAN", "FEV", "MAR", "ABR", "MAIO", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ" ]
    RANGES = {
        "JAN":  ('2019-12-26 00:00:00', '2020-01-25 23:59:59'),
        "FEV":  ('2020-01-26 00:00:00', '2020-02-25 23:59:59'),
        "MAR":  ('2020-02-26 00:00:00', '2020-03-25 23:59:59'),
        "ABR":  ('2020-03-26 00:00:00', '2020-04-25 23:59:59'),
        "MAIO": ('2020-04-26 00:00:00', '2020-05-25 23:59:59'),
        "JUN":  ('2020-05-26 00:00:00', '2020-06-25 23:59:59'),
        "JUL":  ('2020-06-26 00:00:00', '2020-07-25 23:59:59'),
        "AGO":  ('2020-07-26 00:00:00', '2020-08-25 23:59:59'),
        "SET":  ('2020-08-26 00:00:00', '2020-09-25 23:59:59'),
        "OUT":  ('2020-09-26 00:00:00', '2020-10-25 23:59:59'),
        "NOV":  ('2020-10-26 00:00:00', '2020-11-25 23:59:59'),
        "DEZ":  ('2020-11-26 00:00:00', '2020-12-31 23:59:59'),
    }
    RANGES_ACC = {
        "JAN":  ('2019-12-26 00:00:00', '2020-01-25 23:59:59'),
        "FEV":  ('2019-12-26 00:00:00', '2020-02-25 23:59:59'),
        "MAR":  ('2019-12-26 00:00:00', '2020-03-25 23:59:59'),
        "ABR":  ('2019-12-26 00:00:00', '2020-04-25 23:59:59'),
        "MAIO": ('2019-12-26 00:00:00', '2020-05-25 23:59:59'),
        "JUN":  ('2019-12-26 00:00:00', '2020-06-25 23:59:59'),
        "JUL":  ('2019-12-26 00:00:00', '2020-07-25 23:59:59'),
        "AGO":  ('2019-12-26 00:00:00', '2020-08-25 23:59:59'),
        "SET":  ('2019-12-26 00:00:00', '2020-09-25 23:59:59'),
        "OUT":  ('2019-12-26 00:00:00', '2020-10-25 23:59:59'),
        "NOV":  ('2019-12-26 00:00:00', '2020-11-25 23:59:59'),
        "DEZ":  ('2019-12-26 00:00:00', '2020-12-31 23:59:59'),
    }
    
    def __init__(self, dir_csat, start, end):
        self.dir_csat = dir_csat
        self.start = start
        self.end = end
    
    def read_mesas(self):
        return [ None ] + util.read_mesas(self.dir_csat)
        
    def read_pesquisas(self):
        logger.info('recuperando dados da planilha de pesquisas de satisfação')
        currdir = os.getcwd()
        try:
            os.chdir(self.dir_csat)
            return pd.read_excel(config.SURVEYS_SPREADSHEET)
        finally:
            os.chdir(currdir)
    
    def read_pesquisas_mentor(self):
        logger.info('recuperando dados da planilha de pesquisas de satisfação do Mentor')
        currdir = os.getcwd()
        try:
            def conv_date(date):
                if date == "" or date is None or pd.isna(date):
                    return None
                return str(date)
            
            os.chdir(self.dir_csat)
            df =  pd.read_excel(self.MENTOR_SURVEYS)
            df[ 'Incidente Criado em'         ] = df[ 'Incidente Criado em'         ].apply(conv_date)
            df[ 'Última Data de Resolução'    ] = df[ 'Última Data de Resolução'    ].apply(conv_date)
            df[ 'Data de Fechamento'          ] = df[ 'Data de Fechamento'          ].apply(conv_date)
            df[ 'Data de criação da pesquisa' ] = df[ 'Data de criação da pesquisa' ].apply(conv_date)
            df[ 'Data da Resposta'            ] = df[ 'Data da Resposta'            ].apply(conv_date)
            return df
        finally:
            os.chdir(currdir)
    
    def calc_kpi(self, mesa, start_date, end_date, click_df, mentor_df):
        assert start_date <= end_date
        if mesa is None:
            click_df = click_df[ click_df[ 'data_resposta' ].between(start_date, end_date) ].copy()
            mentor_df = mentor_df[ mentor_df[ 'Data da Resposta' ].between(start_date, end_date) ].copy()
        else:
            click_df = click_df[ ( click_df[ 'mesa_acao' ] == mesa ) & 
                                 ( click_df[ 'data_resposta' ].between(start_date, end_date) ) ].copy()
            mentor_df = mentor_df[ ( mentor_df[ 'Grupo Designado' ] ==  mesa ) & 
                                   ( mentor_df[ 'Data da Resposta' ].between(start_date, end_date) ) ].copy()
        
        non_breached_click  = len( click_df[  click_df[ 'avaliacao'      ].ge(self.THRESHOLD_KPI) ])
        breached_click      = len( click_df[  click_df[ 'avaliacao'      ].lt(self.THRESHOLD_KPI) ])
        non_breached_mentor = len(mentor_df[ mentor_df[ 'Nota Questão A' ].ge(self.THRESHOLD_KPI) ])
        breached_mentor     = len(mentor_df[ mentor_df[ 'Nota Questão A' ].lt(self.THRESHOLD_KPI) ])
        #print(mesa, start_date, non_breached_mentor, breached_mentor)
        non_breached        = non_breached_click + non_breached_mentor
        breached            = breached_click + breached_mentor
        
        if (non_breached + breached) == 0:
            kpi = None
        else:
            kpi = (non_breached / (non_breached + breached)) * 100.0
        return kpi, breached + non_breached
        
    def generate_table(self, mesas, pesquisas_df, pesquisas_mentor_df, acc):
        if acc:
            logger.info("generating ACC CSAT table")
            ranges = self.RANGES_ACC
        else:
            logger.info("generating CSAT table")
            ranges = self.RANGES
        data = {
            "MESA"     : [],
            "JAN"      : [],
            "FEV"      : [],
            "MAR"      : [],
            "ABR"      : [],
            "MAIO"     : [],
            "JUN"      : [],
            "JUL"      : [],
            "AGO"      : [],
            "SET"      : [],
            "OUT"      : [],
            "NOV"      : [],
            "DEZ"      : [],
            "JAN Qtd"  : [],
            "FEV Qtd"  : [],
            "MAR Qtd"  : [],
            "ABR Qtd"  : [],
            "MAIO Qtd" : [],
            "JUN Qtd"  : [],
            "JUL Qtd"  : [],
            "AGO Qtd"  : [],
            "SET Qtd"  : [],
            "OUT Qtd"  : [],
            "NOV Qtd"  : [],
            "DEZ Qtd"  : [],
        }
        for mesa in mesas:
            data[ "MESA" ].append(mesa)
            for periodo in self.PERIODOS:
                start_date, end_date = ranges[ periodo ]
                kpi, qtd = self.calc_kpi(mesa, start_date, end_date, pesquisas_df, pesquisas_mentor_df)
                data[ periodo ].append(kpi)
                data[ f"{periodo} Qtd" ].append(qtd)
        return pd.DataFrame(data)
        
    def _date_to_period(self, dt):
        if pd.isna(dt):
            return "XXXXXX"
        for periodo, begin_end in self.RANGES.items():
            begin, end = begin_end
            survey_date = util.unparse_date(dt) + " 00:00:00"
            if begin <= survey_date <= end:
                return periodo
        #logger.warning("invalid date %s", util.unparse_date(dt))
        #print(begin, util.unparse_date(dt), end)
        #assert 1 == 2 # TODO: handle out of range dates
        return "XXXXXX"
        
    def generate_controle(self, pesquisas_df, min_surveys, by_tecnico=False):
        logger.info("generating monthly control table")
        data = {}
        for row in pesquisas_df.itertuples():
            mesa          = row.mesa_acao
            chave_usuario = row.chave_usuario
            nome_usuario  = row.nome_usuario
            if by_tecnico:
                chave_tecnico = row.chave_tecnico
                nome_tecnico  = row.nome_tecnico
                key = (mesa, chave_usuario, nome_usuario, chave_tecnico, nome_tecnico)
            else:
                key = (mesa, chave_usuario, nome_usuario)
            qtd = 1
            if pd.isna(row.data_resposta):
                ruim = 0
                boa = 0
            else:
                ruim = 1 if row.avaliacao < self.THRESHOLD_KPI else 0
                boa = 1 if row.avaliacao >= self.THRESHOLD_KPI else 0
            if key not in data:
                data[ key ] = { 
                    'qtd'               : 0,       
                    'avaliacoes_ruins'  : 0,
                    'avaliacoes_boas'   : 0,
                    'resp_janeiro'      : 0,
                    'resp_fevereiro'    : 0,
                    'resp_março'        : 0,
                    'resp_abril'        : 0,
                    'resp_maio'         : 0,
                    'resp_junho'        : 0,
                    'resp_julho'        : 0,
                    'resp_agosto'       : 0,
                    'resp_setembro'     : 0,
                    'resp_outubro'      : 0,
                    'resp_novembro'     : 0,
                    'resp_dezembro'     : 0,
                }
            data[ key ][ 'qtd'              ] += 1
            data[ key ][ 'avaliacoes_ruins' ] += ruim
            data[ key ][ 'avaliacoes_boas'  ] += boa
            data[ key ][ 'resp_janeiro'     ] += 1 if self._date_to_period(row.data_resposta) == "JAN"  else 0
            data[ key ][ 'resp_fevereiro'   ] += 1 if self._date_to_period(row.data_resposta) == "FEV"  else 0
            data[ key ][ 'resp_março'       ] += 1 if self._date_to_period(row.data_resposta) == "MAR"  else 0
            data[ key ][ 'resp_abril'       ] += 1 if self._date_to_period(row.data_resposta) == "ABR"  else 0
            data[ key ][ 'resp_maio'        ] += 1 if self._date_to_period(row.data_resposta) == "MAIO" else 0
            data[ key ][ 'resp_junho'       ] += 1 if self._date_to_period(row.data_resposta) == "JUN"  else 0
            data[ key ][ 'resp_julho'       ] += 1 if self._date_to_period(row.data_resposta) == "JUL"  else 0
            data[ key ][ 'resp_agosto'      ] += 1 if self._date_to_period(row.data_resposta) == "AGO"  else 0
            data[ key ][ 'resp_setembro'    ] += 1 if self._date_to_period(row.data_resposta) == "SET"  else 0
            data[ key ][ 'resp_outubro'     ] += 1 if self._date_to_period(row.data_resposta) == "OUT"  else 0
            data[ key ][ 'resp_novembro'    ] += 1 if self._date_to_period(row.data_resposta) == "NOV"  else 0
            data[ key ][ 'resp_dezembro'    ] += 1 if self._date_to_period(row.data_resposta) == "DEZ"  else 0
        
        if by_tecnico:
            result = { 
                'mesa'              : [], 
                'chave_usuario'     : [], 
                'nome_usuario'      : [], 
                'chave_tecnico'     : [], 
                'nome_tecnico'      : [], 
                'qtd'               : [], 
                'avaliacoes_ruins'  : [], 
                'avaliacoes_boas'   : [],
                'resp_janeiro'      : [],
                'resp_fevereiro'    : [],
                'resp_março'        : [],
                'resp_abril'        : [],
                'resp_maio'         : [],
                'resp_junho'        : [],
                'resp_julho'        : [],
                'resp_agosto'       : [],
                'resp_setembro'     : [],
                'resp_outubro'      : [],
                'resp_novembro'     : [],
                'resp_dezembro'     : [],
            }
        else:
            result = { 
                'mesa'              : [], 
                'chave_usuario'     : [], 
                'nome_usuario'      : [], 
                'qtd'               : [], 
                'avaliacoes_ruins'  : [], 
                'avaliacoes_boas'   : [],
                'resp_janeiro'      : [],
                'resp_fevereiro'    : [],
                'resp_março'        : [],
                'resp_abril'        : [],
                'resp_maio'         : [],
                'resp_junho'        : [],
                'resp_julho'        : [],
                'resp_agosto'       : [],
                'resp_setembro'     : [],
                'resp_outubro'      : [],
                'resp_novembro'     : [],
                'resp_dezembro'     : [],
                
            }
        for key, value in data.items():
            if value[ 'qtd' ] < min_surveys:
                continue
            if by_tecnico:
                (mesa, chave_usuario, nome_usuario, chave_tecnico, nome_tecnico) = key
            else:
                (mesa, chave_usuario, nome_usuario) = key
            result[ 'mesa'              ].append(mesa)
            result[ 'chave_usuario'     ].append(chave_usuario)
            result[ 'nome_usuario'      ].append(nome_usuario)
            if by_tecnico:
                result[ 'chave_tecnico' ].append(chave_tecnico)
                result[ 'nome_tecnico'  ].append(nome_tecnico)
            result[ 'qtd'               ].append(value[ 'qtd'               ])
            result[ 'avaliacoes_ruins'  ].append(value[ 'avaliacoes_ruins'  ])
            result[ 'avaliacoes_boas'   ].append(value[ 'avaliacoes_boas'   ])
            result[ 'resp_janeiro'      ].append(value[ 'resp_janeiro'      ])
            result[ 'resp_fevereiro'    ].append(value[ 'resp_fevereiro'    ])
            result[ 'resp_março'        ].append(value[ 'resp_março'        ])
            result[ 'resp_abril'        ].append(value[ 'resp_abril'        ])
            result[ 'resp_maio'         ].append(value[ 'resp_maio'         ])
            result[ 'resp_junho'        ].append(value[ 'resp_junho'        ])
            result[ 'resp_julho'        ].append(value[ 'resp_julho'        ])
            result[ 'resp_agosto'       ].append(value[ 'resp_agosto'       ])
            result[ 'resp_setembro'     ].append(value[ 'resp_setembro'     ])
            result[ 'resp_outubro'      ].append(value[ 'resp_outubro'      ])
            result[ 'resp_novembro'     ].append(value[ 'resp_novembro'     ])
            result[ 'resp_dezembro'     ].append(value[ 'resp_dezembro'     ])
            
            
            
        result_df = pd.DataFrame(result)
        result_df.sort_values(['qtd', 'avaliacoes_ruins', 'avaliacoes_boas'], ascending=False, inplace=True, ignore_index=True)
        return result_df
        
    def open_spreadsheet(self):
        logger.info("opening KPI spreadsheet")
        ks = os.path.join(self.dir_csat, "__" + self.CSAT_SPREADSHEET)
        if os.path.exists(ks):
            logger.warning("KPI spreadsheet already exists. Deleting it")
            os.unlink(ks)
        return pd.ExcelWriter(ks, datetime_format=None)   
    
    def save(self, pesquisas_df, pesquisas_mentor_df, csat_df, csat_acc_df, controle_df, controle_by_tecnico_df):
        logger.info("saving output spreadsheet")
        with self.open_spreadsheet() as xw:
            csat_acc_df.to_excel(xw, sheet_name="CSAT", index=False)
            csat_df.to_excel(xw, sheet_name="CSAT - Mês", index=False)
            controle_df.to_excel(xw, sheet_name="CONTROLE_RESPOSTAS", index=False)
            controle_by_tecnico_df.to_excel(xw, sheet_name="CONTROLE_RESPOSTAS_TECNICO", index=False)
            pesquisas_df.to_excel(xw, sheet_name="PESQUISAS", index=False)
            pesquisas_mentor_df.to_excel(xw, sheet_name="PESQUISAS_MENTOR", index=False)
            
    def run(self):
        try:
            logger.info('runn4 - versão %d.%d.%d', *self.VERSION)
            dump_surveys.App(self.dir_csat, self.start, self.end, unanswered=True, delspotfire=True).run()
            mesas = self.read_mesas()
            pesquisas_df = self.read_pesquisas()
            pesquisas_mentor_df = self.read_pesquisas_mentor()
            csat_df = self.generate_table(mesas, pesquisas_df, pesquisas_mentor_df, acc=False)
            csat_acc_df = self.generate_table(mesas, pesquisas_df, pesquisas_mentor_df, acc=True)
            controle_df = self.generate_controle(pesquisas_df, min_surveys=0, by_tecnico=False)
            controle_by_tecnico_df = self.generate_controle(pesquisas_df, min_surveys=0, by_tecnico=True)
            self.save(pesquisas_df, pesquisas_mentor_df, csat_df, csat_acc_df, controle_df, controle_by_tecnico_df)
            logger.info("finished")
        except:
            logger.exception('an error has occurred')
            raise
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_csat', type=str, help='diretório CSAT')
    parser.add_argument('start_date', type=str, help='start date')
    parser.add_argument('end_date', type=str, help='end date')
    args = parser.parse_args()
    ranges, ranges_acc = build_ranges(args.end_date)
    App.RANGES = ranges
    App.RANGES_ACC = ranges_acc
    app = App(args.dir_csat, args.start_date, args.end_date)
    app.run()
    