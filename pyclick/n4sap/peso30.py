import pandas as pd
import pyclick.n4sap.models as models

class Peso30(models.N4SapKpi):
    
    KPI_NAME         = "PESO30"
    SLA              = "N/A"
    PRAZO_CORRIGIR_M = 72 * 60
    PRAZO_ORIENTAR_M = 40 * 60
    PRAZO_REALIZAR_M = 36 * 60

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
            
    def update_details(self, inc, breached, categoria, prazo_m, duration_m, pendencia_m):
        for atrib in inc.atribuicoes:
            if atrib.mesa not in self.MESAS_CONTRATO:
                continue
            self.details[ 'violacao'       ].append(self.BREACHED_MAPPING[ breached ])
            self.details[ 'id_chamado'     ].append(inc.id_chamado)
            self.details[ 'chamado_pai'    ].append(inc.chamado_pai)
            self.details[ 'categoria'      ].append(categoria)
            self.details[ 'prazo'          ].append(prazo_m)
            self.details[ 'duracao'        ].append(duration_m + pendencia_m)
            self.details[ 'ultima_mesa'    ].append(inc.mesa_atual)
            self.details[ 'ultimo_status'  ].append(inc.status)
            self.details[ 'atribuicao'     ].append(atrib.seq)
            self.details[ 'mesa'           ].append(atrib.mesa)
            self.details[ 'ultima_atrib'   ].append('S' if inc.ultima_atribuicao.seq == atrib.seq else 'N')
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
            msg = "Nenhum incidente peso 30 processado"
        else:
            msg = f"{self.numerator} violações / {self.denominator} incidentes escalados"
        return msg

    def has_assignment_within_period(self, inc, start_dt, end_dt):
        for atrib in inc.get_atribuicoes_mesas([ self.MESA_ESCALADOS ]):
            if atrib.intersects_with(start_dt, end_dt):
                return True
    
    def evaluate(self, click, start_dt, end_dt):
        mesa = click.get_mesa(self.MESA_ESCALADOS)
        if mesa is None:
            return
        for inc in mesa.get_seen_incidentes():
            if inc.id_chamado.startswith("S"):
                continue
            if not self.has_assignment_within_period(inc, start_dt, end_dt):
                continue
            categoria = self.categorizar(inc)
            prazo_m = self.calcular_prazo(inc, self.MESA_ESCALADOS)
            duration_m = self.calc_duration_mesas(inc, [ self.MESA_ESCALADOS ])
            pendencia_m = self.calc_pendencia_mesas(inc, [ self.MESA_ESCALADOS ])
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
            