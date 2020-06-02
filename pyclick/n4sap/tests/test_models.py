from pyclick.models import *
from pyclick.n4sap.models import *
import unittest

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

