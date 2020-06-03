import pandas as pd
import pyclick.n4sap.models as models        

class Prc(models.N4SapKpi):
    
    PRAZO_M = 135 * 60
    SLA     = 25.0
    
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
        for atrib in inc.atribuicoes:
            if atrib.mesa not in self.MESAS_NAO_PRIORITARIAS:
                continue
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
            msg = "Nenhum incidente corrigir processado"
        else:
            msg = f"{self.numerator} violações / {self.denominator} incidentes"
        return msg
        
    def evaluate(self, click):
        super().evaluate(click)
        for inc in click.get_incidentes():
            if inc.id_chamado.startswith("T") or inc.id_chamado.startswith("S"):
                continue
            if not inc.possui_atribuicoes(self.MESAS_NAO_PRIORITARIAS):
                continue
            categoria = self.categorizar(inc)
            if categoria != "CORRIGIR":
                continue
            duration_m = click.calc_duration_mesas(inc.id_chamado, self.MESAS_NAO_PRIORITARIAS)
            self.numerator   += (1 if duration_m > self.PRAZO_M else 0)
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
            