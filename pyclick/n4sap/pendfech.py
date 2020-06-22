import pandas as pd
import pyclick.n4sap.models as models
import pyclick.config as config

class PendenteFechado(models.N4SapKpi):
    
    KPI_NAME    = "PEND.FECH."
    SLA         = "N/A"
    
    def __init__(self):
        super().__init__()
        self.numerator = 0
        self.denominator = 0
        self.details = {
            'violacao'      : [],
            'incidente'     : [],
            'mesa'          : [],
            'categoria'     : [],    
            'duracao_m'     : [],
            'pendencia_m'   : [],
            
        }
        self.mesas_idx = {}
        
    def update_details(self, inc, breached):
        categoria = self.categorizar(inc)
        self.details[ 'violacao'    ].append('S' if breached else 'N')
        self.details[ 'incidente'   ].append(inc.id_chamado)
        self.details[ 'mesa'        ].append(inc.mesa_atual)
        self.details[ 'categoria'   ].append(categoria)
        self.details[ 'duracao_m'   ].append(0)
        self.details[ 'pendencia_m' ].append(0)
        for atrib in inc.get_atribuicoes_mesas(self.MESAS_CONTRATO):
            self.details[ 'duracao_m'   ][ -1 ] += atrib.duracao_m
            self.details[ 'pendencia_m' ][ -1 ] += atrib.pendencia_m
            
    def get_details(self):
        return pd.DataFrame(self.details)
    
    def get_description(self):
        if self.denominator == 0:
            msg = "Nenhum incidente processado"
        else:
            msg = f"{self.numerator} inc.s pend. fech. / {self.denominator} incidentes"
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
            for inc in mesa.get_seen_incidentes():
                if inc.id_chamado.startswith("S"):
                    continue
                if not self.has_assignment_within_period(inc, start_dt, end_dt):
                    continue
                if mesa_name != inc.mesa_atual:
                    continue
                if inc.status == 'ABERTO':
                    continue
                acao = inc.ultima_acao_aberta
                breached = acao.pendencia == 'S' and acao.acao_nome not in config.STOP_CLOCK_ACTIONS
                self.denominator += 1
                self.numerator += 1 if breached else 0
                self.update_details(inc, breached)
    
    def get_result(self):
        msg = self.get_description()
        if self.denominator == 0:
            return None, msg
        else:
            result = 100.0 * (self.numerator / self.denominator)
            return result, msg