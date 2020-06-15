import unittest
from pyclick.models import *
from pyclick.n4sap.ids import Ids

class TestIds(unittest.TestCase):
    
    def setUp(self):
        self.click = Click()
        self.ids = Ids()
        self.start_dt = '2020-04-26 00:00:00'
        self.end_dt = '2020-05-26 00:00:00'        
        self.closed_inc_evts = Event.parse_events(r"""
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5893881	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-31 16:23:15	2020-03-31 16:23:15	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5893883	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-31 16:23:15	2020-03-31 16:23:36	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5893915	Aguardando Cliente - Aprovação	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-31 16:23:36	2020-03-31 16:23:37	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5893918	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-31 16:23:37	2020-03-31 16:42:46	19
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5896670	Atribuição interna	S	N4-SAP_DEMANDAS_PS	2020-03-31 16:42:46	2020-03-31 16:42:46	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5896673	Atribuir ao Fornecedor	S	N4-SAP_DEMANDAS_PS	2020-03-31 16:42:46	2020-03-31 17:28:34	18
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5901944	Pendência Sanada - Aprovação	S	N4-SAP_DEMANDAS_PS	2020-03-31 17:28:34	2020-04-27 11:11:43	8291
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	7950977	Atribuição interna	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 11:11:43	2020-04-27 11:11:43	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	7950980	Atribuir ao Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 11:11:43	2020-04-27 11:19:04	8
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	7952253	Atribuição interna	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 11:19:04	2020-04-27 15:14:01	235
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	7986870	Resolver	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 15:14:01	2020-04-29 16:35:25	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	8198052	Encerrar	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-29 16:35:25		0
            T327450	S188668	Execução	PS - Cadastro na YSPS_DESCONTAHRS	2700	5901939	Atribuição interna	N	N4-SAP_DEMANDAS_PS	2020-03-31 17:28:28	2020-03-31 17:28:28	0
            T327450	S188668	Execução	PS - Cadastro na YSPS_DESCONTAHRS	2700	5901940	Atribuir ao Fornecedor	N	N4-SAP_DEMANDAS_PS	2020-03-31 17:28:28	2020-04-27 15:13:57	8533
            T327450	S188668	Execução	PS - Cadastro na YSPS_DESCONTAHRS	2700	7986863	Resolver	N	N4-SAP_DEMANDAS_PS	2020-04-27 15:13:57	2020-04-27 15:13:57	0
            T327450	S188668	Execução	PS - Cadastro na YSPS_DESCONTAHRS	2700	7986866	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 15:13:57	2020-04-29 16:35:26	1162
            T327450	S188668	Execução	PS - Cadastro na YSPS_DESCONTAHRS	2700	8198055	Encerrar	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-29 16:35:26		0
        """)
        
        self.unviolated_inc_evts = Event.parse_events(r"""
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	5542992	Atribuição interna	N	N1-SD2_WEB	2020-03-26 17:10:48	2020-03-26 17:10:48	0
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	5542996	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-03-26 17:10:48	2020-03-26 17:10:51	0
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	5543000	Campo do formulário alterado	N	N1-SD2_WEB	2020-03-26 17:10:51	2020-03-26 17:15:02	5
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	5543501	Atribuição interna	N	N1-SD2_WEB	2020-03-26 17:15:02	2020-04-29 09:25:04	48490
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8133348	Atribuição interna	N	N1-SD2_WEB	2020-04-29 09:25:04	2020-04-29 09:32:03	7
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8134502	Atribuição interna	N	N1-SD2_WEB	2020-04-29 09:32:03	2020-04-29 09:32:23	0
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8134562	Atribuição interna	N	N1-SD2_WEB	2020-04-29 09:32:23	2020-04-29 09:35:08	3
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8135175	Item alterado	N	N1-SD2_WEB	2020-04-29 09:35:08	2020-04-29 09:35:41	0
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8135324	Atribuição interna	N	N2-SD2_SAP_CORP	2020-04-29 09:35:41	2020-04-29 09:35:41	0
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8135330	Atribuir ao Fornecedor	N	N2-SD2_SAP_CORP	2020-04-29 09:35:41	2020-04-29 09:38:42	3
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8135690	Atribuição interna	N	N2-SD2_SAP_CORP	2020-04-29 09:38:42	2020-04-29 09:59:15	21
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8139317	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-29 09:59:15	2020-04-29 09:59:15	0
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8139322	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-29 09:59:15	2020-04-29 10:09:30	10
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8141294	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-29 10:09:30	2020-05-06 14:07:41	2398
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8636793	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-06 14:07:41	2020-05-11 09:53:28	1366
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8939081	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-11 09:53:28	2020-05-18 15:58:17	3065
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9529260	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-18 15:58:17	2020-05-20 15:42:49	1064
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9730703	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-20 15:42:49	2020-05-20 16:30:53	48
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9738377	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-20 16:30:53	2020-05-20 16:30:54	0
            307645		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9738379	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-20 16:30:54		1710        
        """)
        
        self.less_than_180h_inc_evts = Event.parse_events(r"""
            000001		ORIENTAR	Suporte ao serviço de SAP	540	8139317	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-29 09:59:15		5400
        """)

        self.more_than_180h_and_less_than_360h_inc_evts = Event.parse_events(r"""
            000002		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8139317	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-29 09:59:15		16200
        """)
        
        self.service_request_with_more_than_360h_and_less_than_540h = Event.parse_events(r"""
            S000003		ATENDER	GRC / AC - Outros	5400	8433084	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-05-04 13:54:02	2020-05-04 13:54:02	0
            T000003	S000003	Execução	GRC / AC - Outros	5400	8433106	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-05-04 13:54:13	2020-05-04 13:54:13	27000
        """)
        
        self.events =   self.closed_inc_evts                                        \
        +               self.unviolated_inc_evts                                    \
        +               self.less_than_180h_inc_evts                                \
        +               self.more_than_180h_and_less_than_360h_inc_evts             \
        +               self.service_request_with_more_than_360h_and_less_than_540h
        
        
    def tearDown(self):
        pass
    
    def test_it_computes_the_kpi_for_no_incidents(self):
        kpi, observation = self.ids.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente aberto violando SLA", observation)

    def test_it_does_not_compute_the_kpi_for_a_closed_incident(self):
        for evt in self.closed_inc_evts:
            self.click.update(evt)
        self.ids.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.ids.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente aberto violando SLA", observation)
        
    def test_id_does_not_compute_the_kpi_for_incs_that_arent_breaching_the_sla(self):
        for evt in self.unviolated_inc_evts:
            self.click.update(evt)
        self.ids.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.ids.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente aberto violando SLA", observation)
        
    def test_it_computes_the_kpi_for_open_incs_with_less_than_180h(self):    
        for evt in self.less_than_180h_inc_evts:
            self.click.update(evt)
        self.ids.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.ids.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 ids / 1 incidentes", observation)

    def test_it_computes_the_kpi_for_open_incs_with_more_than_180h_and_less_than_360h(self):    
        for evt in self.more_than_180h_and_less_than_360h_inc_evts:
            self.click.update(evt)
        self.ids.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.ids.get_result()
        self.assertEqual(200.0, kpi)
        self.assertEqual("2 ids / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_a_service_request_with_more_than_360_and_less_than_360h(self):    
        for evt in self.service_request_with_more_than_360h_and_less_than_540h:
            self.click.update(evt)
        self.ids.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.ids.get_result()
        self.assertEqual(300.0, kpi)
        self.assertEqual("3 ids / 1 incidentes", observation)
    
    def test_it_computes_the_kpi(self):
        for evt in self.events:
            self.click.update(evt)
        self.ids.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.ids.get_result()
        self.assertEqual(200, kpi)
        self.assertEqual("6 ids / 3 incidentes", observation)
        #self.ids.get_details().to_excel("teste.xlsx")
    
    def test_it_skips_incs_with_prior_assignments_and_no_current_assigment(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-24 23:59:59	999961
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N4-SAP-XXXXXXXXXXXXXXXXXXXX	2020-04-24 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.ids.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.ids.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente aberto violando SLA", observation)

    def test_it_skips_incs_with_prior_assignments_closed_within_period_that_are_not_the_last_group(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	9999699
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	N	N6-SAP-XXXXXXXXXXXXXXXXXXXX	2020-04-26 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.ids.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.ids.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente aberto violando SLA", observation)
            