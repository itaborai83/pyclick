import pandas as pd
import pyclick.n4sap.models as models        

class Prc(models.N4SapKpi):
    
    KPI_NAME    = "PRC"
    PRAZO_M     = 135 * 60
    SLA         = 25.0
    
    def __init__(self):
        super().__init__()
        self.reset()
        
    def reset(self):
        self.numerator = 0
        self.denominator = 0
        self.details = {
            'violacao'          : [],
            'id_chamado'        : [],
            'chamado_pai'       : [],
            'categoria'         : [],
            'prazo'             : [],
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
            
    def update_details(self, inc, breached):
        categoria = self.categorizar(inc)
        for atrib in inc.atribuicoes:
            if atrib.mesa not in self.MESAS_NAO_PRIORITARIAS_V2:
                continue
            self.details[ 'violacao'       ].append(self.BREACHED_MAPPING[ breached ])
            self.details[ 'id_chamado'     ].append(inc.id_chamado)
            self.details[ 'chamado_pai'    ].append(inc.chamado_pai)
            self.details[ 'categoria'      ].append(categoria)
            self.details[ 'prazo'          ].append(self.PRAZO_M)
            self.details[ 'ultima_mesa'    ].append(inc.mesa_atual)
            self.details[ 'ultimo_status'  ].append(inc.status)
            self.details[ 'atribuicao'     ].append(atrib.seq)
            self.details[ 'mesa'           ].append(atrib.mesa)
            self.details[ 'entrada'        ].append(atrib.entrada)
            self.details[ 'status_entrada' ].append(atrib.status_entrada)
            self.details[ 'saida'          ].append(atrib.saida)
            self.details[ 'status_saida'   ].append(atrib.status_saida)
            self.details[ 'duracao_m'      ].append(atrib.duracao_m)
            self.details[ 'pendencia_m'    ].append(atrib.pendencia_m)
            
    def get_details(self):
        return pd.DataFrame(self.details)
    
    def get_description(self):
        if self.denominator == 0:
            msg = "Nenhum incidente corrigir processado"
        else:
            msg = f"{self.numerator} violações / {self.denominator} incidentes"
        return msg

    def has_assignment_within_period(self, inc, start_dt, end_dt):
        for atrib in inc.get_atribuicoes_mesas(self.MESAS_NAO_PRIORITARIAS_V2):
            if atrib.intersects_with(start_dt, end_dt):
                return True
        return False
        
    def evaluate(self, click, start_dt, end_dt, mesa_filter=None):
        for inc in click.get_incidentes():
            inc = self.remap_mesas_by_last(inc, mesa_filter, self.MESAS_CONTRATO)
            if inc is None:
                continue
            categoria = self.categorizar(inc)
            if categoria != "CORRIGIR":
                continue
            if not inc.possui_atribuicoes(self.MESAS_NAO_PRIORITARIAS_V2):
                continue
            if not self.has_assignment_within_period(inc, start_dt, end_dt):
                continue
            ultima_mesa_contrato = inc.get_latest_mesa_from(self.MESAS_NAO_PRIORITARIAS_V2)
            prazo_m = self.calcular_prazo(inc, ultima_mesa_contrato)
            assert prazo_m == self.PRAZO_M
            duration_m = self.calc_duration_mesas(inc, self.MESAS_NAO_PRIORITARIAS_V2)
            breached = duration_m > prazo_m
            if inc.status == 'ABERTO' and not breached:
                continue            
            self.numerator   += (1 if breached else 0)
            self.denominator += 1
            self.update_details(inc, breached)

    def get_result(self):
        msg = self.get_description()
        if self.denominator == 0:
            return None, msg
        else:
            result = 100.0 * (self.numerator / self.denominator)
            return result, msg
            
