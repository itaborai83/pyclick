import unittest
from pyclick.models import *
            
class TestEvento(unittest.TestCase):

    def setUp(self):
        self.evt1 = Event(
            id_chamado      = "123" ,               chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",                prazo_oferta_m  = 8 * 60,   id_acao         = 111
        ,   acao_nome       = "Campos alterados",   pendencia       = "N",      mesa_atual      = "N4-FOO-BAR"
        ,   data_acao       = "2020-01-01 09:15:00"
        ,   data_fim_acao   = "2020-01-01 09:30:00"
        ,   duracao_m       = 15*60
        )
        self.evt2 = Event(
            id_chamado      = "124",                chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",                prazo_oferta_m  = 8 * 60,   id_acao         = 112
        ,   acao_nome       = "Campos alterados",   pendencia       = "S",      mesa_atual      = "N4-FOO-BAR"
        ,   data_acao       = "2020-01-01 09:30:00"
        ,   data_fim_acao   = "2020-01-01 09:45:00"
        ,   duracao_m       = 0
        )        
        self.evt3 = Event(
            id_chamado      = "123" ,               chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",                prazo_oferta_m  = 8 * 60,   id_acao         = 111
        ,   acao_nome       = "Campos alterados",   pendencia       = "N",      mesa_atual      = "N4-FOO-BAR"
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
    
    def test_it_parse_an_event(self):
        txt_evento = r"400982		ORIENTAR	Dúvida sobre o serviço	99960	7322803	Atribuição interna	N	N1-SD2_SAP	2020-04-16 16:09:32	2020-04-16 16:09:32	0"
        evt = Event.parse_event(txt_evento)
        self.assertEqual(evt.id_chamado      , '400982')
        self.assertEqual(evt.chamado_pai     , None)
        self.assertEqual(evt.categoria       , 'ORIENTAR')
        self.assertEqual(evt.oferta_catalogo , 'Dúvida sobre o serviço')
        self.assertEqual(evt.prazo_oferta_m  , 99960)
        self.assertEqual(evt.id_acao         , 7322803)
        self.assertEqual(evt.acao_nome       , 'Atribuição interna')
        self.assertEqual(evt.pendencia       , 'N')
        self.assertEqual(evt.mesa_atual      , 'N1-SD2_SAP')
        self.assertEqual(evt.data_acao       , '2020-04-16 16:09:32')
        self.assertEqual(evt.data_fim_acao   , '2020-04-16 16:09:32')
        self.assertEqual(evt.duracao_m       , 0)

    def test_it_parse_events(self):
        txt_eventos = r"""            
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7322803	Atribuição interna	N	N1-SD2_SAP	2020-04-16 16:09:32	2020-04-16 16:09:32	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7322804	Atribuir ao Fornecedor	N	N1-SD2_SAP	2020-04-16 16:09:32	2020-04-16 16:20:18	11
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7324671	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:20:18	2020-04-16 16:20:18	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7324673	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:20:18	2020-04-16 16:23:08	3
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7325015	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:23:08	2020-04-17 11:02:00	219
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7380505	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 11:02:00	2020-04-17 11:02:00	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7380508	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 11:02:00	2020-04-17 17:59:49	417
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7437217	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 17:59:49	2020-04-17 17:59:50	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7437218	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 17:59:50	2020-05-04 21:31:00	24692
            400982		ORIENTAR	Dúvida sobre o serviço	99960	8474333	Resolver	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 21:31:00	2020-05-06 21:32:56	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	8678175	Encerrar	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 21:32:56		0        
        """
        evts = Event.parse_events(txt_eventos)
        self.assertEqual(11, len(evts))
        self.assertEqual(evts[ -1 ].id_chamado      , '400982')
        self.assertEqual(evts[ -1 ].chamado_pai     , None)
        self.assertEqual(evts[ -1 ].categoria       , 'ORIENTAR')
        self.assertEqual(evts[ -1 ].oferta_catalogo , 'Dúvida sobre o serviço')
        self.assertEqual(evts[ -1 ].prazo_oferta_m  , 99960)
        self.assertEqual(evts[ -1 ].id_acao         , 8678175)
        self.assertEqual(evts[ -1 ].acao_nome       , 'Encerrar')
        self.assertEqual(evts[ -1 ].pendencia       , 'S')
        self.assertEqual(evts[ -1 ].mesa_atual      , 'N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(evts[ -1 ].data_acao       , '2020-05-06 21:32:56')
        self.assertEqual(evts[ -1 ].data_fim_acao   , None)
        self.assertEqual(evts[ -1 ].duracao_m       , 0)   
        
class TestAcao(unittest.TestCase):

    def setUp(self):
        self.evt1 = Event(
            id_chamado      = "123" ,               chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",                prazo_oferta_m  = 8 * 60,   id_acao         = 111
        ,   acao_nome       = "Campos alterados",   pendencia       = "N",      mesa_atual      = "N4-FOO-BAR"
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
            id_chamado      = "124",                chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",                prazo_oferta_m  = 8 * 60,   id_acao         = 112
        ,   acao_nome       = "Campos alterados",   pendencia       = "S",      mesa_atual      = "N4-FOO-BAR"
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
    
    def test_it_has_an_status(self):
        self.act1.acao_nome = 'Resolver'
        self.assertEqual(self.act1.status, 'RESOLVIDO')
        
        self.act1.acao_nome = 'Resolver Fornecedor - Executar antes do "Resolver"!'
        self.assertEqual(self.act1.status, 'RESOLVIDO')    
        
        self.act1.acao_nome = 'Encerrar'
        self.assertEqual(self.act1.status, 'ENCERRADO')
        
        self.act1.acao_nome = 'Cancelar'
        self.assertEqual(self.act1.status, 'CANCELADO')

        self.act1.acao_nome = 'Cancelado'
        self.assertEqual(self.act1.status, 'CANCELADO')
        
        for nome, status in STATUS_MAPPING.items():
            self.act1.acao_nome = nome
            self.assertEqual(self.act1.status, status)
        
class TestIncident(unittest.TestCase):

    def setUp(self):
        self.evt1 = Event(
            id_chamado      = "123" ,               chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",                prazo_oferta_m  = 8 * 60,   id_acao         = 111
        ,   acao_nome       = "Campos alterados",   pendencia       = "N",      mesa_atual      = "N4-FOO-BAR"
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
            id_chamado      = "124",                chamado_pai     = None,     categoria       = "CAT1"
        ,   oferta_catalogo = "OF1",                prazo_oferta_m  = 8 * 60,   id_acao         = 112
        ,   acao_nome       = "Campos alterados",   pendencia       = "S",      mesa_atual      = "N4-FOO-BAR"
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
        self.inc = Incidente(id_chamado="123", chamado_pai=None, categoria="CORRIGIR-NÃO EMERGENCIAL", oferta="Suporte ao Serviço de SAP", prazo=540)
        self.actions = [
            Acao(id_acao=1,  acao_nome="Campos alterados",  pendencia="N", mesa_atual="MESA 1", data_acao="2020-01-01 09:10:00", data_fim_acao="2020-01-01 09:20:00", duracao_m=10),
            Acao(id_acao=2,  acao_nome="Campos alterados",  pendencia="S", mesa_atual="MESA 1", data_acao="2020-01-01 09:20:00", data_fim_acao="2020-01-01 09:30:00", duracao_m=10),
            Acao(id_acao=3,  acao_nome="Campos alterados",  pendencia="N", mesa_atual="MESA 1", data_acao="2020-01-01 09:30:00", data_fim_acao="2020-01-01 09:40:00", duracao_m=10),
            
            Acao(id_acao=4,  acao_nome="Campos alterados",  pendencia="N", mesa_atual="MESA 2", data_acao="2020-01-01 09:40:00", data_fim_acao="2020-01-01 09:50:00", duracao_m=10),
            Acao(id_acao=5,  acao_nome="Campos alterados",  pendencia="S", mesa_atual="MESA 2", data_acao="2020-01-01 09:50:00", data_fim_acao="2020-01-01 10:00:00", duracao_m=10),
            Acao(id_acao=6,  acao_nome="Campos alterados",  pendencia="N", mesa_atual="MESA 2", data_acao="2020-01-01 10:00:00", data_fim_acao="2020-01-01 10:10:00", duracao_m=10),
            
            Acao(id_acao=7,  acao_nome="Campos alterados",  pendencia="S", mesa_atual="MESA 3", data_acao="2020-01-01 10:10:00", data_fim_acao="2020-01-01 10:20:00", duracao_m=10),
            Acao(id_acao=8,  acao_nome="Campos alterados",  pendencia="N", mesa_atual="MESA 3", data_acao="2020-01-01 10:20:00", data_fim_acao="2020-01-01 10:30:00", duracao_m=10),
            Acao(id_acao=9,  acao_nome="Campos alterados",  pendencia="S", mesa_atual="MESA 3", data_acao="2020-01-01 10:30:00", data_fim_acao="2020-01-01 10:40:00", duracao_m=10),
            
            Acao(id_acao=10, acao_nome="Campos alterados", pendencia="N", mesa_atual="MESA 4", data_acao="2020-01-01 10:40:00", data_fim_acao="2020-01-01 10:50:00", duracao_m=10),
            Acao(id_acao=11, acao_nome="Campos alterados", pendencia="S", mesa_atual="MESA 4", data_acao="2020-01-01 10:50:00", data_fim_acao="2020-01-01 11:00:00", duracao_m=10),
            Acao(id_acao=12, acao_nome="Resolver", pendencia="N", mesa_atual="MESA 4", data_acao="2020-01-01 11:00:00", data_fim_acao=None,                  duracao_m=10)
        ]
        
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
        for action in self.actions:
            self.inc.add_acao(action)
        
        duration = self.inc.calc_duration()
        self.assertEqual(duration, 70)
        
        duration = self.inc.calc_duration_mesas([ "MESA 1" ])
        self.assertEqual(duration, 20)
        
        duration = self.inc.calc_duration_mesas([ "MESA 2" ])
        self.assertEqual(duration, 20)
        
        duration = self.inc.calc_duration_mesas([ "MESA 3" ])
        self.assertEqual(duration, 10)
        
        duration = self.inc.calc_duration_mesas([ "MESA 4" ])
        self.assertEqual(duration, 20)
        
        duration = self.inc.calc_duration_mesas([ "MESA 1", "MESA 3" ])
        self.assertEqual(duration, 30)
        
        duration = self.inc.calc_duration_mesas([ "MESA 2", "MESA 4" ])
        self.assertEqual(duration, 40)
    
    def test_it_has_an_status(self):
        for action in self.actions:
            self.inc.add_acao(action)
        for nome, status in STATUS_MAPPING.items():
            self.inc.acoes[ -1 ].acao_nome = nome
            self.assertEqual(self.inc.status, status)
    
    def test_it_tracks_assignments(self):
        for action in self.actions:
            self.inc.add_acao(action)
        self.assertEqual(len(self.inc.atribuicoes), 4)
        
        atrib = self.inc.atribuicoes[ 0 ]
        self.assertEqual(atrib.seq, 1)
        self.assertEqual(atrib.mesa, "MESA 1")
        self.assertEqual(atrib.entrada, "2020-01-01 09:10:00")
        self.assertEqual(atrib.status_entrada, "ABERTO")
        self.assertEqual(atrib.saida, "2020-01-01 09:40:00")
        self.assertEqual(atrib.status_saida, "ABERTO")
        self.assertEqual(atrib.duracao_m, 20)
        self.assertEqual(atrib.pendencia_m, 10)
        
        atrib = self.inc.atribuicoes[ 1 ]
        self.assertEqual(atrib.seq, 2)
        self.assertEqual(atrib.mesa, "MESA 2")
        self.assertEqual(atrib.entrada, "2020-01-01 09:40:00")
        self.assertEqual(atrib.status_entrada, "ABERTO")
        self.assertEqual(atrib.saida, "2020-01-01 10:10:00")
        self.assertEqual(atrib.status_saida, "ABERTO")
        self.assertEqual(atrib.duracao_m, 20)
        self.assertEqual(atrib.pendencia_m, 10)
        
        atrib = self.inc.atribuicoes[ 2 ]
        self.assertEqual(atrib.seq, 3)
        self.assertEqual(atrib.mesa, "MESA 3")
        self.assertEqual(atrib.entrada, "2020-01-01 10:10:00")
        self.assertEqual(atrib.status_entrada, "ABERTO")
        self.assertEqual(atrib.saida, "2020-01-01 10:40:00")
        self.assertEqual(atrib.status_saida, "ABERTO")
        self.assertEqual(atrib.duracao_m, 10)
        self.assertEqual(atrib.pendencia_m, 20)
        
        atrib = self.inc.atribuicoes[ 3 ]
        self.assertEqual(atrib.seq, 4)
        self.assertEqual(atrib.mesa, "MESA 4")
        self.assertEqual(atrib.entrada, "2020-01-01 10:40:00")
        self.assertEqual(atrib.status_entrada, "ABERTO")
        self.assertEqual(atrib.saida, None)
        self.assertEqual(atrib.status_saida, "RESOLVIDO")
        self.assertEqual(atrib.duracao_m, 20)
        self.assertEqual(atrib.pendencia_m, 10)
        
class TestClick(unittest.TestCase):
    
    def setUp(self):
        self.click = Click()
        self.eventos = Event.parse_events(r"""
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2210767	Atribuição interna	N	N1-SD2_EMAIL	2020-03-01 02:06:57	2020-03-01 02:06:57	0
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2210768	Atribuir ao Fornecedor	N	N1-SD2_EMAIL	2020-03-01 02:06:57	2020-03-01 02:08:32	2
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2210771	Atribuição interna	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-03-01 02:08:32	2020-03-01 02:08:32	0
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2210773	Atribuir ao Fornecedor	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-03-01 02:08:32	2020-03-01 02:15:40	7
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2210795	Atribuição interna	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-03-01 02:15:40	2020-03-01 02:17:59	2
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2210798	Atribuição interna	N	N2-SD2_SAP_SERV	2020-03-01 02:17:59	2020-03-01 02:17:59	0
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2210800	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-03-01 02:17:59	2020-03-02 06:59:42	0
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2232509	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-03-02 06:59:42	2020-03-02 07:18:56	18
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2232985	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-03-02 07:18:56	2020-03-02 07:22:55	4
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2233103	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-02 07:22:55	2020-03-02 07:22:55	0
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2233105	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-02 07:22:55	2020-03-02 08:15:52	0
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2237852	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-02 08:15:52	2020-03-02 08:18:29	0
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2238140	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-02 08:18:29	2020-03-04 10:56:38	1196
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2536139	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-04 10:56:38	2020-03-04 10:56:39	0
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2536145	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-04 10:56:39	2020-03-04 11:29:13	33
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2544197	Retorno do usuário	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-04 11:29:13	2020-03-04 11:29:18	0
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2544226	Pendência Sanada	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-04 11:29:18	2020-03-04 11:29:22	0
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2544258	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-04 11:29:22	2020-03-06 10:54:10	1045
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2819882	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-06 10:54:10	2020-04-22 08:32:24	16626
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7614533	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-22 08:32:24	2020-04-22 08:32:24	0
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7614535	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-22 08:32:24	2020-04-30 19:37:33	3780
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8315407	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-30 19:37:33	2020-05-05 14:00:31	840
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8535968	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-05-05 14:00:31	2020-05-08 18:30:17	1860
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8875072	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-05-08 18:30:17	2020-05-11 17:43:36	523
            119773		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9009952	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-05-11 17:43:36		5417        
        """) + Event.parse_events("""
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032069	Atribuição interna	N	N1-SD2_WEB	2020-02-27 15:14:52	2020-02-27 15:14:52	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032070	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-02-27 15:14:52	2020-02-27 15:14:57	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032071	Campo do formulário alterado	N	N1-SD2_WEB	2020-02-27 15:14:57	2020-02-27 15:23:33	9
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2034015	Atribuição interna	N	N1-SD2_WEB	2020-02-27 15:23:33	2020-02-27 15:44:14	21
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2038309	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-02-27 15:44:14	2020-02-27 15:44:14	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2038315	Atribuir ao Fornecedor	N	N2-SD2_SAP_PRAPO	2020-02-27 15:44:14	2020-02-27 15:56:56	12
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041363	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-02-27 15:56:56	2020-02-27 15:59:16	3
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041836	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-02-27 15:59:16	2020-02-27 15:59:16	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041841	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-02-27 15:59:16	2020-02-27 16:00:59	1
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2042290	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-02-27 16:00:59	2020-02-28 17:33:57	633
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2158921	Campos alterados	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-02-28 17:33:57	2020-02-28 17:34:16	1
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2158951	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-02-28 17:34:16	2020-03-02 14:58:48	384
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2317548	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-02 14:58:48	2020-03-03 17:55:48	717
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2479011	Campos alterados	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-03 17:55:48	2020-03-05 17:37:11	1062
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2764051	Campos alterados	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-05 17:37:11	2020-03-05 17:39:11	2
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2764262	Campos alterados	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-05 17:39:11	2020-04-06 10:15:47	11436
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6349995	Pendência de TIC	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-06 10:15:47	2020-04-20 10:34:54	4879
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7519497	Aguardando Cliente	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-20 10:34:54	2020-04-27 15:25:06	2451
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988865	Retorno do usuário	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 15:25:06	2020-04-27 15:25:07	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988866	Pendência Sanada	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 15:25:07	2020-04-27 15:25:09	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988868	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 15:25:09	2020-04-27 15:26:34	1
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7989088	Resolver	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 15:26:34		0        
        """) + Event.parse_events("""
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411672	Atribuição interna	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 11:17:56	2020-05-04 11:17:56	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411674	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 11:17:56	2020-05-04 11:18:14	1
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411714	Aguardando Cliente - Aprovação	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 11:18:14	2020-05-04 11:18:14	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411718	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 11:18:14	2020-05-04 11:18:29	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411772	Pendência Sanada - Aprovação	S	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 11:18:29	2020-05-04 11:18:30	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411774	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 11:18:30	2020-05-04 11:20:38	2
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8412271	Atribuição interna	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 11:20:38	2020-05-05 16:12:48	832
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8557671	Atendimento Agendado	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-05 16:12:48	2020-05-05 16:12:49	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8557672	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-05 16:12:49	2020-05-06 09:47:26	155
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8597552	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-06 09:47:26	2020-05-06 09:47:27	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8597555	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-06 09:47:27	2020-05-06 09:55:14	8
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8598963	Resolver	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-06 09:55:14	2020-05-08 09:58:04	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8804245	Encerrar	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-08 09:58:04		0        
        """) + Event.parse_events("""
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411754	Atribuição interna	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 11:18:24	2020-05-04 11:18:24	0
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411756	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 11:18:24	2020-05-04 11:21:30	3
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8412440	Atribuição interna	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 11:21:30	2020-05-06 09:55:13	994
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8598958	Resolver	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-06 09:55:13		0        
        """)
        self.eventos.sort(key=lambda x: x.data_acao)
    
    def tearDown(self):
        pass
    
    def test_it_process_events(self):
        for evt in self.eventos:
            self.click.update(evt)
        self.assertEqual(4, self.click.incident_count())
        
        incidente = self.click.get_incidente('119773')
        mesa = self.click.get_mesa('N4-SAP-SUSTENTACAO-APOIO_OPERACAO')
        self.assertEqual(incidente.id_chamado, '119773')
        self.assertEqual(incidente.chamado_pai, None)
        self.assertEqual(incidente.categoria, 'CORRIGIR-NÃO EMERGENCIAL')
        self.assertEqual(incidente.oferta, 'Suporte ao serviço de SAP')
        self.assertEqual(incidente.prazo, 540)
        self.assertEqual(incidente.action_count, 25)
        self.assertEqual(incidente.calc_duration(), 31320)
        self.assertEqual(incidente.calc_duration_mesas([ 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' ]), 31287)
        self.assertEqual(self.click.calc_children_duration_mesas('119773', [ 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' ]), 0)
        self.assertEqual(
            incidente.calc_duration_mesas([ 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' ]),
            self.click.calc_duration_mesas('119773', [ 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' ])
        )
        self.assertEqual(incidente.mesa_atual, mesa.name)
        self.assertTrue(mesa.has_incidente(incidente.id_chamado))
        self.assertTrue(mesa.seen_incidente(incidente.id_chamado))
        self.assertFalse(self.click.get_mesa('N1-SD2_EMAIL').has_incidente(incidente.id_chamado))
        self.assertFalse(self.click.get_mesa('N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC').has_incidente(incidente.id_chamado))
        self.assertFalse(self.click.get_mesa('N2-SD2_SAP_SERV').has_incidente(incidente.id_chamado))
        self.assertFalse(self.click.get_mesa('N2-SD2_SAP_PRAPO').has_incidente(incidente.id_chamado))
        
        self.assertIn('N1-SD2_EMAIL', self.click.mesas)
        self.assertIn('N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC', self.click.mesas)
        self.assertIn('N2-SD2_SAP_SERV', self.click.mesas)
        self.assertIn('N2-SD2_SAP_PRAPO', self.click.mesas)
        
        incidente = self.click.get_incidente('110322')
        mesa = self.click.get_mesa('N4-SAP-SUSTENTACAO-APOIO_OPERACAO')
        self.assertEqual(incidente.id_chamado, '110322')
        self.assertEqual(incidente.chamado_pai, None)
        self.assertEqual(incidente.categoria, 'CORRIGIR-NÃO EMERGENCIAL')
        self.assertEqual(incidente.oferta, 'Suporte ao serviço de SAP')
        self.assertEqual(incidente.prazo, 540)
        self.assertEqual(incidente.action_count, 22)
        self.assertEqual(incidente.calc_duration(), 14282)
        self.assertEqual(incidente.calc_duration_mesas([ 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' ]), 14237)
        self.assertEqual(self.click.calc_children_duration_mesas('110322', [ 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' ]), 0)
        self.assertEqual(
            incidente.calc_duration_mesas([ 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' ]),
            self.click.calc_duration_mesas('110322', [ 'N4-SAP-SUSTENTACAO-APOIO_OPERACAO' ])
        )
        self.assertFalse(mesa.has_incidente(incidente.id_chamado)) # incident was closed
        self.assertTrue(mesa.seen_incidente(incidente.id_chamado))
        self.assertFalse(self.click.get_mesa('N1-SD2_WEB').has_incidente(incidente.id_chamado))	
        self.assertFalse(self.click.get_mesa('N2-SD2_SAP_PRAPO').has_incidente(incidente.id_chamado))
        
        self.assertIn('N1-SD2_WEB', self.click.mesas)
        self.assertIn('N2-SD2_SAP_PRAPO', self.click.mesas)
        self.assertIn('N4-SAP-SUSTENTACAO-APOIO_OPERACAO', self.click.mesas)

        incidente = self.click.get_incidente('S251253')
        mesa = self.click.get_mesa('N4-SAP-SUSTENTACAO-FINANCAS')
        self.assertEqual(incidente.id_chamado, 'S251253')
        self.assertEqual(incidente.chamado_pai, None)
        self.assertEqual(incidente.categoria, 'ATENDER')
        self.assertEqual(incidente.oferta, 'FI-AA - Alteração de atribuicao contas do razão imobilizado')
        self.assertEqual(incidente.prazo, 5400)
        self.assertEqual(incidente.action_count, 13)
        self.assertEqual(incidente.calc_duration(), 843)
        self.assertEqual(incidente.calc_duration_mesas([ 'N4-SAP-SUSTENTACAO-FINANCAS' ]), 843)
        self.assertEqual(self.click.calc_children_duration_mesas('S251253', [ 'N4-SAP-SUSTENTACAO-FINANCAS' ]), 997)
        self.assertIn('S251253', self.click.children_of)
        self.assertEqual(
            self.click.calc_children_duration_mesas('S251253', [ 'N4-SAP-SUSTENTACAO-FINANCAS' ]),
            self.click.calc_duration_mesas('S251253', [ 'N4-SAP-SUSTENTACAO-FINANCAS' ])
        )
        self.assertFalse(mesa.has_incidente(incidente.id_chamado)) # incident was closed
        self.assertTrue(mesa.seen_incidente(incidente.id_chamado))
        
        self.assertIn('N1-SD2_WEB', self.click.mesas)
        self.assertIn('N2-SD2_SAP_PRAPO', self.click.mesas)
        self.assertIn('N4-SAP-SUSTENTACAO-APOIO_OPERACAO', self.click.mesas)
        
        
        incidente = self.click.get_incidente('T465903')
        mesa = self.click.get_mesa('N4-SAP-SUSTENTACAO-FINANCAS')
        self.assertEqual(incidente.id_chamado, 'T465903')
        self.assertEqual(incidente.chamado_pai, 'S251253')
        self.assertEqual(incidente.categoria, 'Execução')
        self.assertEqual(incidente.oferta, 'FI-AA - Alteração de atribuicao contas do razão imobilizado')
        self.assertEqual(incidente.prazo, 5400)
        self.assertEqual(incidente.action_count, 4)
        self.assertEqual(incidente.calc_duration(), 997)
        self.assertEqual(incidente.calc_duration_mesas([ 'N4-SAP-SUSTENTACAO-FINANCAS' ]), 997)
        self.assertEqual(self.click.calc_children_duration_mesas('T465903', [ 'N4-SAP-SUSTENTACAO-FINANCAS' ]), 0)
        self.assertEqual(
            incidente.calc_duration_mesas([ 'N4-SAP-SUSTENTACAO-FINANCAS' ]),
            incidente.calc_duration_mesas([ 'N4-SAP-SUSTENTACAO-FINANCAS' ]),
            self.click.calc_duration_mesas('T465903', [ 'N4-SAP-SUSTENTACAO-FINANCAS' ])
        )        
        self.assertEqual(incidente.mesa_atual, mesa.name)
        self.assertFalse(mesa.has_incidente(incidente.id_chamado)) # task was closed
        self.assertTrue(mesa.seen_incidente(incidente.id_chamado))

class TestKpi(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_it_purges_incidents(self):
        kpi = Kpi()
        kpi.purge("123")
        self.assertTrue(kpi.is_purged("123"))
        self.assertFalse(kpi.is_purged("234"))

class TestN4SapKpi(unittest.TestCase):
    
    def setUp(self):
        self.n4 = N4SapKpi()
    
    def tearDown(self):
        pass
    
    def test_it_categorizes_an_incident(self):
        inc = Incidente(id_chamado="T123", chamado_pai=None, categoria=None, oferta=None, prazo=None)
        categoria = self.n4.categorizar(inc)
        self.assertEqual("ATENDER - TAREFA", categoria)

        inc = Incidente(id_chamado="S123", chamado_pai=None, categoria=None, oferta=None, prazo=None)
        categoria = self.n4.categorizar(inc)
        self.assertEqual("ATENDER", categoria)

        inc = Incidente(id_chamado="123", chamado_pai=None, categoria="fooCORRIGIRbar", oferta=None, prazo=None)
        categoria = self.n4.categorizar(inc)
        self.assertEqual("CORRIGIR", categoria)
        
        inc = Incidente(id_chamado="123", chamado_pai=None, categoria="foobar", oferta=None, prazo=None)
        categoria = self.n4.categorizar(inc)
        self.assertEqual("ORIENTAR", categoria)
        
        inc = Incidente(id_chamado="123", chamado_pai=None, categoria="foobar", oferta=None, prazo=None)
        self.n4.set_override_categoria("123", "ATENDER")
        categoria = self.n4.categorizar(inc)
        self.assertEqual("ATENDER", categoria)

class TestPrp(unittest.TestCase):
    
    def setUp(self):
        self.click = Click()
        self.prp = Prp()
        self.closed_inc_evts = Event.parse_events(r"""
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7322803	Atribuição interna	N	N1-SD2_SAP	2020-04-16 16:09:32	2020-04-16 16:09:32	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7322804	Atribuir ao Fornecedor	N	N1-SD2_SAP	2020-04-16 16:09:32	2020-04-16 16:20:18	11
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7324671	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:20:18	2020-04-16 16:20:18	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7324673	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:20:18	2020-04-16 16:23:08	3
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7325015	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:23:08	2020-04-17 11:02:00	219
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7380505	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 11:02:00	2020-04-17 11:02:00	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7380508	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 11:02:00	2020-04-17 17:59:49	417
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7437217	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 17:59:49	2020-04-17 17:59:50	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7437218	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 17:59:50	2020-05-04 21:31:00	24692
            400982		ORIENTAR	Dúvida sobre o serviço	99960	8474333	Resolver	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 21:31:00	2020-05-06 21:32:56	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	8678175	Encerrar	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 21:32:56		0        
        """)

        self.violated_closed_inc_evts = Event.parse_events(r"""
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7322803	Atribuição interna	N	N1-SD2_SAP	2020-04-16 16:09:32	2020-04-16 16:09:32	0
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7322804	Atribuir ao Fornecedor	N	N1-SD2_SAP	2020-04-16 16:09:32	2020-04-16 16:20:18	11
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7324671	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:20:18	2020-04-16 16:20:18	0
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7324673	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:20:18	2020-04-16 16:23:08	3
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7325015	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:23:08	2020-04-17 11:02:00	219
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7380505	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 11:02:00	2020-04-17 11:02:00	0
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7380508	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 11:02:00	2020-04-17 17:59:49	417
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7437217	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 17:59:49	2020-04-17 17:59:50	0
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7437218	Aguardando Cliente - Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 17:59:50	2020-05-04 21:31:00	24692
            400983		ORIENTAR	Dúvida sobre o serviço	99960	8474333	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 21:31:00	2020-05-06 21:32:56	0
            400983		ORIENTAR	Dúvida sobre o serviço	99960	8678175	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 21:32:56		0        
        """)
        
        self.solved_inc_events = Event.parse_events(r"""
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032069	Atribuição interna	N	N1-SD2_WEB	2020-02-27 15:14:52	2020-02-27 15:14:52	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032070	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-02-27 15:14:52	2020-02-27 15:14:57	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032071	Campo do formulário alterado	N	N1-SD2_WEB	2020-02-27 15:14:57	2020-02-27 15:23:33	9
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2034015	Atribuição interna	N	N1-SD2_WEB	2020-02-27 15:23:33	2020-02-27 15:44:14	21
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2038309	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-02-27 15:44:14	2020-02-27 15:44:14	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2038315	Atribuir ao Fornecedor	N	N2-SD2_SAP_PRAPO	2020-02-27 15:44:14	2020-02-27 15:56:56	12
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041363	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-02-27 15:56:56	2020-02-27 15:59:16	3
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041836	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 15:59:16	2020-02-27 15:59:16	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041841	Atribuir ao Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 15:59:16	2020-02-27 16:00:59	1
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2042290	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 16:00:59	2020-02-28 17:33:57	633
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2158921	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-28 17:33:57	2020-02-28 17:34:16	1
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2158951	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-28 17:34:16	2020-03-02 14:58:48	384
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2317548	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-02 14:58:48	2020-03-03 17:55:48	717
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2479011	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-03 17:55:48	2020-03-05 17:37:11	1062
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2764051	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-05 17:37:11	2020-03-05 17:39:11	2
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2764262	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-05 17:39:11	2020-04-06 10:15:47	11436
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6349995	Pendência de TIC	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-06 10:15:47	2020-04-20 10:34:54	4879
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7519497	Aguardando Cliente	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-20 10:34:54	2020-04-27 15:25:06	2451
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988865	Retorno do usuário	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:06	2020-04-27 15:25:07	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988866	Pendência Sanada	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:07	2020-04-27 15:25:09	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988868	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:09	2020-04-27 15:26:34	1
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7989088	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:26:34		0
        """)

        self.violated_solved_inc_events = Event.parse_events(r"""
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032069	Atribuição interna	N	N1-SD2_WEB	2020-02-27 15:14:52	2020-02-27 15:14:52	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032070	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-02-27 15:14:52	2020-02-27 15:14:57	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032071	Campo do formulário alterado	N	N1-SD2_WEB	2020-02-27 15:14:57	2020-02-27 15:23:33	9
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2034015	Atribuição interna	N	N1-SD2_WEB	2020-02-27 15:23:33	2020-02-27 15:44:14	21
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2038309	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-02-27 15:44:14	2020-02-27 15:44:14	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2038315	Atribuir ao Fornecedor	N	N2-SD2_SAP_PRAPO	2020-02-27 15:44:14	2020-02-27 15:56:56	12
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041363	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-02-27 15:56:56	2020-02-27 15:59:16	3
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041836	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 15:59:16	2020-02-27 15:59:16	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041841	Atribuir ao Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 15:59:16	2020-02-27 16:00:59	1
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2042290	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 16:00:59	2020-02-28 17:33:57	633
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2158921	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-28 17:33:57	2020-02-28 17:34:16	1
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2158951	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-28 17:34:16	2020-03-02 14:58:48	384
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2317548	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-02 14:58:48	2020-03-03 17:55:48	717
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2479011	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-03 17:55:48	2020-03-05 17:37:11	1062
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2764051	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-05 17:37:11	2020-03-05 17:39:11	2
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2764262	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-05 17:39:11	2020-04-06 10:15:47	11436
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6349995	Pendência de TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-06 10:15:47	2020-04-20 10:34:54	4879
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7519497	Aguardando Cliente	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-20 10:34:54	2020-04-27 15:25:06	2451
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988865	Retorno do usuário	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:06	2020-04-27 15:25:07	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988866	Pendência Sanada	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:07	2020-04-27 15:25:09	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988868	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:09	2020-04-27 15:26:34	1
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7989088	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:26:34		0
        """)
        
        self.cancelled_inc_events = Event.parse_events(r"""
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772322	Atribuição interna	N	N1-SD2_WEB	2020-05-07 17:28:56	2020-05-07 17:28:56	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772324	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-05-07 17:28:56	2020-05-07 17:28:58	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772326	Campo do formulário alterado	N	N1-SD2_WEB	2020-05-07 17:28:58	2020-05-07 17:31:40	3
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772654	Atribuição interna	N	N1-SD2_WEB	2020-05-07 17:31:40	2020-05-07 17:32:57	1
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772797	Item alterado	N	N1-SD2_WEB	2020-05-07 17:32:57	2020-05-07 17:33:26	1
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772854	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-05-07 17:33:26	2020-05-07 17:33:26	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772858	Atribuir ao Fornecedor	N	N2-SD2_SAP_ABGE	2020-05-07 17:33:26	2020-05-07 17:36:24	3
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8773196	Atribuição interna	N	N2-SD2_SAP_SERV	2020-05-07 17:36:24	2020-05-07 18:05:48	29
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8775700	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:05:48	2020-05-07 18:05:48	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8775702	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:05:48	2020-05-07 18:31:18	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8777229	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:31:18	2020-05-07 19:22:25	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779407	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:22:25	2020-05-07 19:22:25	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779409	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:22:25	2020-05-07 19:29:48	7
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779634	Cancelar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:29:48	2020-05-07 19:29:54	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779635	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:29:54	2020-05-07 19:30:04	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779640	Cancelado	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:30:04		0        
        """)
        
        self.violated_cancelled_inc_events = Event.parse_events(r"""
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772322	Atribuição interna	N	N1-SD2_WEB	2020-05-07 17:28:56	2020-05-07 17:28:56	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772324	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-05-07 17:28:56	2020-05-07 17:28:58	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772326	Campo do formulário alterado	N	N1-SD2_WEB	2020-05-07 17:28:58	2020-05-07 17:31:40	3
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772654	Atribuição interna	N	N1-SD2_WEB	2020-05-07 17:31:40	2020-05-07 17:32:57	1
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772797	Item alterado	N	N1-SD2_WEB	2020-05-07 17:32:57	2020-05-07 17:33:26	1
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772854	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-05-07 17:33:26	2020-05-07 17:33:26	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772858	Atribuir ao Fornecedor	N	N2-SD2_SAP_ABGE	2020-05-07 17:33:26	2020-05-07 17:36:24	3
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8773196	Atribuição interna	N	N2-SD2_SAP_SERV	2020-05-07 17:36:24	2020-05-07 18:05:48	29
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8775700	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:05:48	2020-05-07 18:05:48	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8775702	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:05:48	2020-05-07 18:31:18	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8777229	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:31:18	2020-05-07 19:22:25	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779407	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:22:25	2020-05-07 19:22:25	540
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779409	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:22:25	2020-05-07 19:29:48	7
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779634	Cancelar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:29:48	2020-05-07 19:29:54	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779635	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:29:54	2020-05-07 19:30:04	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779640	Cancelado	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:30:04		0        
        """)
        
        self.deprioritized_inc_events = Event.parse_events(r"""
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7643434	Atribuição interna	N	N1-SD2_CHAT_HUMANO	2020-04-22 11:05:40	2020-04-22 11:05:40	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7643435	Atribuir ao Fornecedor	N	N1-SD2_CHAT_HUMANO	2020-04-22 11:05:40	2020-04-22 11:26:45	21
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7647806	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-22 11:26:45	2020-04-22 11:26:45	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7647808	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-04-22 11:26:45	2020-04-22 11:28:14	2
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7648053	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-22 11:28:14	2020-04-22 14:28:37	180
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7672162	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:28:37	2020-04-22 14:28:37	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7672167	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:28:37	2020-04-22 14:40:19	12
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7674402	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:40:19	2020-04-27 17:58:46	1818
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8010478	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-27 17:58:46	2020-04-29 16:06:57	968
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:06:57	2020-04-29 16:06:57	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8193377	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:06:57	2020-04-29 16:07:40	1
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8193482	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:07:40	2020-04-29 16:07:41	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8193485	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:07:41	2020-05-05 14:37:34	8550
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-05 14:37:34	2020-05-05 14:37:34	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8541252	Atribuir ao Fornecedor	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-05 14:37:34	2020-05-11 15:41:10	2224
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8991593	Resolver	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-11 15:41:10	2020-05-13 15:43:01	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	9192079	Encerrar	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-13 15:43:01		0        
        """)
        
        self.violated_deprioritized_inc_events = Event.parse_events(r"""
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7643434	Atribuição interna	N	N1-SD2_CHAT_HUMANO	2020-04-22 11:05:40	2020-04-22 11:05:40	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7643435	Atribuir ao Fornecedor	N	N1-SD2_CHAT_HUMANO	2020-04-22 11:05:40	2020-04-22 11:26:45	21
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7647806	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-22 11:26:45	2020-04-22 11:26:45	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7647808	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-04-22 11:26:45	2020-04-22 11:28:14	2
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7648053	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-22 11:28:14	2020-04-22 14:28:37	180
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7672162	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:28:37	2020-04-22 14:28:37	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7672167	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:28:37	2020-04-22 14:40:19	12
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7674402	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:40:19	2020-04-27 17:58:46	1818
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8010478	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-27 17:58:46	2020-04-29 16:06:57	968
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:06:57	2020-04-29 16:06:57	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8193377	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:06:57	2020-04-29 16:07:40	1
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8193482	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:07:40	2020-04-29 16:07:41	540
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8193485	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:07:41	2020-05-05 14:37:34	8550
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-05 14:37:34	2020-05-05 14:37:34	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8541252	Atribuir ao Fornecedor	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-05 14:37:34	2020-05-11 15:41:10	2224
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8991593	Resolver	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-11 15:41:10	2020-05-13 15:43:01	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	9192079	Encerrar	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-13 15:43:01		0        
        """)
        
        self.service_request_and_task_inc_events = Event.parse_events(r"""
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411672	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:17:56	2020-05-04 11:17:56	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411674	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:17:56	2020-05-04 11:18:14	1
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411714	Aguardando Cliente - Aprovação	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:14	2020-05-04 11:18:14	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411718	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:14	2020-05-04 11:18:29	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411772	Pendência Sanada - Aprovação	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:29	2020-05-04 11:18:30	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411774	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:30	2020-05-04 11:20:38	2
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8412271	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:20:38	2020-05-05 16:12:48	832
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8557671	Atendimento Agendado	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-05 16:12:48	2020-05-05 16:12:49	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8557672	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-05 16:12:49	2020-05-06 09:47:26	155
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8597552	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:47:26	2020-05-06 09:47:27	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8597555	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:47:27	2020-05-06 09:55:14	8
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8598963	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:55:14	2020-05-08 09:58:04	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8804245	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 09:58:04		0
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411754	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:24	2020-05-04 11:18:24	0
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411756	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:24	2020-05-04 11:21:30	3
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8412440	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:21:30	2020-05-06 09:55:13	994
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8598958	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:55:13		0        
        """)

        self.violated_service_request_and_task_inc_events = Event.parse_events(r"""
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411672	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:17:56	2020-05-04 11:17:56	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411674	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:17:56	2020-05-04 11:18:14	1
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411714	Aguardando Cliente - Aprovação	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:14	2020-05-04 11:18:14	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411718	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:14	2020-05-04 11:18:29	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411772	Pendência Sanada - Aprovação	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:29	2020-05-04 11:18:30	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411774	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:30	2020-05-04 11:20:38	2
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8412271	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:20:38	2020-05-05 16:12:48	832
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8557671	Atendimento Agendado	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-05 16:12:48	2020-05-05 16:12:49	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8557672	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-05 16:12:49	2020-05-06 09:47:26	155
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8597552	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:47:26	2020-05-06 09:47:27	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8597555	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:47:27	2020-05-06 09:55:14	8
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8598963	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:55:14	2020-05-08 09:58:04	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8804245	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 09:58:04		0
            T465904	S251254	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411754	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:24	2020-05-04 11:18:24	0
            T465904	S251254	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411756	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:24	2020-05-04 11:21:30	3
            T465904	S251254	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8412440	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:21:30	2020-05-06 09:55:13	994
            T465904	S251254	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8598958	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:55:13		0        
        """)
        
        self.events = self.closed_inc_evts                                \
        +             self.violated_closed_inc_evts                       \
        +             self.solved_inc_events                              \
        +             self.violated_solved_inc_events                     \
        +             self.cancelled_inc_events                           \
        +             self.violated_cancelled_inc_events                  \
        +             self.deprioritized_inc_events                       \
        +             self.violated_deprioritized_inc_events              \
        +             self.service_request_and_task_inc_events            \
        +             self.violated_service_request_and_task_inc_events        
        
    def tearDown(self):
        pass
    
    def test_it_computes_the_kpi_for_no_incidents(self):
        kpi, observation = self.prp.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente peso 35 processado", observation)

    def test_it_computes_the_kpi_for_a_closed_incident(self):
        for evt in self.closed_inc_evts:
            self.click.update(evt)
        self.prp.evaluate(self.click)
        kpi, observation = self.prp.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)

    def test_it_computes_the_kpi_for_a_closed_incident_that_violated_the_sla(self):
        for evt in self.violated_closed_inc_evts:
            self.click.update(evt)
        self.prp.evaluate(self.click)
        kpi, observation = self.prp.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_solved_inc_events(self):
        for evt in self.solved_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click)
        kpi, observation = self.prp.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
        
    def test_it_computes_the_kpi_for_solved_inc_events_that_violated_the_sla(self):
        for evt in self.violated_solved_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click)
        kpi, observation = self.prp.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_cancelles_inc_events(self):
        for evt in self.cancelled_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click)
        kpi, observation = self.prp.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_cancelles_inc_events_that_violated_the_sla(self):
        for evt in self.violated_cancelled_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click)
        kpi, observation = self.prp.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    
    def test_it_compute_the_kpi_for_deprioritized_inc_events(self):
        for evt in self.deprioritized_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click)
        kpi, observation = self.prp.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)    
    
    def test_it_compute_the_kpi_for_deprioritized_inc_events_that_violated_the_sla(self):
        for evt in self.violated_deprioritized_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click)
        kpi, observation = self.prp.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_service_requests_and_their_tasks(self):
        for evt in self.service_request_and_task_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click)
        kpi, observation = self.prp.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_service_requests_and_their_tasks_that_violated_the_sla(self):
        for evt in self.violated_service_request_and_task_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click)
        kpi, observation = self.prp.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi(self):
        for evt in self.events:
            self.click.update(evt)
        self.prp.evaluate(self.click)
        kpi, observation = self.prp.get_result()
        self.assertEqual(50.0, kpi)
        self.assertEqual("5 violações / 10 incidentes", observation)
        #self.prp.get_details().to_excel("teste.xlsx")