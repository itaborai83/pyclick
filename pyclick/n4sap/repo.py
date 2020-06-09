import sqlite3
import pandas as pd
import pyclick.util as util
import pyclick.models as models
import pyclick.repo as repo


class RepoN4(repo.Repo):

    def __init__(self, conn):
        super().__init__(conn)
    
    def get_business_times(self):
        sql = "SELECT * FROM VW_TEMPO_UTIL_MESAS"
        return pd.read_sql(sql, self.conn)

    def get_pending_times(self):
        sql = "SELECT * FROM VW_TEMPO_PENDENCIAS_MESAS"
        return pd.read_sql(sql, self.conn)

    def get_surveys(self):
        sql = "SELECT * FROM PESQUISAS ORDER BY ID_PESQUISA"
        return pd.read_sql(sql, self.conn)
        
    def get_period(self):
        sql = "SELECT VALOR FROM PARAMS WHERE PARAM = 'HORA_INICIO_APURACAO'"
        start_dt = self.conn.execute(sql).fetchone()[ 0 ]
        sql = "SELECT VALOR FROM PARAMS WHERE PARAM = 'HORA_FIM_APURACAO'"
        end_dt = self.conn.execute(sql).fetchone()[ 0 ]
        return start_dt, end_dt
    
        
