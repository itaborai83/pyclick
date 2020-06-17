import pandas as pd
import pyclick.n4sap.models as models

class Estoque(models.N4SapKpi):
    
    KPI_NAME    = "ESTOQUE"
    SLA         = "N/A"
    
    def __init__(self):
        super().__init__()
        self.count = 0
        self.details = {
            'mesa'              : [],
            'incidentes'        : [],
            'orientar'          : [],
            'corrigir'          : [],
            'atender'           : []
        }
        self.mesas_idx = {}
        
    def update_details(self, inc):
        mesa = inc.mesa_atual
        if mesa not in self.mesas_idx:
            idx = len(self.mesas_idx)
            self.mesas_idx[ mesa ] = idx
            self.details[ 'mesa'        ].append(mesa)
            self.details[ 'incidentes'  ].append(0)
            self.details[ 'orientar'    ].append(0)
            self.details[ 'corrigir'    ].append(0)
            self.details[ 'atender'     ].append(0)
        idx = self.mesas_idx[ mesa ]
        categoria = self.categorizar(inc)
        self.details[ 'incidentes' ][ idx ] += 1
        self.details[ 'orientar' ][ idx ]   += 1 if categoria == 'ORIENTAR' else 0
        self.details[ 'corrigir' ][ idx ]   += 1 if categoria == 'CORRIGIR' else 0
        self.details[ 'atender'  ][ idx ]   += 1 if categoria == 'ATENDER - TAREFA' else 0
                                                          
    def get_details(self):
        return pd.DataFrame(self.details)
    
    def get_description(self):
        if self.count == 0:
            msg = "Nenhum incidente no estoque"
        else:
            msg = f"{self.count} incidentes no estoque"
        return msg
    
    def has_assignment_within_period(self, inc, start_dt, end_dt):
        for atrib in inc.get_atribuicoes_mesas(self.MESAS_CONTRATO):
            if atrib.intersects_with(start_dt, end_dt):
                return True
        return False
        
    def evaluate(self, click, start_dt, end_dt):
        super().evaluate(click)
        for mesa_name in self.MESAS_CONTRATO:
            mesa = click.get_mesa(mesa_name)
            if mesa is None:
                continue
            for inc in mesa.get_incidentes():
                if inc.id_chamado.startswith("S"):
                    continue
                if not self.has_assignment_within_period(inc, start_dt, end_dt):
                    continue
                assert inc.status == 'ABERTO'
                self.count += 1
                self.update_details(inc)
    
    def get_result(self):
        msg = self.get_description()
        if self.count == 0:
            return None, msg
        else:
            result = self.count
            return result, msg