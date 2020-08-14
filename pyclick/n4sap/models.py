import os
import pandas as pd
import pyclick.config as config
import pyclick.util as util
import pyclick.models as models

class ClickN4(models.Click):
    
    def __init__(self, incsrv, strict_orientar=False):
        super().__init__()
        self.incsrv = incsrv
        self.strict_orientar = strict_orientar
        self.expurgos_orientar = set()
    
    def categorizar(self, inc):
        return self.incsrv.categorizar(inc)
            
    def update(self, event):
        if self.incsrv.categorizar(event) is None:
            self.expurgos_orientar.add(event.id_chamado)
            return
        super().update(event)
            
class N4SapKpi(models.Kpi):
    
    KPI_NAME                = None
    SLA                     = None
    MESA_PRIORIDADE         = 'N4-SAP-SUSTENTACAO-PRIORIDADE'
    MESA_ESCALADOS          = 'N4-SAP-SUSTENTACAO-ESCALADOS'
    MESAS_NAO_PRIORITARIAS  = [ # TODO: Remover MESAS_NAO_PRIORITARIAS ... contém a mesa de escalados
        'N4-SAP-SUSTENTACAO-ABAST_GE'
    ,   'N4-SAP-SUSTENTACAO-APOIO_OPERACAO'
    ,   'N4-SAP-SUSTENTACAO-CORPORATIVO'
    ,   'N4-SAP-SUSTENTACAO-ESCALADOS'
    ,   'N4-SAP-SUSTENTACAO-FINANCAS' 
    ,   'N4-SAP-SUSTENTACAO-GRC'
    ,   'N4-SAP-SUSTENTACAO-PORTAL'
    ,   'N4-SAP-SUSTENTACAO-SERVICOS'
    ]
    MESAS_NAO_PRIORITARIAS_V2  = [
        'N4-SAP-SUSTENTACAO-ABAST_GE'
    ,   'N4-SAP-SUSTENTACAO-APOIO_OPERACAO'
    ,   'N4-SAP-SUSTENTACAO-CORPORATIVO'
    #,   'N4-SAP-SUSTENTACAO-ESCALADOS'
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
    
    def __init__(self, incsrv=None, logger=None):
        if incsrv is None:
            incsrv = IncidentService()
        if logger is None:
            logger = util.get_null_logger()
        super().__init__()
        self.incsrv = incsrv
        self.logger = logger
    
    def add_expurgo(self, id_chamado):
        self.incsrv.add_expurgo(id_chamado)
    
    def is_purged(self, id_chamado):
        return self.incsrv.is_purged(id_chamado)

    def add_oferta_catalogo(self, oferta, prazo_oferta_m):
        self.incsrv.add_oferta_catalogo(oferta, prazo_oferta_m)
        
    def set_override_categoria(self, id_chamado, categoria):
        self.incsrv.set_override_categoria(id_chamado, categoria)
    
    def unset_override_categoria(self, id_chamado):
        self.incsrv.unset_override_categoria(id_chamado)
        
    def set_override_categorias(self, categorias):
        for id_chamado, categoria in categorias.items():
            self.set_override_categoria(id_chamado, categoria)
            
    def set_override_categoria(self, id_chamado, categoria):
        self.incsrv.set_override_categoria(id_chamado, categoria)
    
    def unset_override_categoria(self, id_chamado):
        self.incsrv.unset_override_categoria[ id_chamado ]
    
    def categorizar(self, inc):
        return self.incsrv.categorizar(inc)
        
    def calcular_prazo(self, inc, mesa_atual=None, enable_peso30=False):
        # TODO: assert mesa_atual is not None
        # assert mesa_atual is not None
        if mesa_atual is None:
            mesa_atual = inc.mesa_atual
        return self.incsrv.calcular_prazo(inc, mesa_atual, enable_peso30=enable_peso30)
    
    def calc_duration_mesas(self, inc, mesas):
        return self.incsrv.calc_duration_mesas(inc, mesas)
    
    def calc_pendencia_mesas(self, inc, mesas):
        return self.incsrv.calc_pendencia_mesas(inc, mesas)
        
    def build_mesa_mapping(self, mesa):
        return {
            'N4-SAP-SUSTENTACAO-ABAST_GE'       : mesa
        ,   'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' : mesa
        ,   'N4-SAP-SUSTENTACAO-CORPORATIVO'    : mesa
        ,   'N4-SAP-SUSTENTACAO-FINANCAS'       : mesa
        ,   'N4-SAP-SUSTENTACAO-GRC'            : mesa
        ,   'N4-SAP-SUSTENTACAO-PORTAL'         : mesa
        ,   'N4-SAP-SUSTENTACAO-SERVICOS'       : mesa
        }
    def evaluate(self, click):
        raise NotImplementedError
    
    def get_details(self):
        raise NotImplementedError

    def get_result(self):
        raise NotImplementedError
        
    def update_summary(self, summary, mesa=''):
        kpi, obs = self.get_result()
        summary[ 'INDICADOR'    ].append(self.KPI_NAME)
        summary[ 'MESA'         ].append(mesa)
        summary[ 'VALOR'        ].append(kpi)
        summary[ 'SLA'          ].append(self.SLA)
        summary[ 'OBS'          ].append(obs)

class IncidentService(object): 
    
    SLA_PESO35              =   9 * 60
    SLA_PESO30_ORIENTAR     =   9 * 60
    SLA_PESO30_CORRIGIR     =  72 * 60
    SLA_PESO30_ATENDER      =  36 * 60
    SLA_ORIENTAR            =  40 * 60
    SLA_CORRIGIR            = 135 * 60
    SLA_ORIENTAR            =  27 * 60
    SLA_ATENDER_SIMPLES     =  45 * 60
    SLA_ATENDER_MEDIO       =  90 * 60
    SLA_ATENDER_COMPLEXO    = 180 * 60
    SLAS_ATENDER            = set([45 * 60, 90 * 60, 180 * 60])
    SLA_ATENDER_DEFAULT     = 45 * 60
    MESA_PRIORIDADE         = 'N4-SAP-SUSTENTACAO-PRIORIDADE'
    MESA_ESCALADOS          = 'N4-SAP-SUSTENTACAO-ESCALADOS'
    MESAS_NAO_PRIORITARIAS  = [
        'N4-SAP-SUSTENTACAO-ABAST_GE'
    ,   'N4-SAP-SUSTENTACAO-APOIO_OPERACAO'
    ,   'N4-SAP-SUSTENTACAO-CORPORATIVO'
    ,   'N4-SAP-SUSTENTACAO-FINANCAS' 
    ,   'N4-SAP-SUSTENTACAO-GRC'
    ,   'N4-SAP-SUSTENTACAO-PORTAL'
    ,   'N4-SAP-SUSTENTACAO-SERVICOS'
    ]
    MESAS_CONTRATO          = [
        'N4-SAP-SUSTENTACAO-ABAST_GE'
    ,   'N4-SAP-SUSTENTACAO-APOIO_OPERACAO'
    ,   'N4-SAP-SUSTENTACAO-CORPORATIVO'
    ,   'N4-SAP-SUSTENTACAO-FINANCAS' 
    ,   'N4-SAP-SUSTENTACAO-GRC'
    ,   'N4-SAP-SUSTENTACAO-PORTAL'
    ,   'N4-SAP-SUSTENTACAO-SERVICOS'
    ,   'N4-SAP-SUSTENTACAO-PRIORIDADE'    
    ,   'N4-SAP-SUSTENTACAO-ESCALADOS'    
    ]
    
    def __init__(self, strict_orientar=False):
        self.ofertas_catalogo = {}
        self.override_categorias = {}
        self.override_ofertas = {}
        self.expurgos = set()
        self.strict_orientar = strict_orientar
    
    def add_expurgo(self, id_chamado):
        self.expurgos.add(id_chamado)
    
    def is_purged(self, id_chamado):
        return id_chamado in self.expurgos
        
    def add_oferta_catalogo(self, oferta, prazo_oferta_m):
        self.ofertas_catalogo[ oferta ] = prazo_oferta_m
        
    def set_override_categoria(self, id_chamado, categoria):
        self.override_categorias[ id_chamado ] = categoria
    
    def unset_override_categoria(self, id_chamado):
        del self.override_categorias[ id_chamado ]

    def set_override_oferta(self, id_chamado, oferta):
        self.override_ofertas[ id_chamado ] = oferta
    
    def unset_override_oferta(self, id_chamado):
        del self.override_ofertas[ id_chamado ]        
        
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
            if not self.strict_orientar:
                return 'ORIENTAR'
            elif self.strict_orientar and 'ORIENTAR' in inc.categoria.upper():
                return 'ORIENTAR'
            else:
                return None
                
    def calcular_prazo(self, inc, mesa_atual, enable_peso30=False):
        assert mesa_atual is not None
        assert mesa_atual in self.MESAS_CONTRATO
        categoria = self.categorizar(inc)
        assert categoria is not None
        
        if mesa_atual == self.MESA_PRIORIDADE:
            return self.SLA_PESO35
        
        elif mesa_atual == self.MESA_ESCALADOS and enable_peso30:
            if categoria in ('ATENDER', 'ATENDER - TAREFA'):
                return self.SLA_PESO30_ATENDER
            elif categoria == 'CORRIGIR':
                return self.SLA_PESO30_CORRIGIR
            elif categoria == 'ORIENTAR':
                return self.SLA_PESO30_ORIENTAR
            assert 1 == 2 # should not happen
            
        elif categoria in ('ATENDER', 'ATENDER - TAREFA'):
            oferta = self.override_ofertas.get(inc.id_chamado, inc.oferta)
            prazo = self.ofertas_catalogo.get(oferta, inc.prazo)
            return prazo if prazo in self.SLAS_ATENDER else self.SLA_ATENDER_DEFAULT
            
        elif categoria == 'CORRIGIR':
            return 135 * 60
            
        elif categoria == 'ORIENTAR':
            return 27 * 60
            
        assert 1 == 2 # should not happen
    
    def calc_duration_mesas(self, inc, mesas):
        assert mesas is not None and len(mesas) > 0
        return inc.calc_duration_mesas(mesas)
    
    def calc_pendencia_mesas(self, inc, mesas):
        assert mesas is not None and len(mesas) > 0
        return inc.calc_pendencia_mesas(mesas)
    
    def get_expurgos(self):
        return pd.DataFrame({ 
            'id_chamado' : list(sorted(self.expurgos))
        })
    
    def get_overrides_categoria(self):
        return pd.DataFrame({ 
            'id_chamado' : list(self.override_categorias.keys()),
            'categoria'  : list(self.override_categorias.values())
        })
    
    def get_overrides_oferta(self):
        return pd.DataFrame({ 
            'id_chamado' : list(self.override_ofertas.keys()),
            'oferta'     : list(self.override_ofertas.values())
        })        