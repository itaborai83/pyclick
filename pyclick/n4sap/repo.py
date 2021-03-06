import sqlite3
import pandas as pd
import pyclick.util as util
import pyclick.models as models
import pyclick.repo as repo

SQL_DASHBOARD_AGING = util.get_query('PORTAL__DASHBOARD_AGING')

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
        sql = """
            SELECT 	ID_PESQUISA
            ,       ID_CHAMADO
            ,       MESA_ACAO       AS 'mesa'
            ,       NOME_TECNICO    AS 'tecnico'
            ,       NOME_USUARIO    AS 'usuario'
            ,       DATA_RESPOSTA
            ,       AVALIACAO
            ,       MOTIVO
            ,       COMENTARIO
            FROM    PESQUISAS
            ORDER   BY ID_PESQUISA
        """
        return pd.read_sql(sql, self.conn)
        
    def get_period(self):
        sql = "SELECT VALOR FROM PARAMS WHERE PARAM = 'HORA_INICIO_APURACAO'"
        start_dt = self.conn.execute(sql).fetchone()[ 0 ]
        sql = "SELECT VALOR FROM PARAMS WHERE PARAM = 'HORA_FIM_APURACAO'"
        end_dt = self.conn.execute(sql).fetchone()[ 0 ]
        return start_dt, end_dt
    
    def get_aging_dashboard_data(self):
        return pd.read_sql(SQL_DASHBOARD_AGING, self.conn)
        
