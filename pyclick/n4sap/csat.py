import pandas as pd
import pyclick.n4sap.models as models        

class Csat(models.N4SapKpi):
    
    KPI_NAME    = "CSAT"
    SLA         = 90.0
    NOTA_CORTE  = 4
    
    def __init__(self):
        super().__init__()
        self.reset()
        
    def reset(self):
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
        self.details_tecnicos = {
            'tecnico'           : [],
            'avaliacoes'        : [],
            'score'             : [],
            'aval_positivas'    : [],
            'aval_negativas'    : [],
        }
        self.details_tecnicos_idx = {}
            
    def update_details(self, pesq, breached, start_dt, end_dt):
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
        
        if pesq.tecnico not in self.details_tecnicos_idx:
            idx = len(self.details_tecnicos[ 'tecnico' ])
            self.details_tecnicos_idx[ pesq.tecnico ] = idx
            self.details_tecnicos[ 'tecnico'          ].append(pesq.tecnico),
            self.details_tecnicos[ 'avaliacoes'       ].append(0)
            self.details_tecnicos[ 'score'            ].append(0)
            self.details_tecnicos[ 'aval_positivas'   ].append(0)
            self.details_tecnicos[ 'aval_negativas'   ].append(0)
        idx = self.details_tecnicos_idx[ pesq.tecnico ]
        score_factor = -0.1 if not breached else +0.9
        self.details_tecnicos[ 'avaliacoes'       ][ idx ] += 1
        self.details_tecnicos[ 'score'            ][ idx ] += score_factor
        self.details_tecnicos[ 'aval_positivas'   ][ idx ] += 1 if not breached else 0
        self.details_tecnicos[ 'aval_negativas'   ][ idx ] += 1 if breached else 0
                                                          
    def get_details(self):
        return pd.DataFrame(self.details), pd.DataFrame(self.details_tecnicos)
    
    def get_description(self):
        if self.denominator == 0:
            msg = "Nenhuma pesquisa respondida"
        else:
            msg = f"1.0 - ({self.numerator} violações / {self.denominator} pesquisas)"
        return msg
        
    def evaluate(self, click, start_dt, end_dt, mesa_filter=None):
        for pesq in click.get_pesquisas_mesas( self.MESAS_CONTRATO ):
            if mesa_filter is not None and pesq.mesa != mesa_filter:
                continue
            breached = pesq.avaliacao < self.NOTA_CORTE
            self.numerator   += (1 if breached else 0)
            self.denominator += 1
            self.update_details(pesq, breached, start_dt, end_dt)

    def get_result(self):
        msg = self.get_description()
        if self.denominator == 0:
            return None, msg
        else:
            result = 100.0 * (1.0 - (self.numerator / self.denominator))
            return result, msg

class CsatPeriodo(Csat):
    
    KPI_NAME    = "CSAT - Período"
    SLA         = 90.0
    NOTA_CORTE  = 4
    
    def __init__(self):    
        super().__init__()
            
    def evaluate(self, click, start_dt, end_dt, mesa_filter=None):
        for pesq in click.get_pesquisas_mesas( self.MESAS_CONTRATO ):
            if mesa_filter is not None and pesq.mesa != mesa_filter:
                continue            
            if not (start_dt <= pesq.data_resposta <= end_dt):
                continue
            breached = pesq.avaliacao < self.NOTA_CORTE
            self.numerator   += (1 if breached else 0)
            self.denominator += 1
            self.update_details(pesq, breached, start_dt, end_dt)
        