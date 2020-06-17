import unittest
from pyclick.models import *
from pyclick.n4sap.estoque import Estoque

class TestEstoque(unittest.TestCase):
    
    def setUp(self):
        self.click = Click()
        self.estoque = Estoque()
        self.start_dt = '2020-04-26 00:00:00'
        self.end_dt = '2020-05-26 00:00:00'        
        
        
    def tearDown(self):
        pass
    
    def test_it_computes_the_kpi_for_no_incidents(self):
        kpi, observation = self.estoque.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente no estoque", observation)
        
    
    def test_it_does_not_compute_the_kpi_for_a_closed_incident(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	9999699
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Resolver	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-26 01:02:03		0
        """)
        for evt in evts:
            self.click.update(evt)
        inc = self.click.get_incidente('XXXXXX')
        self.estoque.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.estoque.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente no estoque", observation)

    def test_it_computes_the_kpi_for_an_open_incident(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	9999699
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Item alterado	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-26 01:02:03		0
        """)
        for evt in evts:
            self.click.update(evt)
        inc = self.click.get_incidente('XXXXXX')
        self.estoque.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.estoque.get_result()
        self.assertEqual(1, kpi)
        self.assertEqual("1 incidentes no estoque", observation)
        
    def test_it_skips_incs_with_prior_assignments_and_no_current_assigment(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-24 23:59:59	999961
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N4-SAP-XXXXXXXXXXXXXXXXXXXX	2020-04-24 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.estoque.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.estoque.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente no estoque", observation)

    def test_it_skips_incs_with_prior_assignments_closed_within_period_that_are_not_the_last_group(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	9999699
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	N	N6-SAP-XXXXXXXXXXXXXXXXXXXX	2020-04-26 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.estoque.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.estoque.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente no estoque", observation)
