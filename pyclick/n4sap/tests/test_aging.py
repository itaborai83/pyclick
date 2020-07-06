import unittest
from pyclick.models import *
from pyclick.n4sap.aging import Aging

class TestAging(unittest.TestCase):
    
    def setUp(self):
        self.click = Click()
        self.aging = Aging(60, 90)
        self.start_dt = '2020-04-26 00:00:00'
        self.end_dt = '2020-05-26 00:00:00'        
        
        
    def tearDown(self):
        pass

    def test_it_computes_the_kpi_for_no_incidents(self):
        kpi, observation = self.aging.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente violando aging 60", observation)

    def test_it_does_not_compute_the_kpi_for_a_closed_incident(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	9999699
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Resolver	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-26 01:02:03		0
        """)
        for evt in evts:
            self.click.update(evt)
        inc = self.click.get_incidente('XXXXXX')
        self.aging.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.aging.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente violando aging 60", observation)

    def test_it_computes_the_kpi_for_an_open_incident(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-24 00:00:00	2020-04-26 23:59:59	9999699
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Item alterado	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-26 01:02:03		0
        """)
        for evt in evts:
            self.click.update(evt)
        inc = self.click.get_incidente('XXXXXX')
        self.aging.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.aging.get_result()
        self.assertEqual(1, kpi)
        self.assertEqual("1 incidentes violando aging 60", observation)

    def test_it_does_not_computes_the_kpi_for_an_opened_too_long(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2010-03-24 00:00:00	2020-04-26 23:59:59	9999699
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Item alterado	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-26 01:02:03		0
        """)
        for evt in evts:
            self.click.update(evt)
        inc = self.click.get_incidente('XXXXXX')
        self.aging.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.aging.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente violando aging 60", observation)
            
    def test_it_skips_incs_with_prior_assignments_and_no_current_assigment(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-24 00:00:00	2020-04-24 23:59:59	999961
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N4-SAP-XXXXXXXXXXXXXXXXXXXX	2020-04-24 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.aging.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.aging.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente violando aging 60", observation)