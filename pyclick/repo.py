import sqlite3
import pandas as pd
import pyclick.util as util
import pyclick.models as models

SQL_LISTA_EVENTOS = util.get_query("KPI__LISTA_EVENTOS")

class Repo(object):

    def __init__(self, conn):
        self.conn = conn
    
    def load_events(self):
        c = self.conn.cursor()
        c.execute(SQL_LISTA_EVENTOS)
        results = []
        for row in c:
            evt = models.Event(
                id_chamado          = row[  0 ]
            ,   chamado_pai         = row[  1 ]
            ,   categoria           = row[  2 ]
            ,   oferta_catalogo     = row[  3 ]
            ,   prazo_oferta_m      = row[  4 ]
            ,   id_acao             = row[  5 ]
            ,   acao_nome           = row[  6 ]
            ,   pendencia           = row[  7 ]
            ,   mesa_atual          = row[  8 ]
            ,   data_acao           = row[  9 ]
            ,   data_fim_acao       = row[ 10 ]
            ,   duracao_m           = row[ 11 ]
            )
            results.append(evt)
        c.close()
        return results

    def load_relatorio_medicao(self):
        sql = "SELECT * FROM VW_REL_MEDICAO ORDER BY DATA_INICIO_ACAO, ID_CHAMADO, ID_ACAO"
        df = pd.read_sql(sql, self.conn)
        return df
        