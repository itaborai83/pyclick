import os
import pandas as pd

import pyclick.util as util
import pyclick.config as config
import pyclick.n4sap.config as n4_config
import pyclick.kpis as kpis

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('kpis2')

class N4Handler(kpis.Handler):
    MESAS = n4_config.MESAS[:]

class PrpEntry(object):
    
    PRAZO_PRP = 9 * 60
    
    def __init__(self, row):
        self.id_chamado     = row.ID_CHAMADO
        self.chamado_pai    = row.CHAMADO_PAI
        self.start_dt       = row.DATA_INICIO_ACAO
        self.end_dt         = row.DATA_INICIO_ACAO
        self.status         = None
        self.ultima_acao    = None
        self.duracao        = 0
        self.priorizacoes   = 0
        self.despriorizacoes = 0
        self.rows           = []
    
    def update(self, row):
        self.end_dt         = row.DATA_INICIO_ACAO
        self.duracao        += (0 if row.PENDENCIA == 'S' else row.DURACAO_M)
        self.status         = row.STATUS_DE_EVENTO
        self.ultima_acao    = row.ULTIMA_ACAO_NOME
        self.rows.append(row)

class PrpHandler(N4Handler):

    def __init__(self):
        self.watch_list = {}
        self.entries = {}
    
    def start_watching(self, row):
        if row.ID_CHAMADO not in self.entries:
            self.entries[ row.ID_CHAMADO ] = PrpEntry(row)
        entry = self.entries[ row.ID_CHAMADO ]
        entry.priorizacoes += 1
        self.watch_list[ row.ID_CHAMADO ] = entry
        return entry
        
    def stop_watching(self, row, desprioriza=False):
        entry = self.watch_list[ row.ID_CHAMADO ]
        del self.watch_list[ row.ID_CHAMADO ]
        if desprioriza:
            entry.despriorizacoes += 1
        
    def process_action(self, row):
        if row.MESA_ATUAL == 'N4-SAP-SUSTENTACAO-PRIORIDADE' and row.ID_CHAMADO not in self.watch_list:
            entry = self.start_watching(row)
        
        if row.ID_CHAMADO not in self.watch_list:
            return
        
        entry = self.watch_list[ row.ID_CHAMADO ]
        if row.MESA_ATUAL == 'N4-SAP-SUSTENTACAO-PRIORIDADE':
            entry.update(row)
        
        elif row.MESA_ATUAL != 'N4-SAP-SUSTENTACAO-PRIORIDADE':
            self.stop_watching(row, desprioriza=True)
            
    def end_event(self, row):
        if row.ID_CHAMADO in self.watch_list:
            self.stop_watching(row, desprioriza=False)
        
    def end(self):
        mapping = {}
        for entry in self.entries.values():
            mapping[ entry.id_chamado ] = entry
            if entry.id_chamado.startswith('S'):
                entry.duracao = 0 # clear service request duration
        for entry in self.entries.values():
            if not entry.id_chamado.startswith('T'):
                continue
            parent = mapping.get(entry.chamado_pai, None)
            if parent:
                parent.duracao += entry.duracao
        
    def compute_kpi(self):
        df = self.get_kpi_entries()
        if len(df) == 0:
            return 0.0
        kpi = sum([ 1.0 if e.duracao > self.PRAZO_PRP else 0.0 ]) / len(df)
        return kpi * 100.0
    
    def get_kpi_details(self):
        entries = [ e for e in self.entries.values() if not e.id_chamado.startswith('T') and e.status != 'Aberto']
        df = pd.DataFrame({
            'id_chamado'        : [ e.id_chamado                    for e in entries ],
            'chamado_pai'       : [ e.chamado_pai                   for e in entries ],
            'status'            : [ e.status                        for e in entries ],
            'abertura_chamado'  : [ util.parse_datetime(e.rows[ -1 ].DATA_ABERTURA_CHAMADO) for e in entries ],
            'fechamento_chamado': [ util.parse_datetime(e.rows[ -1 ].DATA_RESOLUCAO_CHAMADO) for e in entries ],
            'priorizacoes'      : [ e.priorizacoes                  for e in entries ],
            'despriorizacoes'   : [ e.despriorizacoes               for e in entries ],
            'data_inicio'       : [ util.parse_datetime(e.start_dt) for e in entries ],
            'data_fim'          : [ util.parse_datetime(e.end_dt)   for e in entries ],
            'ultima_acao'       : [ e.status                        for e in entries ],
            'duracao'           : [ e.duracao                       for e in entries ]
        })
        return df
