import pyclick.util as util
import unittest

        
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
    
class Incidente(object):
    
    __slots__ = [
        'id_chamado' 
    ,   'chamado_pai' 
    ,   'categoria' 
    ,   'oferta' 
    ,   'prazo'
    ,   'acoes'
    ]
    
    def __init__(self, id_chamado, chamado_pai, categoria, oferta, prazo):
        self.id_chamado     = id_chamado
        self.chamado_pai    = chamado_pai
        self.categoria      = categoria
        self.oferta         = oferta
        self.prazo          = prazo
        self.acoes          = []
    
    def __str__(self):
        return util.build_str(self, self.__slots__)
    
    def __repr__(self):
        return util.build_str(self, self.__slots__)
        
    def __eq__(self, other):
        return util.shallow_equality_test(self, other, self.__slots__)
        
    @classmethod
    def build_from(klass, evt):
        return klass(
            id_chamado          = evt.id_chamado          
        ,   chamado_pai         = evt.chamado_pai
        ,   categoria           = evt.categoria
        ,   oferta              = evt.oferta_catalogo 
        ,   prazo               = evt.prazo_oferta_m
        )


class TestEvento(unittest.TestCase):

    def setUp(self):
        self.evt1 = Event(
            id_chamado      = "123" 
        ,   chamado_pai     = None
        ,   categoria       = "CAT1"
        ,   oferta_catalogo = "OF1"
        ,   prazo_oferta_m  = 8 * 60
        ,   id_acao         = 111
        ,   acao_nome       = "Ação 1"
        ,   pendencia       = "N"
        ,   mesa_atual      = "N4-FOO-BAR"
        ,   data_acao       = "2020-01-01 09:15:00"
        ,   data_fim_acao   = "2020-01-01 09:30:00"
        ,   duracao_m       = 15*60
        )
        self.evt2 = Event(
            id_chamado      = "123" 
        ,   chamado_pai     = None
        ,   categoria       = "CAT1"
        ,   oferta_catalogo = "OF1"
        ,   prazo_oferta_m  = 8 * 60
        ,   id_acao         = 112
        ,   acao_nome       = "Ação 2"
        ,   pendencia       = "N"
        ,   mesa_atual      = "N4-FOO-BAR"
        ,   data_acao       = "2020-01-01 09:30:00"
        ,   data_fim_acao   = "2020-01-01 09:45:00"
        ,   duracao_m       = 15*60
        )        
        self.evt3 = Event(
            id_chamado      = "123" 
        ,   chamado_pai     = None
        ,   categoria       = "CAT1"
        ,   oferta_catalogo = "OF1"
        ,   prazo_oferta_m  = 8 * 60
        ,   id_acao         = 111
        ,   acao_nome       = "Ação 1"
        ,   pendencia       = "N"
        ,   mesa_atual      = "N4-FOO-BAR"
        ,   data_acao       = "2020-01-01 09:15:00"
        ,   data_fim_acao   = "2020-01-01 09:30:00"
        ,   duracao_m       = 15*60
        )

    def tearDown(self):
        pass
    
    def test_it_implements_equality(self):
        self.assertEqual(self.evt1, self.evt1)
        self.assertNotEqual(self.evt1, self.evt2)
        self.assertEqual(self.evt1, self.evt3)
    

