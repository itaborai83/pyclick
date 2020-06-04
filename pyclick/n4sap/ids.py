import math
import pandas as pd
import pyclick.n4sap.models as models        

class Ids(models.N4SapKpi):
    
    SLA     = 170.0
    
    def __init__(self):
        super().__init__()
        self.numerator = 0
        self.denominator = 0
        self.details = {
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
            
    def update_details(self, inc):
        categoria = self.categorizar(inc)
        prazo = self.calcular_prazo(inc)
        for atrib in inc.atribuicoes:
            if atrib.mesa not in self.MESAS_CONTRATO:
                continue
            self.details[ 'id_chamado'     ].append(inc.id_chamado)
            self.details[ 'chamado_pai'    ].append(inc.chamado_pai)
            self.details[ 'categoria'      ].append(categoria)
            self.details[ 'prazo'          ].append(prazo)
            self.details[ 'ultima_mesa'    ].append(inc.mesa_atual)
            self.details[ 'ultimo_status'  ].append(inc.status)
            self.details[ 'atribuicao'     ].append(atrib.seq)
            self.details[ 'mesa'           ].append(atrib.mesa)
            self.details[ 'entrada'        ].append(atrib.entrada)
            self.details[ 'status_entrada' ].append(atrib.status_entrada)
            self.details[ 'saida'          ].append(atrib.saida)
            self.details[ 'status_saida'   ].append(atrib.status_saida)
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
            msg = "Nenhum incidente aberto violando SLA"
        else:
            msg = f"{self.numerator} ids / {self.denominator} incidentes"
        return msg
        
    def evaluate(self, click):
        super().evaluate(click)
        for mesa_name in self.MESAS_CONTRATO:
            mesa = click.get_mesa(mesa_name)
            if mesa is None:
                continue
            for inc in mesa.get_incidentes():
                if inc.id_chamado.startswith("T"):
                    continue
                assert inc.status == 'ABERTO'
                categoria = self.categorizar(inc)
                prazo_m = self.calcular_prazo(inc)
                duration_m = click.calc_duration_mesas(inc.id_chamado, self.MESAS_CONTRATO)
                if duration_m < prazo_m:
                    continue
                ids = math.ceil(duration_m / (180.0 * 60))
                self.numerator   += ids
                self.denominator += 1
                self.update_details(inc)
                if inc.id_chamado in click.children_of:
                    for child_id in click.children_of[ inc.id_chamado ]:
                        child = click.get_incidente(child_id)
                        self.update_details(child)

    def get_result(self):
        msg = self.get_description()
        if self.denominator == 0:
            return None, msg
        else:
            result = 100.0 * (self.numerator / self.denominator)
            return result, msg