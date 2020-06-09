import pandas as pd
import pyclick.util as util
import pyclick.ranges as ranges

STATUS_MAPPING = {
    'Atribuição interna'                                    : 'ABERTO',
    'Atribuir ao Fornecedor'                                : 'ABERTO',
    'Resolver'                                              : 'RESOLVIDO',
    'Encerrar'                                              : 'ENCERRADO',
    'Aguardando Cliente - Fornecedor'                       : 'ABERTO',
    'Pendência Sanada - Fornecedor/TIC'                     : 'ABERTO',
    'Aguardando Cliente'                                    : 'ABERTO',
    'Campo do formulário alterado'                          : 'ABERTO',
    'Iniciar Atendimento'                                   : 'ABERTO',
    'Item alterado'                                         : 'ABERTO',
    'Pendência Sanada'                                      : 'ABERTO',
    'Cancelar'                                              : 'CANCELADO',
    'Campos alterados'                                      : 'ABERTO',
    'Aguardando Cliente - Aprovação'                        : 'ABERTO',
    'Pendência Sanada - Aprovação'                          : 'ABERTO',
    'Cancelado'                                             : 'CANCELADO',
    'Retorno do usuário'                                    : 'ABERTO',
    'Pendência de TIC'                                      : 'ABERTO',
    'Atendimento Agendado'                                  : 'ABERTO',
    'Reabrir'                                               : 'ABERTO',
    'Reaberto pelo Fornecedor'                              : 'ABERTO',
    'Pendencia de Fornecedor'                               : 'ABERTO',
    'Categoria alterada'                                    : 'ABERTO',
    'Pendência Feriado Local'                               : 'ABERTO',
    'Pendência Sanada Feriado Local'                        : 'ABERTO',
    'Resposta do Fornecedor'                                : 'ABERTO',
    'Resolver Fornecedor - Executar antes do "Resolver"!'   : 'RESOLVIDO',
    'Iniciar Relógio'                                       : 'ABERTO',
    'Parar Relógio'                                         : 'ABERTO',
    'Atendimento Programado'                                : 'ABERTO'
}

