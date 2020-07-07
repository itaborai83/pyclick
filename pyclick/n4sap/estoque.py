import pandas as pd
import pyclick.n4sap.models as models

class Estoque(models.N4SapKpi):
    
    KPI_NAME    = "ESTOQUE"
    SLA         = "N/A"
    
    def __init__(self):
        super().__init__()
        self.reset()
        
    def reset(self):
        self.count = 0
        self.details = {
            'id_chamado'        : [],
            'chamado_pai'       : [],
            'categoria'         : [],
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
        self.mesas_idx = {}
        
    def update_details(self, inc):
        categoria = self.categorizar(inc)
        duration_m = inc.calc_duration_mesas(self.MESAS_CONTRATO)
        pendencia_m = inc.calc_pendencia_mesas(self.MESAS_CONTRATO) 

        for atrib in inc.atribuicoes:
            if atrib.mesa not in self.MESAS_CONTRATO:
                continue
            self.details[ 'id_chamado'     ].append(inc.id_chamado)
            self.details[ 'chamado_pai'    ].append(inc.chamado_pai)
            self.details[ 'categoria'      ].append(categoria)
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
        
    def evaluate(self, click, start_dt, end_dt, mesa_filter=None):
        for mesa_name in self.MESAS_CONTRATO:
            mesa = click.get_mesa(mesa_name)
            if mesa is None:
                continue
            for inc in mesa.get_incidentes():
                inc = self.remap_mesas_by_last(inc, mesa_filter, self.MESAS_CONTRATO)
                if inc is None:
                    continue
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