import unittest
from pyclick.models import *
from pyclick.n4sap.models import *
from pyclick.n4sap.peso30 import Peso30

class TestPeso30(unittest.TestCase):
    
    def setUp(self):
        self.incsrv = IncidentService()
        self.click = ClickN4(self.incsrv)
        self.peso30 = Peso30(self.incsrv)
        self.start_dt = '2020-04-26 00:00:00'
        self.end_dt = '2020-05-26 00:00:00'        
                
    def tearDown(self):
        pass
    
    def test_it_computes_the_kpi_for_no_incidents(self):
        kpi, observation = self.peso30.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente peso 30 processado", observation)
        
    def test_it_skips_incs_with_prior_assignments_and_no_current_assigment(self):
        evts = Event.parse_events(r"""
            AAAAAA		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-24 00:00:00	2020-04-24 23:59:59	999961
            AAAAAA		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N4-SAP-XXXXXXXXXXXXXXXXXXXX	2020-04-24 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.peso30.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.peso30.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente peso 30 processado", observation)

    def test_it_computes_the_kpi_for_a_closed_incident(self):
        evts = Event.parse_events(r"""
            BBBBBB		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-24 00:00:00	2020-04-26 23:59:59	9999699
            BBBBBB		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Resolver	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-26 01:02:03		0
        """)
        for evt in evts:
            self.click.update(evt)
        self.peso30.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.peso30.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes escalados", observation)
    
    def test_it_computes_the_kpi_for_an_open_incident(self):
        evts = Event.parse_events(r"""
            CCCCCC		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-24 00:00:00	2020-04-26 23:59:59	30
            CCCCCC		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Iniciar Atendimento	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-26 01:02:03		0
        """)
        for evt in evts:
            self.click.update(evt)
        self.peso30.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.peso30.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente peso 30 processado", observation)
    
    def test_it_computes_the_kpi_for_a_breached_open_incident(self):
        evts = Event.parse_events(r"""
            CCCCCC		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-24 00:00:00	2020-04-26 23:59:59	999999
            CCCCCC		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Iniciar Atendimento	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-26 01:02:03		0
        """)
        for evt in evts:
            self.click.update(evt)
        self.peso30.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.peso30.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes escalados", observation)
    
    if False:            
        def test_it_computes_the_kpi(self):
            evts = Event.parse_events(r"""
                AAAAAA		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-24 23:59:59	999961
                AAAAAA		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N4-SAP-XXXXXXXXXXXXXXXXXXXX	2020-04-24 23:59:59	2020-05-05 14:37:34	0
                BBBBBB		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	9999699
                BBBBBB		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Iniciar Atendimento	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-26 01:02:03		0
                CCCCCC		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	9999699
                CCCCCC		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Cancelar	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-26 01:02:03		0
                DDDDDD		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	9999699
                DDDDDD		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Cancelar	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-26 01:02:03		0        
            """)
            for evt in evts:
                self.click.update(evt)
            self.pendfech.evaluate(self.click, self.start_dt, self.end_dt)
            kpi, observation = self.pendfech.get_result()
            self.assertEqual(50.0, kpi)
            self.assertEqual("1 inc.s pend. fech. / 2 incidentes", observation)