class Event(object):
    
    __slots__ = [    
        'id_chamado' 
    ,   'chamado_pai'
    ,   'categoria'
    ,   'oferta_catalogo'
    ,   'prazo_oferta_m'
    ,   'id_acao'
    ,   'acao_nome'
    ,   'pendencia'
    ,   'mesa_atual'
    ,   'data_acao'
    ,   'data_fim_acao'
    ,   'duracao_m'
    ]
    
    def __init__(self, id_chamado, chamado_pai, categoria, oferta_catalogo, prazo_oferta_m, id_acao, 
                acao_nome, pendencia, mesa_atual, data_acao, data_fim_acao, duracao_m):
        self.id_chamado      = id_chamado
        self.chamado_pai     = chamado_pai
        self.categoria       = categoria
        self.oferta_catalogo = oferta_catalogo
        self.prazo_oferta_m  = prazo_oferta_m
        self.id_acao         = id_acao
        self.acao_nome       = acao_nome
        self.pendencia       = pendencia
        self.mesa_atual      = mesa_atual
        self.data_acao       = data_acao
        self.data_fim_acao   = data_fim_acao
        self.duracao_m       = duracao_m
        
    def __str__(self):
        return util.build_str(self, self.__slots__)
    
    def __repr__(self):
        return util.build_str(self, self.__slots__)
        
    def __eq__(self, other):
        return util.shallow_equality_test(self, other, self.__slots__)
    
    @classmethod
    def parse_events(klass, txt):
        result = []
        lines = txt.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            evt = klass.parse_event(line)
            result.append(evt)
        return result
    
    @classmethod
    def parse_event(klass, txt):
        txt = txt.strip()
        fields = txt.split('\t')
        assert len(fields) == 12 # len(self.__slots__)
        id_chamado      = None if not fields[  0 ] else fields[  0 ]
        chamado_pai     = None if not fields[  1 ] else fields[  1 ]
        categoria       = None if not fields[  2 ] else fields[  2 ]
        oferta_catalogo = None if not fields[  3 ] else fields[  3 ]
        prazo_oferta_m  = None if not fields[  4 ] else int(fields[  4 ])
        id_acao         = None if not fields[  5 ] else int(fields[  5 ])
        acao_nome       = None if not fields[  6 ] else fields[  6 ]
        pendencia       = None if not fields[  7 ] else fields[  7 ]
        mesa_atual      = None if not fields[  8 ] else fields[  8 ]
        data_acao       = None if not fields[  9 ] else fields[  9 ]
        data_fim_acao   = None if not fields[ 10 ] else fields[ 10 ]
        duracao_m       = None if not fields[ 11 ] else int(fields[ 11 ])
        return klass(
            id_chamado      = id_chamado
        ,   chamado_pai     = chamado_pai
        ,   categoria       = categoria
        ,   oferta_catalogo = oferta_catalogo
        ,   prazo_oferta_m  = prazo_oferta_m
        ,   id_acao         = id_acao
        ,   acao_nome       = acao_nome
        ,   pendencia       = pendencia
        ,   mesa_atual      = mesa_atual
        ,   data_acao       = data_acao
        ,   data_fim_acao   = data_fim_acao
        ,   duracao_m       = duracao_m
        )
    @classmethod
    def to_df(klass, evts):
        # TODO: add test case
        data = {
            'id_chamado'        : []
        ,   'chamado_pai'       : []
        ,   'categoria'         : []
        ,   'oferta_catalogo'   : []
        ,   'prazo_oferta_m'    : []
        ,   'id_acao'           : []
        ,   'acao_nome'         : []
        ,   'pendencia'         : []
        ,   'mesa_atual'        : []
        ,   'data_acao'         : []
        ,   'data_fim_acao'     : []
        ,   'duracao_m'         : []
        }
        for evt in evts:
            data[ 'id_chamado'      ].append(evt.id_chamado)
            data[ 'chamado_pai'     ].append(evt.chamado_pai)
            data[ 'categoria'       ].append(evt.categoria)
            data[ 'oferta_catalogo' ].append(evt.oferta_catalogo)
            data[ 'prazo_oferta_m'  ].append(evt.prazo_oferta_m)
            data[ 'id_acao'         ].append(evt.id_acao)
            data[ 'acao_nome'       ].append(evt.acao_nome)
            data[ 'pendencia'       ].append(evt.pendencia)
            data[ 'mesa_atual'      ].append(evt.mesa_atual)
            data[ 'data_acao'       ].append(evt.data_acao)
            data[ 'data_fim_acao'   ].append(evt.data_fim_acao)
            data[ 'duracao_m'       ].append(evt.duracao_m)
        return pd.DataFrame(data)
        
class Acao(object):
    
    __slots__ = [
        'id_acao'
    ,   'acao_nome'
    ,   'pendencia'
    ,   'mesa_atual'
    ,   'data_acao'
    ,   'data_fim_acao'
    ,   'duracao_m'
    ]
    
    def __init__(self, id_acao, acao_nome, pendencia, mesa_atual, data_acao, data_fim_acao, duracao_m):
        assert data_fim_acao is None or data_acao <= data_fim_acao # should I keep this check given that there are known cases of temporal inconsistencies?
        assert pendencia in ( 'S', 'N' )
        assert duracao_m >= 0
        self.id_acao        = id_acao
        self.acao_nome      = acao_nome
        self.pendencia      = pendencia
        self.mesa_atual     = mesa_atual
        self.data_acao      = data_acao
        self.data_fim_acao  = data_fim_acao
        self.duracao_m      = duracao_m
        

    def __str__(self):
        return util.build_str(self, self.__slots__, False)
    
    def __repr__(self):
        return util.build_str(self, self.__slots__, False)
        
    def __eq__(self, other):
        return util.shallow_equality_test(self, other, self.__slots__)

    @property
    def status(self):
        return STATUS_MAPPING[ self.acao_nome ]
        
    @classmethod
    def build_from(klass, evt):
        return klass(
            id_acao        = evt.id_acao
        ,   acao_nome      = evt.acao_nome
        ,   pendencia      = evt.pendencia
        ,   mesa_atual     = evt.mesa_atual
        ,   data_acao      = evt.data_acao
        ,   data_fim_acao  = evt.data_fim_acao
        ,   duracao_m      = evt.duracao_m
        )

