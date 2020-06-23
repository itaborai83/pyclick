import pandas as pd
import pyclick.n4sap.models as models

class Peso30(models.N4SapKpi):
    
    KPI_NAME    = "PESO30"
    SLA         = "N/A"
    
    def __init__(self):
        super().__init__()
        self.numerator = 0
        self.denominator = 0
        self.details = {
            'violacao'      : [],
            'incidente'     : [],
            'categoria'     : [],
            'prazo_m'       : [],
            'duracao_m'     : [],
            'pendencia_m'   : []
        }
        self.mesas_idx = {}
        
    def update_details(self, inc, breached, categoria, prazo_m, duration_m, pendencia_m):
        self.details[ 'violacao'  ].append('S' if breached else 'N')
        self.details[ 'incidente' ].append(inc.id_chamado)
        self.details[ 'categoria' ].append(categoria)
        self.details[ 'prazo_m'   ].append(prazo_m)
        self.details[ 'duracao_m' ].append(duration_m)
        self.details[ 'pendencia_m' ].append(pendencia_m)
                                                          
    def get_details(self):
        return pd.DataFrame(self.details)
    
    def get_description(self):
        if self.denominator == 0:
            msg = "Nenhum incidente escalado aberto"
        else:
            msg = f"{self.numerator} inc.s estourados / {self.denominator} incidentes escalados"
        return msg    
        
    def calc_duration(self, inc):
        return inc.calc_duration_mesas(self.MESA_ESCALADOS)
    
    def calcular_prazo(self, inc):
        categoria = self.categorizar(inc)
        if categoria == 'ATENDER - TAREFA':
            return 5 * 9 * 60
        elif categoria == 'CORRIGIR':
            return 15 * 9 * 60
        elif categoria == 'ORIENTAR':
            return 3 * 9 * 60
        else:
            assert 1 == 2 # should not happen

    def evaluate(self, click, start_dt, end_dt):
        super().evaluate(click)
        mesa = click.get_mesa(self.MESA_ESCALADOS)
        if mesa is None:
            return
        for inc in mesa.get_incidentes():
            if inc.id_chamado.startswith("S"):
                continue
            assert inc.status == 'ABERTO'
            categoria = self.categorizar(inc)
            prazo_m = self.calcular_prazo(inc)
            duration_m = self.calc_duration(inc)
            pendencia_m = inc.calc_pendencia_mesas([ self.MESA_ESCALADOS ])
            breached = (duration_m + pendencia_m) > prazo_m
            self.denominator += 1
            self.numerator += 1 if breached else 0            
            self.update_details(inc, breached, categoria, prazo_m, duration_m, pendencia_m)
    
    def get_result(self):
        msg = self.get_description()
        if self.denominator == 0:
            return None, msg
        else:
            result = 100.0 * (self.numerator / self.denominator)
            return result, msg