import pandas as pd
import pyclick.util as util        
import pyclick.n4sap.models as models

logger = util.get_logger('pro')

class Pro(models.N4SapKpi):
    
    KPI_NAME    = "PRO"
    PRAZO_M     = 27 * 60
    SLA         = 15.0
    
    def __init__(self, incsrv):
        super().__init__(incsrv=incsrv)
        self.reset()
        
    def reset(self):
        self.numerator = 0
        self.denominator = 0
        self.details = {
            'violacao'          : [],
            'id_chamado'        : [],
            'chamado_pai'       : [],
            'categoria'         : [],
            'categoria_click'   : [],
            'prazo'             : [],
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
            
    def update_details(self, inc, duration_m, breached):
        categoria = self.categorizar(inc)
        for atrib in inc.atribuicoes:
            if atrib.mesa not in self.MESAS_NAO_PRIORITARIAS:
                continue
            self.details[ 'violacao'        ].append(self.BREACHED_MAPPING[ breached ])
            self.details[ 'id_chamado'      ].append(inc.id_chamado)
            self.details[ 'chamado_pai'     ].append(inc.chamado_pai)
            self.details[ 'categoria'       ].append(categoria)
            self.details[ 'categoria_click' ].append(inc.categoria)
            self.details[ 'prazo'           ].append(self.PRAZO_M)
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
            msg = "Nenhum incidente orientar processado"
        else:
            msg = f"{self.numerator} violações / {self.denominator} incidentes"
        return msg

    def has_assignment_within_period(self, inc, start_dt, end_dt):
        for atrib in inc.get_atribuicoes_mesas(self.MESAS_NAO_PRIORITARIAS):
            if atrib.intersects_with(start_dt, end_dt):
                return True
        return False
        
    def evaluate(self, click, start_dt, end_dt, mesa_filter=None):
        for inc in click.get_incidentes():
            inc = self.remap_mesas_by_last(inc, mesa_filter, self.MESAS_CONTRATO)
            if inc is None:
                continue
            categoria = self.categorizar(inc)
            if categoria != "ORIENTAR":
                continue            
            if not inc.possui_atribuicoes(self.MESAS_NAO_PRIORITARIAS):
                continue
            if not self.has_assignment_within_period(inc, start_dt, end_dt):
                continue                
            # Prazo Peso 30 não está no contrato, logo não deve ser considerado para fins de prazo no PRO
            ultima_mesa_contrato = inc.get_latest_mesa_from(self.MESAS_NAO_PRIORITARIAS) 
            prazo_m = self.calcular_prazo(inc, ultima_mesa_contrato)
            if prazo_m != self.PRAZO_M:
                logger.error(f"prazos divergentes ORIENTAR p/ {inc.id_chamado}. Expected {self.PRAZO_M} / Actual { prazo_m } ")
            # Mesa de Peso 30 *deve* ser considerado para fins de duração no PRO
            duration_m = self.calc_duration_mesas(inc, self.MESAS_NAO_PRIORITARIAS)
            breached = duration_m > self.PRAZO_M
            if not breached and inc.status == 'ABERTO' and inc.mesa_atual in self.MESAS_NAO_PRIORITARIAS:
                continue            
            self.numerator   += (1 if breached else 0)
            self.denominator += 1
            self.update_details(inc, duration_m, breached)
            
    def get_result(self):
        msg = self.get_description()
        if self.denominator == 0:
            return None, msg
        else:
            result = 100.0 * (self.numerator / self.denominator)
            return result, msg
            
