import pyclick.models as models

class N4SapKpi(models.Kpi):
    
    MESA_PRIORIDADE = 'N4-SAP-SUSTENTACAO-PRIORIDADE'
    
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
