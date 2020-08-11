import math
import pandas as pd
import pyclick.n4sap.models as models        

class Ids(models.N4SapKpi):
    
    KPI_NAME    = "IDS"
    SLA         = 170.0
    
    def __init__(self):
        super().__init__()
        self.reset()
        
    def reset(self):
        self.numerator = 0
        self.denominator = 0
        self.details = {
            'fator_ids'         : [],
            'id_chamado'        : [],
            'chamado_pai'       : [],
            'categoria'         : [],
            'categoria_click'   : [],            
            'prazo'             : [],
            'prazo_click'       : [],
            'duracao'           : [],
            'ultima_mesa'       : [],
            'ultimo_status'     : [],
            'atribuicao'        : [],
            'mesa'              : [],
            'entrada'           : [],
            'status_entrada'    : [],
            'saida'             : [],
            'status_saida'      : [],
            'duracao_m'         : [],
            'pendencia_m'       : [],
        }
            
    def update_details(self, inc, prazo_m, duration_m, ids_factor):
        categoria = self.categorizar(inc)
        for atrib in inc.atribuicoes:
            if atrib.mesa not in self.MESAS_CONTRATO:
                continue
            self.details[ 'fator_ids'       ].append(ids_factor)
            self.details[ 'id_chamado'      ].append(inc.id_chamado)
            self.details[ 'chamado_pai'     ].append(inc.chamado_pai)
            self.details[ 'categoria'       ].append(categoria)
            self.details[ 'categoria_click' ].append(inc.categoria)            
            self.details[ 'prazo'           ].append(prazo_m)
            self.details[ 'prazo_click'     ].append(inc.prazo)
            self.details[ 'duracao'         ].append(duration_m)
            self.details[ 'ultima_mesa'     ].append(inc.mesa_atual)
            self.details[ 'ultimo_status'   ].append(inc.status)
            self.details[ 'atribuicao'      ].append(atrib.seq)
            self.details[ 'mesa'            ].append(atrib.mesa)
            self.details[ 'entrada'         ].append(atrib.entrada)
            self.details[ 'status_entrada'  ].append(atrib.status_entrada)
            self.details[ 'saida'           ].append(atrib.saida)
            self.details[ 'status_saida'    ].append(atrib.status_saida)
            self.details[ 'duracao_m'       ].append(atrib.duracao_m)
            self.details[ 'pendencia_m'     ].append(atrib.pendencia_m)
            
    def get_details(self):
        return pd.DataFrame(self.details)
    
    def get_description(self):
        if self.denominator == 0:
            msg = "Nenhum incidente aberto violando SLA"
        else:
            msg = f"{self.numerator} ids / {self.denominator} incidentes"
        return msg

    def has_assignment_within_period(self, inc, start_dt, end_dt):
        for atrib in inc.get_atribuicoes_mesas(self.MESAS_NAO_PRIORITARIAS):
            if atrib.intersects_with(start_dt, end_dt):
                return True
        return False
        
    def evaluate(self, click, start_dt, end_dt, mesa_filter=None):
        for mesa_name in self.MESAS_CONTRATO:
            mesa = click.get_mesa(mesa_name)
            if mesa is None:
                continue
            for inc in mesa.get_incidentes():
                inc = self.remap_mesas_by_last(inc, mesa_filter, self.MESAS_CONTRATO)
                if inc is None:
                    continue
                categoria = self.categorizar(inc)
                if categoria == 'ATENDER':
                    continue
                if not self.has_assignment_within_period(inc, start_dt, end_dt):
                    continue
                assert inc.status == 'ABERTO'
                categoria = self.categorizar(inc)
                prazo_m = self.calcular_prazo(inc, mesa_name)
                duration_m = self.calc_duration_mesas(inc, self.MESAS_CONTRATO)
                if duration_m < prazo_m:
                    continue
                ids = math.ceil(duration_m / (180.0 * 60))
                self.numerator   += ids
                self.denominator += 1
                self.update_details(inc, prazo_m, duration_m, ids)

        
    def get_result(self):
        msg = self.get_description()
        if self.denominator == 0:
            return None, msg
        else:
            result = 100.0 * (self.numerator / self.denominator)
            return result, msg            
