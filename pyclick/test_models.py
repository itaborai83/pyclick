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
        assert data_fim_acao is None or data_acao <= data_fim_acao
        assert pendencia in [ 'S', 'N' ]
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
    
    def add_acao(self, acao):
        self.acoes.append(acao)
    
    def action_count(self):
        return len(self.acoes)
    
    def calc_duration(self):
        return sum([ a.duracao_m for a in self.acoes if a.pendencia =='N'])
    
    def calc_duration_mesas(self, mesas):
        return sum([ a.duracao_m for a in self.acoes if a.pendencia == 'N' and a.mesa_atual in mesas ])
        
    @classmethod
    def build_from(klass, evt):
        return klass(
            id_chamado          = evt.id_chamado          
        ,   chamado_pai         = evt.chamado_pai
        ,   categoria           = evt.categoria
        ,   oferta              = evt.oferta_catalogo 
        ,   prazo               = evt.prazo_oferta_m
        )

class Click(object):
    
    def __init__(self):
        self.incidentes = {}
        self.seen_actions = set()
    
    def update(self, event):
        if event.id_chamado not in self.incidentes:
            self.incidentes[ event.id_chamado ] = Incidente.build_from(event)
        incidente = self.incidentes[ event.id_chamado ]
        acao = Acao.build_from(event)
        incidente.add_acao(acao)
    
    def incident_count(self):
        return len(self.incidentes)
        
    def get_incidente(self, id_chamado):
        return self.incidentes.get(id_chamado, None)
        
