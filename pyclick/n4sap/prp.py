import pandas as pd
import pyclick.n4sap.models as models        

class Prp(models.N4SapKpi):
    
    KPI_NAME    = "PRP"
    PRAZO_M     = 9 * 60
    SLA         = 10.0
    
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
            'ultima_atrib'      : [],
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
            if atrib.mesa not in self.MESAS_CONTRATO:
                continue
            self.details[ 'violacao'        ].append(self.BREACHED_MAPPING[ breached ])
            self.details[ 'id_chamado'      ].append(inc.id_chamado)
            self.details[ 'chamado_pai'     ].append(inc.chamado_pai)
            self.details[ 'categoria'       ].append(categoria)
            self.details[ 'categoria_click' ].append(inc.categoria)
            self.details[ 'prazo'           ].append(inc.prazo)
            self.details[ 'duracao'         ].append(duration_m)
            self.details[ 'ultima_mesa'     ].append(inc.mesa_atual)
            self.details[ 'ultimo_status'   ].append(inc.status)
            self.details[ 'atribuicao'      ].append(atrib.seq)
            self.details[ 'mesa'            ].append(atrib.mesa)
            self.details[ 'ultima_atrib'    ].append('S' if inc.ultima_atribuicao.seq == atrib.seq else 'N')
            self.details[ 'entrada'         ].append(atrib.entrada)
            self.details[ 'status_entrada'  ].append(atrib.status_entrada)
            self.details[ 'saida'           ].append(atrib.saida)
            self.details[ 'status_saida'    ].append(atrib.status_saida)
            if inc.id_chamado.startswith('S'):
                self.details[ 'duracao_m'      ].append(None)
                self.details[ 'pendencia_m'    ].append(None)
            else:
                self.details[ 'duracao_m'      ].append(atrib.duracao_m)
                self.details[ 'pendencia_m'    ].append(atrib.pendencia_m)
            
            
    def get_details(self):
        return pd.DataFrame(self.details)
    
    def get_description(self):
        if self.denominator == 0:
            msg = "Nenhum incidente peso 35 processado"
        else:
            msg = f"{self.numerator} violações / {self.denominator} incidentes"
        return msg
    
    def has_assignment_within_period(self, inc, start_dt, end_dt):
        for atrib in inc.get_atribuicoes_mesas([ self.MESA_PRIORIDADE ]):
            if atrib.intersects_with(start_dt, end_dt):
                return True
        return False
        
    def evaluate(self, click, start_dt, end_dt):
        mesa = click.get_mesa(self.MESA_PRIORIDADE)
        if mesa is None:
            return
        for inc in mesa.get_seen_incidentes():
            if inc.id_chamado.startswith("T"):
                continue
            if not self.has_assignment_within_period(inc, start_dt, end_dt):
                continue
            prazo = self.calcular_prazo(inc, self.MESA_PRIORIDADE)
            assert prazo == self.PRAZO_M            
            duration_m = click.calc_duration_mesas(inc.id_chamado, [ self.MESA_PRIORIDADE ])
            breached = duration_m > prazo
            if inc.status == 'ABERTO' and not breached:
                continue
            self.numerator   += (1 if breached else 0)
            self.denominator += 1
            self.update_details(inc, duration_m, breached)
            if inc.id_chamado in click.children_of:
                for child_id in click.children_of[ inc.id_chamado ]:
                    child = click.get_incidente(child_id)
                    self.update_details(child, duration_m, breached=None)

    def get_result(self):
        msg = self.get_description()
        if self.denominator == 0:
            return None, msg
        else:
            result = 100.0 * (self.numerator / self.denominator)
            return result, msg
            
class PrpV2(Prp):
        
    def __init__(self, incsrv):
        assert incsrv is not None
        super().__init__(incsrv=incsrv)
            
    def update_details(self, inc, duration_m, breached):
        assert not inc.id_chamado.startswith('S')
        super().update_details(inc, duration_m, breached)
    
    def has_assignment_within_period(self, inc, start_dt, end_dt):
        for atrib in inc.get_atribuicoes_mesas([ self.MESA_PRIORIDADE ]):
            if atrib.intersects_with(start_dt, end_dt):
                return True
        return False
        
    def evaluate(self, click, start_dt, end_dt):
        mesa = click.get_mesa(self.MESA_PRIORIDADE)
        if mesa is None:
            return
        for inc in mesa.get_seen_incidentes():
            categoria = self.categorizar(inc)
            if categoria == 'ATENDER':
                continue
            if not self.has_assignment_within_period(inc, start_dt, end_dt):
                continue
            prazo = self.calcular_prazo(inc, self.MESA_PRIORIDADE)
            assert prazo == self.PRAZO_M
            duration_m = self.calc_duration_mesas(inc, [ self.MESA_PRIORIDADE ])
            breached = duration_m > prazo
            if inc.status == 'ABERTO' and not breached:
                if inc.mesa_atual == self.MESA_PRIORIDADE:
                    continue
            self.numerator   += (1 if breached else 0)
            self.denominator += 1
            self.update_details(inc, duration_m, breached)
            
