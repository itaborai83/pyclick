import pyclick.models as models

class N4SapKpi(models.Kpi):
    
    MESA_PRIORIDADE = 'N4-SAP-SUSTENTACAO-PRIORIDADE'
    MESAS_NAO_PRIORITARIAS = [
        'N4-SAP-SUSTENTACAO-ABAST_GE'
    ,   'N4-SAP-SUSTENTACAO-APOIO_OPERACAO'
    ,   'N4-SAP-SUSTENTACAO-CORPORATIVO'
    ,   'N4-SAP-SUSTENTACAO-ESCALADOS'
    ,   'N4-SAP-SUSTENTACAO-FINANCAS' 
    ,   'N4-SAP-SUSTENTACAO-GRC'
    ,   'N4-SAP-SUSTENTACAO-PORTAL'
    ,   'N4-SAP-SUSTENTACAO-SERVICOS'
    ]
    
    def __init__(self):
        super().__init__()
        self.override_categorias = {}
        
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
    
    def evaluate(self, click):
        pass
