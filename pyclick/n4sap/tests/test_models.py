from pyclick.models import *
from pyclick.n4sap.models import *
import unittest
import unittest.mock as mock

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

class TestIncidentService(unittest.TestCase):

    def setUp(self):
        self.incserv = IncidentService()
        self.inc_orientar = Incidente(id_chamado='AAAAAA', chamado_pai=None, categoria='ORIENTAR', oferta='Dúvida sobre o serviço', prazo=1620)
        self.inc_corrigir = Incidente(id_chamado='BBBBBB', chamado_pai=None, categoria='CORRIGIR', oferta='Suporte ao serviço de SAP', prazo=540)
        self.inc_tarefa = Incidente(id_chamado='TCCCCC', chamado_pai='SDDDDD', categoria='Execução', oferta='HR / PY - Realização de Memória de Cálculo', prazo=45*60)
        self.inc_sreq = Incidente(id_chamado='SDDDDD', chamado_pai=None, categoria='Atender', oferta='HR / PY - Realização de Memória de Cálculo', prazo=45*60)
        self.inc_pseudo_orientar = Incidente(id_chamado='EEEEEE', chamado_pai=None, categoria='Outra Falha', oferta='Suporte aos serviços', prazo=540)
    
    def tearDown(self):
        pass
    
    def test_it_categorizes_an_incident(self):
        categoria = self.incserv.categorizar(self.inc_orientar)
        self.assertEqual('ORIENTAR', categoria)
        categoria = self.incserv.categorizar(self.inc_corrigir)
        self.assertEqual('CORRIGIR', categoria)
        categoria = self.incserv.categorizar(self.inc_tarefa)
        self.assertEqual('ATENDER - TAREFA', categoria)
        categoria = self.incserv.categorizar(self.inc_sreq)
        self.assertEqual('ATENDER', categoria)
        categoria = self.incserv.categorizar(self.inc_pseudo_orientar)
        self.assertEqual('ORIENTAR', categoria)
        self.incserv.strict_orientar = True
        categoria = self.incserv.categorizar(self.inc_pseudo_orientar)
        self.assertEqual(None, categoria)
    
    def test_it_overrides_categorization(self):
        categoria = self.incserv.categorizar(self.inc_orientar)
        self.assertEqual('ORIENTAR', categoria)
        
        self.incserv.set_override_categoria(self.inc_orientar.id_chamado, 'CORRIGIR')
        categoria = self.incserv.categorizar(self.inc_orientar)
        self.assertEqual('CORRIGIR', categoria)
        
        self.incserv.unset_override_categoria(self.inc_orientar.id_chamado)
        categoria = self.incserv.categorizar(self.inc_orientar)
        self.assertEqual('ORIENTAR', categoria)
        
    def test_it_computes_inc_duration(self):
        acao1 = Acao(id_acao=1, acao_nome='Atribuição interna', pendencia='N', mesa_atual='MESA-0', data_acao='2020-01-01 09:30:00', data_fim_acao='2020-01-01 10:00:00', duracao_m=30)
        acao2 = Acao(id_acao=2, acao_nome='Atribuição interna', pendencia='N', mesa_atual='MESA-1', data_acao='2020-01-01 10:00:00', data_fim_acao='2020-01-01 10:30:00', duracao_m=30)
        
        with self.assertRaises(AssertionError):
            self.incserv.calc_duration_mesas(self.inc_orientar, None)
        with self.assertRaises(AssertionError):
            self.incserv.calc_duration_mesas(self.inc_orientar, [])
        
        self.inc_orientar.add_acao(acao1)
        self.inc_orientar.add_acao(acao2)
        duration_m = self.incserv.calc_duration_mesas(self.inc_orientar, ['MESA-1'])
        self.assertEqual(duration_m, 30)

    def test_it_computes_inc_pending_time(self):
        acao1 = Acao(id_acao=1, acao_nome='Atribuição interna', pendencia='S', mesa_atual='MESA-1', data_acao='2020-01-01 09:30:00', data_fim_acao='2020-01-01 10:00:00', duracao_m=30)
        acao2 = Acao(id_acao=2, acao_nome='Atribuição interna', pendencia='N', mesa_atual='MESA-1', data_acao='2020-01-01 10:00:00', data_fim_acao='2020-01-01 10:25:00', duracao_m=30)
        
        with self.assertRaises(AssertionError):
            self.incserv.calc_pendencia_mesas(self.inc_orientar, None)
        with self.assertRaises(AssertionError):
            self.incserv.calc_pendencia_mesas(self.inc_orientar, [])
        
        self.inc_orientar.add_acao(acao1)
        self.inc_orientar.add_acao(acao2)
        duration_m = self.incserv.calc_pendencia_mesas(self.inc_orientar, ['MESA-1'])
        self.assertEqual(duration_m, 30)
    
    def test_it_computes_sla_for_an_inc(self):
        with self.assertRaises(AssertionError):
            sla = self.incserv.calcular_prazo(self.inc_orientar, mesa_atual=None)
        with self.assertRaises(AssertionError):
            sla = self.incserv.calcular_prazo(self.inc_orientar, mesa_atual='N4-MESA-FORA-DO-CONTRATO')
        # orientar
        sla = self.incserv.calcular_prazo(self.inc_orientar, mesa_atual='N4-SAP-SUSTENTACAO-SERVICOS')
        self.assertEqual(27*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_orientar, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(9*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_orientar, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=False)
        self.assertEqual(27*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_orientar, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(9*60, sla)
        
        # corrigir
        sla = self.incserv.calcular_prazo(self.inc_corrigir, mesa_atual='N4-SAP-SUSTENTACAO-SERVICOS')
        self.assertEqual(135*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_corrigir, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(9*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_corrigir, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=False)
        self.assertEqual(135*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_corrigir, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(72*60, sla)
        
        # atender - tarefa
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-SERVICOS')
        self.assertEqual(45*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(9*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=False)
        self.assertEqual(45*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(36*60, sla)
        
        # atender - solicitação de serviço
        sla = self.incserv.calcular_prazo(self.inc_sreq, mesa_atual='N4-SAP-SUSTENTACAO-SERVICOS')
        self.assertEqual(45*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_sreq, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(9*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_sreq, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=False)
        self.assertEqual(45*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_sreq, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(36*60, sla)
        
        # atender - tarefa - complexidade simples
        self.inc_tarefa.prazo = IncidentService.SLA_ATENDER_SIMPLES
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-SERVICOS')
        self.assertEqual(IncidentService.SLA_ATENDER_SIMPLES, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(9*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=False)
        self.assertEqual(45*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(36*60, sla)

        # atender - tarefa - complexidade média
        self.inc_tarefa.prazo = IncidentService.SLA_ATENDER_MEDIO
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-SERVICOS')
        self.assertEqual(IncidentService.SLA_ATENDER_MEDIO, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(9*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=False)
        self.assertEqual(90*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(36*60, sla)

        # atender - tarefa - complexidade alta
        self.inc_tarefa.prazo = IncidentService.SLA_ATENDER_COMPLEXO
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-SERVICOS')
        self.assertEqual(IncidentService.SLA_ATENDER_COMPLEXO, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(9*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=False)
        self.assertEqual(180*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(36*60, sla)

        # atender - tarefa - complexidade não padronizada
        self.inc_tarefa.prazo = IncidentService.SLA_ATENDER_COMPLEXO + 1
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-SERVICOS')
        self.assertEqual(IncidentService.SLA_ATENDER_SIMPLES, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(9*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=False)
        self.assertEqual(45*60, sla)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(36*60, sla)