class Atribuicao(object):
     
    __slots__ = [ 'seq', 'mesa', 'entrada', 'status_entrada', 'saida', 'status_saida', 'duracao_m', 'pendencia_m' ]
     
    def __init__(self, seq, mesa, entrada, status_entrada, saida, status_saida, duracao_m, pendencia_m):
        self.seq            = seq
        self.mesa           = mesa
        self.entrada        = entrada
        self.status_entrada = status_entrada
        self.saida          = saida
        self.status_saida   = status_saida
        self.duracao_m      = duracao_m
        self.pendencia_m    = pendencia_m
        
    def __str__(self):
        return util.build_str(self, self.__slots__, False)
    
    def __repr__(self):
        return util.build_str(self, self.__slots__, False)
        
    def __eq__(self, other):
        return util.shallow_equality_test(self, other, self.__slots__)
    
    def update(self, incidente, acao):
        assert self.mesa == acao.mesa_atual
        self.saida = acao.data_fim_acao
        self.status_saida = acao.status
        if acao.pendencia == 'N':
            self.duracao_m += acao.duracao_m
        elif acao.pendencia == 'S':
            self.pendencia_m += acao.duracao_m
        else:
            assert 1 == 2 # should not happen
    
    def intersects_with(self, start_dt, end_dt):
        r1 = ranges.Range(start_dt, end_dt)
        if self.saida is None:
            r2 = ranges.Range(self.entrada, '9999-12-31 23:59:59')
        else:
            r2 = ranges.Range(self.entrada, self.saida)
        return r1.overlaps_with(r2)
        
    @classmethod
    def build_from(klass, seq, acao):
        return klass(
            seq             = seq
        ,   mesa            = acao.mesa_atual
        ,   entrada         = acao.data_acao
        ,   status_entrada  = acao.status
        ,   saida           = acao.data_fim_acao
        ,   status_saida    = acao.status
        ,   duracao_m       = (0 if acao.pendencia == 'S' else acao.duracao_m)
        ,   pendencia_m     = (0 if acao.pendencia == 'N' else acao.duracao_m)
        )
    
class Incidente(object):
    
    __slots__ = [
        'id_chamado'
    ,   'chamado_pai' 
    ,   'categoria' 
    ,   'oferta' 
    ,   'prazo'
    ,   'acoes'
    ,   'atribuicoes'
    ,   'mesas'
    ]
    
    def __init__(self, id_chamado, chamado_pai, categoria, oferta, prazo):
        self.id_chamado     = id_chamado
        self.chamado_pai    = chamado_pai
        self.categoria      = categoria
        self.oferta         = oferta
        self.prazo          = prazo
        self.acoes          = []
        self.atribuicoes    = []
        self.mesas          = set()
        
    def __str__(self):
        return util.build_str(self, self.__slots__)
    
    def __repr__(self):
        return util.build_str(self, self.__slots__)
    
    def __eq__(self, other):
        return util.shallow_equality_test(self, other, self.__slots__)
    
    def add_acao(self, acao):
        duracao_m = (0 if acao.pendencia == 'S' else acao.duracao_m)
        if len(self.acoes) == 0 or self.mesa_atual != acao.mesa_atual:
            seq = len(self.atribuicoes) + 1
            a = Atribuicao.build_from(seq, acao)
            self.atribuicoes.append(a)
        else:
            self.atribuicoes[ -1 ].update(self, acao)
        self.acoes.append(acao)
        self.mesas.add(acao.mesa_atual)
        
    def calc_duration(self):
        return sum([ a.duracao_m for a in self.acoes if a.pendencia =='N'])
    
    def calc_duration_mesas(self, mesas):
        return sum([
            atrib.duracao_m for atrib in self.get_atribuicoes_mesas(mesas)
        ])
    
    def get_atribuicoes_mesas(self, mesas):
        return list([
            atrib for atrib in self.atribuicoes if atrib.mesa in mesas
        ])
    
    def possui_atribuicoes(self, mesas):
        for mesa in mesas:
            if mesa in self.mesas:
                return True
        return False
    
    @property
    def action_count(self):
        return len(self.acoes)
        
    @property
    def mesa_atual(self):
        assert self.action_count > 0
        return self.acoes[ -1 ].mesa_atual
    
    @property
    def status(self):
        assert self.action_count > 0
        return self.acoes[ -1 ].status
        
    @classmethod
    def build_from(klass, evt):
        return klass(
            id_chamado          = evt.id_chamado          
        ,   chamado_pai         = evt.chamado_pai
        ,   categoria           = evt.categoria
        ,   oferta              = evt.oferta_catalogo 
        ,   prazo               = evt.prazo_oferta_m
        )