class TestAcao(unittest.TestCase):

    def setUp(self):
        self.evt1 = Event(
            id_chamado      = "123" 
        ,   chamado_pai     = None
        ,   categoria       = "CAT1"
        ,   oferta_catalogo = "OF1"
        ,   prazo_oferta_m  = 8 * 60
        ,   id_acao         = 111
        ,   acao_nome       = "Ação 1"
        ,   pendencia       = "N"
        ,   mesa_atual      = "N4-FOO-BAR"
        ,   data_acao       = "2020-01-01 09:15:00"
        ,   data_fim_acao   = "2020-01-01 09:30:00"
        ,   duracao_m       = 15*60
        )
        self.act1 = Acao(
            id_acao        = self.evt1.id_acao
        ,   acao_nome      = self.evt1.acao_nome
        ,   pendencia      = self.evt1.pendencia
        ,   mesa_atual     = self.evt1.mesa_atual
        ,   data_acao      = self.evt1.data_acao
        ,   data_fim_acao  = self.evt1.data_fim_acao
        ,   duracao_m      = self.evt1.duracao_m
        )
        
        self.evt2 = Event(
            id_chamado      = "123" 
        ,   chamado_pai     = None
        ,   categoria       = "CAT1"
        ,   oferta_catalogo = "OF1"
        ,   prazo_oferta_m  = 8 * 60
        ,   id_acao         = 112
        ,   acao_nome       = "Ação 2"
        ,   pendencia       = "S"
        ,   mesa_atual      = "N4-FOO-BAR"
        ,   data_acao       = "2020-01-01 09:30:00"
        ,   data_fim_acao   = "2020-01-01 09:45:00"
        ,   duracao_m       = 0
        )                
        self.act2 = Acao(
            id_acao        = self.evt2.id_acao
        ,   acao_nome      = self.evt2.acao_nome
        ,   pendencia      = self.evt2.pendencia
        ,   mesa_atual     = self.evt2.mesa_atual
        ,   data_acao      = self.evt2.data_acao
        ,   data_fim_acao  = self.evt2.data_fim_acao
        ,   duracao_m      = self.evt2.duracao_m
        )
        
        self.act3 = Acao(
            id_acao        = self.evt1.id_acao
        ,   acao_nome      = self.evt1.acao_nome
        ,   pendencia      = self.evt1.pendencia
        ,   mesa_atual     = self.evt1.mesa_atual
        ,   data_acao      = self.evt1.data_acao
        ,   data_fim_acao  = self.evt1.data_fim_acao
        ,   duracao_m      = self.evt1.duracao_m
        )
        
    def tearDown(self):
        pass
        
    def test_it_implements_equality(self):
        self.assertEqual(self.act1, self.act1)
        self.assertNotEqual(self.act1, self.act2)
        self.assertEqual(self.act1, self.act3)
    
    def test_it_buils_an_action_from_an_event(self):
        act = Acao.build_from(self.evt1)
        self.assertEqual(self.act1, act)
        act = Acao.build_from(self.evt2)
        self.assertEqual(self.act2, act)

class TestIncident(unittest.TestCase):

    def setUp(self):
        self.evt1 = Event(
            id_chamado      = "123" 
        ,   chamado_pai     = None
        ,   categoria       = "CAT1"
        ,   oferta_catalogo = "OF1"
        ,   prazo_oferta_m  = 8 * 60
        ,   id_acao         = 111
        ,   acao_nome       = "Ação 1"
        ,   pendencia       = "N"
        ,   mesa_atual      = "N4-FOO-BAR"
        ,   data_acao       = "2020-01-01 09:15:00"
        ,   data_fim_acao   = "2020-01-01 09:30:00"
        ,   duracao_m       = 15*60
        )
        self.inc1 = Incidente(
            id_chamado      = self.evt1.id_chamado
        ,   chamado_pai     = self.evt1.chamado_pai
        ,   categoria       = self.evt1.categoria
        ,   oferta          = self.evt1.oferta_catalogo
        ,   prazo           = self.evt1.prazo_oferta_m
        )        
        self.evt2 = Event(
            id_chamado      = "124" 
        ,   chamado_pai     = None
        ,   categoria       = "CAT1"
        ,   oferta_catalogo = "OF1"
        ,   prazo_oferta_m  = 8 * 60
        ,   id_acao         = 112
        ,   acao_nome       = "Ação 2"
        ,   pendencia       = "S"
        ,   mesa_atual      = "N4-FOO-BAR"
        ,   data_acao       = "2020-01-01 09:30:00"
        ,   data_fim_acao   = "2020-01-01 09:45:00"
        ,   duracao_m       = 0
        )                
        self.inc2 = Incidente(
            id_chamado      = self.evt2.id_chamado
        ,   chamado_pai     = self.evt2.chamado_pai
        ,   categoria       = self.evt2.categoria
        ,   oferta          = self.evt2.oferta_catalogo
        ,   prazo           = self.evt2.prazo_oferta_m
        )
        
        self.inc3 = Incidente(
            id_chamado      = self.evt1.id_chamado
        ,   chamado_pai     = self.evt1.chamado_pai
        ,   categoria       = self.evt1.categoria
        ,   oferta          = self.evt1.oferta_catalogo
        ,   prazo           = self.evt1.prazo_oferta_m
        )
        
    def tearDown(self):
        pass
        
    def test_it_implements_equality(self):
        self.assertEqual(self.inc1, self.inc1)
        self.assertNotEqual(self.inc1, self.inc2)
        self.assertEqual(self.inc1, self.inc3)
    
    def test_it_buils_an_action_from_an_event(self):
        inc = Incidente.build_from(self.evt1)
        self.assertEqual(self.inc1, inc)
        inc = Incidente.build_from(self.evt2)
        self.assertEqual(self.inc2, inc)