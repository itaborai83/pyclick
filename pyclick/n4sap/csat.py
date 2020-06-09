import pandas as pd
import pyclick.n4sap.models as models        

class Csat(models.N4SapKpi):
    
    KPI_NAME    = "CSAT"
    SLA         = 90.0
    NOTA_CORTE  = 4
    
    def __init__(self):
        super().__init__()
        self.numerator = 0
        self.denominator = 0
        self.details = {
            'violacao'          : [],
            'id_pesquisa'       : [],
            'id_chamado'        : [],
            'mesa'              : [],
            'tecnico'           : [],
            'usuario'           : [],
            'data_resposta'     : [],
            'avaliacao'         : [],
            'motivo'            : [],
            'comentario'        : [],
        }
            
    def update_details(self, pesq, breached):
        self.details[ 'violacao'        ].append(self.BREACHED_MAPPING[ breached ])
        self.details[ 'id_pesquisa'     ].append(pesq.id_pesquisa)
        self.details[ 'id_chamado'      ].append(pesq.id_chamado)
        self.details[ 'mesa'            ].append(pesq.mesa)
        self.details[ 'tecnico'         ].append(pesq.tecnico)
        self.details[ 'usuario'         ].append(pesq.usuario)
        self.details[ 'data_resposta'   ].append(pesq.data_resposta)
        self.details[ 'avaliacao'       ].append(pesq.avaliacao)
        self.details[ 'motivo'          ].append(pesq.motivo)
        self.details[ 'comentario'      ].append(pesq.comentario)
            
    def get_details(self):
        return pd.DataFrame(self.details)
    
    def get_description(self):
        if self.denominator == 0:
            msg = "Nenhuma pesquisa respondida"
        else:
            msg = f"1.0 - ({self.numerator} violações / {self.denominator} pesquisas)"
        return msg
        
    def evaluate(self, click, start_dt, end_dt):
        super().evaluate(click)
        for pesq in click.get_pesquisas_mesas( self.MESAS_CONTRATO ):
            if not (start_dt <= pesq.data_resposta <= end_dt):
                continue
            breached = pesq.avaliacao < self.NOTA_CORTE
            self.numerator   += (1 if breached else 0)
            self.denominator += 1
            self.update_details(pesq, breached)

    def get_result(self):
        msg = self.get_description()
        if self.denominator == 0:
            return None, msg
        else:
            result = 100.0 * (1.0 - (self.numerator / self.denominator))
            return result, msg