class TestEvento(unittest.TestCase):

    def setUp(self):
        self.evt1 = Event(
            id_chamado      = "123" ,       chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",        prazo_oferta_m  = 8 * 60,   id_acao         = 111
        ,   acao_nome       = "Ação 1",     pendencia       = "N",      mesa_atual      = "N4-FOO-BAR"
        ,   data_acao       = "2020-01-01 09:15:00"
        ,   data_fim_acao   = "2020-01-01 09:30:00"
        ,   duracao_m       = 15*60
        )
        self.evt2 = Event(
            id_chamado      = "124",        chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",        prazo_oferta_m  = 8 * 60,   id_acao         = 112
        ,   acao_nome       = "Ação 2",     pendencia       = "S",      mesa_atual      = "N4-FOO-BAR"
        ,   data_acao       = "2020-01-01 09:30:00"
        ,   data_fim_acao   = "2020-01-01 09:45:00"
        ,   duracao_m       = 0
        )        
        self.evt3 = Event(
            id_chamado      = "123" ,       chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",        prazo_oferta_m  = 8 * 60,   id_acao         = 111
        ,   acao_nome       = "Ação 1",     pendencia       = "N",      mesa_atual      = "N4-FOO-BAR"
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
            id_chamado      = "123" ,       chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",        prazo_oferta_m  = 8 * 60,   id_acao         = 111
        ,   acao_nome       = "Ação 1",     pendencia       = "N",      mesa_atual      = "N4-FOO-BAR"
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
            id_chamado      = "124",        chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",        prazo_oferta_m  = 8 * 60,   id_acao         = 112
        ,   acao_nome       = "Ação 2",     pendencia       = "S",      mesa_atual      = "N4-FOO-BAR"
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
            id_chamado      = "123" ,       chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",        prazo_oferta_m  = 8 * 60,   id_acao         = 111
        ,   acao_nome       = "Ação 1",     pendencia       = "N",      mesa_atual      = "N4-FOO-BAR"
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
            id_chamado      = "124",        chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",        prazo_oferta_m  = 8 * 60,   id_acao         = 112
        ,   acao_nome       = "Ação 2",     pendencia       = "S",      mesa_atual      = "N4-FOO-BAR"
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
    
    def test_it_calcutate_durations(self):
        inc = Incidente(id_chamado="123", chamado_pai=None, categoria="CORRIGIR-NÃO EMERGENCIAL", oferta="Suporte ao Serviço de SAP", prazo=540)
        actions = [
            Acao(id_acao=1,  acao_nome="ação 1",  pendencia="N", mesa_atual="MESA 1", data_acao="2020-01-01 09:10:00", data_fim_acao="2020-01-01 09:20:00", duracao_m=10*60),
            Acao(id_acao=2,  acao_nome="ação 2",  pendencia="S", mesa_atual="MESA 1", data_acao="2020-01-01 09:20:00", data_fim_acao="2020-01-01 09:30:00", duracao_m=10*60),
            Acao(id_acao=3,  acao_nome="ação 3",  pendencia="N", mesa_atual="MESA 1", data_acao="2020-01-01 09:30:00", data_fim_acao="2020-01-01 09:40:00", duracao_m=10*60),
            
            Acao(id_acao=4,  acao_nome="ação 4",  pendencia="N", mesa_atual="MESA 2", data_acao="2020-01-01 09:40:00", data_fim_acao="2020-01-01 09:50:00", duracao_m=10*60),
            Acao(id_acao=5,  acao_nome="ação 5",  pendencia="S", mesa_atual="MESA 2", data_acao="2020-01-01 09:50:00", data_fim_acao="2020-01-01 10:00:00", duracao_m=10*60),
            Acao(id_acao=6,  acao_nome="ação 6",  pendencia="N", mesa_atual="MESA 2", data_acao="2020-01-01 10:00:00", data_fim_acao="2020-01-01 10:10:00", duracao_m=10*60),
            
            Acao(id_acao=7,  acao_nome="ação 7",  pendencia="S", mesa_atual="MESA 3", data_acao="2020-01-01 10:10:00", data_fim_acao="2020-01-01 10:20:00", duracao_m=10*60),
            Acao(id_acao=8,  acao_nome="ação 8",  pendencia="N", mesa_atual="MESA 3", data_acao="2020-01-01 10:20:00", data_fim_acao="2020-01-01 10:30:00", duracao_m=10*60),
            Acao(id_acao=9,  acao_nome="ação 9",  pendencia="S", mesa_atual="MESA 3", data_acao="2020-01-01 10:30:00", data_fim_acao="2020-01-01 10:40:00", duracao_m=10*60),
            
            Acao(id_acao=10, acao_nome="ação 10", pendencia="N", mesa_atual="MESA 4", data_acao="2020-01-01 10:40:00", data_fim_acao="2020-01-01 10:50:00", duracao_m=10*60),
            Acao(id_acao=11, acao_nome="ação 11", pendencia="S", mesa_atual="MESA 4", data_acao="2020-01-01 10:50:00", data_fim_acao="2020-01-01 11:00:00", duracao_m=10*60),
            Acao(id_acao=12, acao_nome="ação 12", pendencia="N", mesa_atual="MESA 4", data_acao="2020-01-01 11:00:00", data_fim_acao=None,                  duracao_m=10*60)
        ]
        for action in actions:
            inc.add_acao(action)
        
        duration = inc.calc_duration()
        self.assertEqual(duration, 70 * 60)
        
        duration = inc.calc_duration_mesas([ "MESA 1" ])
        self.assertEqual(duration, 20 * 60)
        
        duration = inc.calc_duration_mesas([ "MESA 2" ])
        self.assertEqual(duration, 20 * 60)
        
        duration = inc.calc_duration_mesas([ "MESA 3" ])
        self.assertEqual(duration, 10 * 60)
        
        duration = inc.calc_duration_mesas([ "MESA 4" ])
        self.assertEqual(duration, 20 * 60)
        
        duration = inc.calc_duration_mesas([ "MESA 1", "MESA 3" ])
        self.assertEqual(duration, 30 * 60)
        
        duration = inc.calc_duration_mesas([ "MESA 2", "MESA 4" ])
        self.assertEqual(duration, 40 * 60)
        
        
        
class TestClick(unittest.TestCase):
    
    def setUp(self):
        self.click = Click()
        self.eventos = [
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2210767, 'Atribuição interna',                  'N', 'N1-SD2_EMAIL',	                                '2020-03-01 02:06:57', '2020-03-01 02:06:57', 0     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2210768, 'Atribuir ao Fornecedor',              'N', 'N1-SD2_EMAIL',	                                '2020-03-01 02:06:57', '2020-03-01 02:08:32', 2     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2210771, 'Atribuição interna',                  'N', 'N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC',	'2020-03-01 02:08:32', '2020-03-01 02:08:32', 0     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2210773, 'Atribuir ao Fornecedor',              'N', 'N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC',	'2020-03-01 02:08:32', '2020-03-01 02:15:40', 7     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2210795, 'Atribuição interna',                  'N', 'N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC',	'2020-03-01 02:15:40', '2020-03-01 02:17:59', 2     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2210798, 'Atribuição interna',                  'N', 'N2-SD2_SAP_SERV',	                                '2020-03-01 02:17:59', '2020-03-01 02:17:59', 0     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2210800, 'Atribuir ao Fornecedor',              'N', 'N2-SD2_SAP_SERV',	                                '2020-03-01 02:17:59', '2020-03-02 06:59:42', 0     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2232985, 'Atribuição interna',                  'N', 'N2-SD2_SAP_PRAPO',	                            '2020-03-02 07:18:56', '2020-03-02 07:22:55', 4     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2232509, 'Atribuição interna',                  'N', 'N2-SD2_SAP_PRAPO',	                            '2020-03-02 06:59:42', '2020-03-02 07:18:56', 18    ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2233103, 'Atribuição interna',                  'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-03-02 07:22:55', '2020-03-02 07:22:55', 0     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2233105, 'Atribuir ao Fornecedor',              'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-03-02 07:22:55', '2020-03-02 08:15:52', 0     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2237852, 'Atribuição interna',                  'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-03-02 08:15:52', '2020-03-02 08:18:29', 0     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2238140, 'Atribuição interna',                  'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-03-02 08:18:29', '2020-03-04 10:56:38', 1196  ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2536139, 'Aguardando Cliente',                  'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-03-04 10:56:38', '2020-03-04 10:56:39', 0     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2536145, 'Aguardando Cliente - Fornecedor',     'S', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-03-04 10:56:39', '2020-03-04 11:29:13', 33    ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2544197, 'Retorno do usuário',                  'S', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-03-04 11:29:13', '2020-03-04 11:29:18', 0     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2544226, 'Pendência Sanada',                    'S', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-03-04 11:29:18', '2020-03-04 11:29:22', 0     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2544258, 'Pendência Sanada - Fornecedor/TIC',   'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-03-04 11:29:22', '2020-03-06 10:54:10', 1045  ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2819882, 'Atribuição interna',                  'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-03-06 10:54:10', '2020-04-22 08:32:24', 16626 ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 7614533, 'Atribuição interna',                  'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-04-22 08:32:24', '2020-04-22 08:32:24', 0     ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 7614535, 'Atribuir ao Fornecedor',              'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-04-22 08:32:24', '2020-04-30 19:37:33', 3780  ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 8315407, 'Atribuição interna',                  'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-04-30 19:37:33', '2020-05-05 14:00:31', 840   ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 8535968, 'Atribuição interna',                  'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-05-05 14:00:31', '2020-05-08 18:30:17', 1860  ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 8875072, 'Atribuição interna',                  'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-05-08 18:30:17', '2020-05-11 17:43:36', 523   ),
            Event('119773', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 9009952, 'Atribuição interna',                  'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 	            '2020-05-11 17:43:36', None,	              5417  ),
            
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2032069, 'Atribuição interna',	                'N', 'N1-SD2_WEB',	                                    '2020-02-27 15:14:52', '2020-02-27 15:14:52', 0	    ),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2032070, 'Atribuir ao Fornecedor',	            'N', 'N1-SD2_WEB',	                                    '2020-02-27 15:14:52', '2020-02-27 15:14:57', 0	    ),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2032071, 'Campo do formulário alterado',        'N', 'N1-SD2_WEB',	                                    '2020-02-27 15:14:57', '2020-02-27 15:23:33', 9	    ),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2034015, 'Atribuição interna', 	                'N', 'N1-SD2_WEB',	                                    '2020-02-27 15:23:33', '2020-02-27 15:44:14', 21	),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2038309, 'Atribuição interna', 	                'N', 'N2-SD2_SAP_PRAPO',	                            '2020-02-27 15:44:14', '2020-02-27 15:44:14', 0	    ),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2038315, 'Atribuir ao Fornecedor',	            'N', 'N2-SD2_SAP_PRAPO',	                            '2020-02-27 15:44:14', '2020-02-27 15:56:56', 12	),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2041363, 'Atribuição interna', 	                'N', 'N2-SD2_SAP_PRAPO',	                            '2020-02-27 15:56:56', '2020-02-27 15:59:16', 3	    ),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2041836, 'Atribuição interna', 	                'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-02-27 15:59:16', '2020-02-27 15:59:16', 0	    ),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2041841, 'Atribuir ao Fornecedor',	            'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-02-27 15:59:16', '2020-02-27 16:00:59', 1	    ),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2042290, 'Atribuição interna',	                'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-02-27 16:00:59', '2020-02-28 17:33:57', 633	),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2158921, 'Campos alterados',	                'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-02-28 17:33:57', '2020-02-28 17:34:16', 1	    ),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2158951, 'Atribuição interna',	                'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-02-28 17:34:16', '2020-03-02 14:58:48', 384	),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2317548, 'Atribuição interna',	                'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-03-02 14:58:48', '2020-03-03 17:55:48', 717	),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2479011, 'Campos alterados',                    'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-03-03 17:55:48', '2020-03-05 17:37:11', 1062	),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2764051, 'Campos alterados',                    'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-03-05 17:37:11', '2020-03-05 17:39:11', 2	    ),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 2764262, 'Campos alterados',                    'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-03-05 17:39:11', '2020-04-06 10:15:47', 11436	),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 6349995, 'Pendência de TIC',                    'S', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-04-06 10:15:47', '2020-04-20 10:34:54', 4879	),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 7519497, 'Aguardando Cliente',	                'S', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-04-20 10:34:54', '2020-04-27 15:25:06', 2451	),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 7988865, 'Retorno do usuário',	                'S', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-04-27 15:25:06', '2020-04-27 15:25:07', 0     ),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 7988868, 'Pendência Sanada - Fornecedor/TIC',   'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-04-27 15:25:09', '2020-04-27 15:26:34', 1     ),            
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540, 7988866, 'Pendência Sanada',	                'S', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-04-27 15:25:07', '2020-04-27 15:25:09', 0     ),
            Event('110322', None, 'CORRIGIR-NÃO EMERGENCIAL', 'Suporte ao serviço de SAP', 540,	7989088, 'Resolver',                            'N', 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',	            '2020-04-27 15:26:34', None,		          0     )
        ]
        self.eventos.sort(key=lambda x: x.data_acao)
    def tearDown(self):
        pass
    
    def test_it_process_events(self):
        for evt in self.eventos:
            self.click.update(evt)
        self.assertEqual(2, self.click.incident_count())
        
        incidente = self.click.get_incidente('119773')
        self.assertEqual(incidente.id_chamado, '119773')
        self.assertEqual(incidente.chamado_pai, None)
        self.assertEqual(incidente.categoria, 'CORRIGIR-NÃO EMERGENCIAL')
        self.assertEqual(incidente.oferta, 'Suporte ao serviço de SAP')
        self.assertEqual(incidente.prazo, 540)
        self.assertEqual(incidente.action_count(), 25)
        self.assertEqual(incidente.calc_duration(), 31320)
        self.assertEqual(incidente.calc_duration_mesas([ 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' ]), 31287)
        
        incidente = self.click.get_incidente('110322')
        self.assertEqual(incidente.id_chamado, '110322')
        self.assertEqual(incidente.chamado_pai, None)
        self.assertEqual(incidente.categoria, 'CORRIGIR-NÃO EMERGENCIAL')
        self.assertEqual(incidente.oferta, 'Suporte ao serviço de SAP')
        self.assertEqual(incidente.prazo, 540)
        self.assertEqual(incidente.action_count(), 22)
        self.assertEqual(incidente.calc_duration(), 14282)
        self.assertEqual(incidente.calc_duration_mesas([ 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' ]), 14237)
        