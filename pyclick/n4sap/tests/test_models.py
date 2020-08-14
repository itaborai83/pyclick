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

    def test_it_overrides_offering(self):
        self.assertEqual(self.inc_tarefa.oferta, 'HR / PY - Realização de Memória de Cálculo')
        self.assertEqual(self.inc_tarefa.prazo, 2700)
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-CORPORATIVO')
        self.assertEqual(sla, 45*60)
        
        # oferring override with standard SLA
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA', 180*60)
        self.incserv.set_override_oferta(self.inc_tarefa.id_chamado, 'TESTE OVERRIDE OFERTA')
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-CORPORATIVO')
        self.assertEqual(sla, 180*60)

        # oferring override with non standard SLA
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA II', 180*60 + 1) # non standard sla 
        self.incserv.set_override_oferta(self.inc_tarefa.id_chamado, 'TESTE OVERRIDE OFERTA II')
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-CORPORATIVO')
        self.assertEqual(sla, 45*60)

        # oferring override with standard SLA as PESO 35
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA III', 180*60)
        self.incserv.set_override_oferta(self.inc_tarefa.id_chamado, 'TESTE OVERRIDE OFERTA III')
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(sla, 9*60)

        # oferring override with non standard SLA as PESO 35
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA IV', 180*60+1)
        self.incserv.set_override_oferta(self.inc_tarefa.id_chamado, 'TESTE OVERRIDE OFERTA IV')
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(sla, 9*60)

        # oferring override with standard SLA as PESO 30
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA V', 180*60)
        self.incserv.set_override_oferta(self.inc_tarefa.id_chamado, 'TESTE OVERRIDE OFERTA V')
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(sla, 36*60)

        # oferring override with non standard SLA as PESO 30
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA VI', 180*60+1)
        self.incserv.set_override_oferta(self.inc_tarefa.id_chamado, 'TESTE OVERRIDE OFERTA VI')
        sla = self.incserv.calcular_prazo(self.inc_tarefa, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(sla, 36*60)
        
        # incident remains unchanged despite the overrides
        self.assertEqual(self.inc_tarefa.oferta, 'HR / PY - Realização de Memória de Cálculo')
        self.assertEqual(self.inc_tarefa.prazo, 2700)

    def test_it_overrides_offering_and_categorie(self):
        self.assertEqual(self.inc_corrigir.oferta, 'Suporte ao serviço de SAP')
        self.assertEqual(self.inc_corrigir.prazo, 540)
        sla = self.incserv.calcular_prazo(self.inc_corrigir, mesa_atual='N4-SAP-SUSTENTACAO-CORPORATIVO')
        self.assertEqual(sla, 135*60)
        
        self.incserv.set_override_categoria(self.inc_corrigir.id_chamado, 'ATENDER - TAREFA')
        
        # oferring override with standard SLA
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA', 180*60)
        self.incserv.set_override_oferta(self.inc_corrigir.id_chamado, 'TESTE OVERRIDE OFERTA')
        sla = self.incserv.calcular_prazo(self.inc_corrigir, mesa_atual='N4-SAP-SUSTENTACAO-CORPORATIVO')
        self.assertEqual(sla, 180*60)

        # oferring override with non standard SLA
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA II', 180*60 + 1) # non standard sla 
        self.incserv.set_override_oferta(self.inc_corrigir.id_chamado, 'TESTE OVERRIDE OFERTA II')
        sla = self.incserv.calcular_prazo(self.inc_corrigir, mesa_atual='N4-SAP-SUSTENTACAO-CORPORATIVO')
        self.assertEqual(sla, 45*60)

        # oferring override with standard SLA as PESO 35
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA III', 180*60)
        self.incserv.set_override_oferta(self.inc_corrigir.id_chamado, 'TESTE OVERRIDE OFERTA III')
        sla = self.incserv.calcular_prazo(self.inc_corrigir, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(sla, 9*60)

        # oferring override with non standard SLA as PESO 35
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA IV', 180*60+1)
        self.incserv.set_override_oferta(self.inc_corrigir.id_chamado, 'TESTE OVERRIDE OFERTA IV')
        sla = self.incserv.calcular_prazo(self.inc_corrigir, mesa_atual='N4-SAP-SUSTENTACAO-PRIORIDADE')
        self.assertEqual(sla, 9*60)

        # oferring override with standard SLA as PESO 30
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA V', 180*60)
        self.incserv.set_override_oferta(self.inc_corrigir.id_chamado, 'TESTE OVERRIDE OFERTA V')
        sla = self.incserv.calcular_prazo(self.inc_corrigir, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(sla, 36*60)

        # oferring override with non standard SLA as PESO 30
        self.incserv.add_oferta_catalogo('TESTE OVERRIDE OFERTA VI', 180*60+1)
        self.incserv.set_override_oferta(self.inc_corrigir.id_chamado, 'TESTE OVERRIDE OFERTA VI')
        sla = self.incserv.calcular_prazo(self.inc_corrigir, mesa_atual='N4-SAP-SUSTENTACAO-ESCALADOS', enable_peso30=True)
        self.assertEqual(sla, 36*60)
        
        # incident remains unchanged despite the overrides
        self.assertEqual(self.inc_corrigir.oferta, 'Suporte ao serviço de SAP')
        self.assertEqual(self.inc_corrigir.prazo, 540)
        
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
    
    def test_it_returns_a_data_frame_of_purged_incidents(self):
        self.incserv.add_expurgo('123')
        self.incserv.add_expurgo('234')
        self.incserv.add_expurgo('345')
        expurgos_df = self.incserv.get_expurgos()
        expected = { 'id_chamado': [ '123', '234', '345' ]}
        self.assertEqual(expurgos_df.to_dict(orient="list"), expected)

    def test_it_returns_a_data_frame_of_overriden_categories(self):
        self.incserv.set_override_categoria('123', 'ORIENTAR')
        self.incserv.set_override_categoria('234', 'CORRIGIR')
        self.incserv.set_override_categoria('345', 'ATENDER - TAREFA')
        self.incserv.set_override_categoria('456', 'ATENDER')
        categorias_df = self.incserv.get_overrides_categoria()
        expected = { 
            'id_chamado' : [ '123', '234', '345', '456' ],
            'categoria'  : [ 'ORIENTAR', 'CORRIGIR', 'ATENDER - TAREFA', 'ATENDER']
        }
        self.assertEqual(categorias_df.to_dict(orient="list"), expected)
    
    def test_it_returns_a_data_frame_of_overriden_offerings(self):
        self.incserv.set_override_oferta('123', 'OFERTA I')
        self.incserv.set_override_oferta('234', 'OFERTA II')
        self.incserv.set_override_oferta('345', 'OFERTA III')
        self.incserv.set_override_oferta('456', 'OFERTA IV')
        ofertas_df = self.incserv.get_overrides_oferta()
        expected = { 
            'id_chamado' : [ '123', '234', '345', '456' ],
            'oferta'     : [ 'OFERTA I', 'OFERTA II', 'OFERTA III', 'OFERTA IV']
        }
        self.assertEqual(ofertas_df.to_dict(orient="list"), expected)