class Mesa(object):

    def __init__(self, name):
        self.name = name
        self.incidentes = {} # currently open incidentes
        self.seen_incs = {} # all incs once assigned to the mesa
     
    def add_incidente(self, inc):
        assert inc.id_chamado not in self.incidentes
        self.incidentes[ inc.id_chamado ] = inc
        self.seen_incs[ inc.id_chamado ] = inc
    
    def remove_incidente(self, inc):
        assert inc.id_chamado in self.incidentes
        del self.incidentes[ inc.id_chamado ]
    
    def get_incidente(self, id_chamado, seen=False):
        if seen:
            return self.seen_incs.get(id_chamado, None)
        else:
            return self.incidentes.get(id_chamado, None)
    
    def has_incidente(self, id_chamado):
        return id_chamado in self.incidentes
    
    def seen_incidente(self, id_chamado):
        return id_chamado in self.seen_incs
    
    def get_incidentes(self):
        return self.incidentes.values()

    def get_seen_incidentes(self):
        return self.seen_incs.values()
        
class Click(object):
    
    def __init__(self):
        self.incidentes = {}
        self.mesas = {}
        self.children_of = {}
    
    def update_children_mapping(self, evt):
        if evt.chamado_pai is None:
            return
        if evt.chamado_pai not in self.children_of:
            assert evt.chamado_pai.startswith('S')
            self.children_of[ evt.chamado_pai ] = set()
        if evt.id_chamado not in self.children_of[ evt.chamado_pai ]:
            assert evt.id_chamado.startswith('T')
            self.children_of[ evt.chamado_pai ].add(evt.id_chamado)
    
    def update(self, event):
        if event.mesa_atual not in self.mesas:
            self.mesas[ event.mesa_atual ] = Mesa(event.mesa_atual)
        mesa_atual = self.mesas[ event.mesa_atual ]
        
        if event.id_chamado not in self.incidentes:
            self.incidentes[ event.id_chamado ] = Incidente.build_from(event)
            self.update_children_mapping(event)
        incidente = self.incidentes[ event.id_chamado ]
        
        acao = Acao.build_from(event)
        
        if incidente.action_count == 0:
            incidente.add_acao(acao)
            mesa_atual.add_incidente(incidente)
        else:
            mesa_anterior = self.mesas[ incidente.mesa_atual ] # should I switch to nome_mesa_atual???
            incidente.add_acao(acao)
            if mesa_anterior != mesa_atual:
                mesa_anterior.remove_incidente(incidente)
                mesa_atual.add_incidente(incidente)
        
        if incidente.status != 'ABERTO' and event.data_fim_acao is None:
            mesa_atual.remove_incidente(incidente)
            
    def incident_count(self):
        return len(self.incidentes)
        
    def get_incidente(self, id_chamado):
        return self.incidentes.get(id_chamado, None)

    def get_mesa(self, mesa):
        return self.mesas.get(mesa, None)
    
    def calc_duration_mesas(self, id_chamado, mesas):
        if id_chamado.startswith("S"):
            return self.calc_children_duration_mesas(id_chamado, mesas)
        else:
            incidente = self.get_incidente(id_chamado)
            if incidente is None:
                return 0
            return incidente.calc_duration_mesas(mesas)
            
    def calc_children_duration_mesas(self, id_chamado, mesas):
        if id_chamado not in self.children_of:
            return 0
        result_m = 0
        for child_id in self.children_of[ id_chamado ]:
            child = self.incidentes.get(child_id)
            if not child:
                continue
            result_m += child.calc_duration_mesas(mesas)
        return result_m
    
    def get_incidentes(self):
        return self.incidentes.values()
        
class Kpi(object):
    
    def __init__(self):
        self.expurgos = set()
    
    def purge(self, id_chamado):
        self.expurgos.add(id_chamado)
    
    def is_purged(self, id_chamado):
        return id_chamado in self.expurgos
        
    def evaluate(self, click):
        raise NotImplementedError
    
    def get_result(self):
        raise NotImplementedError
    
