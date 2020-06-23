import pyclick.util as util
import pyclick.models as models

class N4SapKpi(models.Kpi):
    
    KPI_NAME                = None
    SLA                     = None
    MESA_PRIORIDADE         = 'N4-SAP-SUSTENTACAO-PRIORIDADE'
    MESA_ESCALADOS          = 'N4-SAP-SUSTENTACAO-ESCALADOS'
    MESAS_NAO_PRIORITARIAS  = [
        'N4-SAP-SUSTENTACAO-ABAST_GE'
    ,   'N4-SAP-SUSTENTACAO-APOIO_OPERACAO'
    ,   'N4-SAP-SUSTENTACAO-CORPORATIVO'
    ,   'N4-SAP-SUSTENTACAO-ESCALADOS'
    ,   'N4-SAP-SUSTENTACAO-FINANCAS' 
    ,   'N4-SAP-SUSTENTACAO-GRC'
    ,   'N4-SAP-SUSTENTACAO-PORTAL'
    ,   'N4-SAP-SUSTENTACAO-SERVICOS'
    ]
    MESAS_CONTRATO          = [ MESA_PRIORIDADE ] + MESAS_NAO_PRIORITARIAS
    BREACHED_MAPPING        = {
        True    : 'S'
    ,   False   : 'N'
    ,   None    : None
    }  
    def __init__(self, logger=None):
        if logger is None:
            logger = util.get_null_logger()
        super().__init__()
        self.override_categorias = {}
        self.logger = logger
        
    def set_override_categoria(self, id_chamado, categoria):
        self.override_categorias[ id_chamado ] = categoria
    
    def unset_override_categoria(self, id_chamado):
        del self.override_categorias[ id_chamado ]
    
    def categorizar(self, inc):
        if inc.id_chamado in self.override_categorias:
            return self.override_categorias[ inc.id_chamado ]
        elif inc.id_chamado.startswith('T'):
            return 'ATENDER - TAREFA'
        elif inc.id_chamado.startswith('S'):
            return 'ATENDER'
        elif 'CORRIGIR' in inc.categoria.upper():
            return 'CORRIGIR'
        else:
            return 'ORIENTAR'
    
    def calcular_prazo(self, inc, mesa_atual=None):
        if mesa_atual is None:
            mesa = inc.mesa_atual
        categoria = self.categorizar(inc)
        if mesa == self.MESA_PRIORIDADE:
            return 9 * 60
        elif categoria in ('ATENDER', 'ATENDER - TAREFA'):
            return inc.prazo
        elif categoria == 'CORRIGIR':
            return 135 * 60
        elif categoria == 'ORIENTAR':
            return 27 * 60
        else:
            assert 1 == 2 # should not happen
            
    def evaluate(self, click):
        pass
    
    def get_details(self):
        raise NotImplementedError

    def get_result(self):
        raise NotImplementedError
        
    def update_summary(self, summary):
        kpi, obs = self.get_result()
        summary[ 'INDICADOR'    ].append(self.KPI_NAME)
        summary[ 'VALOR'        ].append(kpi)
        summary[ 'SLA'          ].append(self.SLA)
        summary[ 'OBS'          ].append(obs)
        
