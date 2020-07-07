import math
import pandas as pd
import pyclick.n4sap.models as models        

class Ids(models.N4SapKpi):
    
    KPI_NAME    = "IDS"
    SLA         = 170.0
    
    def __init__(self):
        super().__init__()
        self.reset()
        
    def reset(self):
        self.numerator = 0
        self.denominator = 0
        self.details = {
            'fator_ids'         : [],
            'id_chamado'        : [],
            'chamado_pai'       : [],
            'categoria'         : [],
            'prazo'             : [],
            'duracao'           : [],
            'ultima_mesa'       : [],
            'ultimo_status'     : [],
            'atribuicao'        : [],
            'mesa'              : [],
            'entrada'           : [],
            'status_entrada'    : [],
            'saida'             : [],
            'status_saida'      : [],
            'duracao_m'         : [],
            'pendencia_m'       : [],
        }
            
    def update_details(self, inc, duration_m, ids_factor):
        categoria = self.categorizar(inc)
        prazo = self.calcular_prazo(inc)
        for atrib in inc.atribuicoes:
            if atrib.mesa not in self.MESAS_CONTRATO:
                continue
            self.details[ 'fator_ids'      ].append(ids_factor)
            self.details[ 'id_chamado'     ].append(inc.id_chamado)
            self.details[ 'chamado_pai'    ].append(inc.chamado_pai)
            self.details[ 'categoria'      ].append(categoria)
            self.details[ 'prazo'          ].append(prazo)
            self.details[ 'duracao'        ].append(duration_m)
            self.details[ 'ultima_mesa'    ].append(inc.mesa_atual)
            self.details[ 'ultimo_status'  ].append(inc.status)
            self.details[ 'atribuicao'     ].append(atrib.seq)
            self.details[ 'mesa'           ].append(atrib.mesa)
            self.details[ 'entrada'        ].append(atrib.entrada)
            self.details[ 'status_entrada' ].append(atrib.status_entrada)
            self.details[ 'saida'          ].append(atrib.saida)
            self.details[ 'status_saida'   ].append(atrib.status_saida)
            if inc.id_chamado.startswith('S'):
                self.details[ 'duracao_m'      ].append(None)
                self.details[ 'pendencia_m'    ].append(None)
            else:
                self.details[ 'duracao_m'      ].append(atrib.duracao_m)
                self.details[ 'pendencia_m'    ].append(atrib.pendencia_m)
            
    def get_details(self):
        return pd.DataFrame(self.details)
    
    def get_description(self):
        if self.denominator == 0:
            msg = "Nenhum incidente aberto violando SLA"
        else:
            msg = f"{self.numerator} ids / {self.denominator} incidentes"
        return msg

    def has_assignment_within_period(self, inc, start_dt, end_dt):
        for atrib in inc.get_atribuicoes_mesas(self.MESAS_NAO_PRIORITARIAS):
            if atrib.intersects_with(start_dt, end_dt):
                return True
        return False
        
    def evaluate(self, click, start_dt, end_dt, mesa=None):
        mesa_mapping = self.build_mesa_mapping(mesa) if mesa is not None else {}
        for mesa_name in self.MESAS_CONTRATO:
            mesa = click.get_mesa(mesa_name)
            if mesa is None:
                continue
            for inc in mesa.get_incidentes():
                inc = inc.remap_mesas(mesa_mapping)
                if inc.id_chamado.startswith("T"):
                    continue
                if not self.has_assignment_within_period(inc, start_dt, end_dt):
                    continue
                assert inc.status == 'ABERTO'
                categoria = self.categorizar(inc)
                prazo_m = self.calcular_prazo(inc)
                duration_m = click.calc_duration_mesas(inc.id_chamado, self.MESAS_CONTRATO)
                try:
                    if duration_m < prazo_m:
                        continue
                except TypeError:
                    # TODO: add test case
                    self.logger.error(
                        "invalid duration -> %s or SLA -> %s for inc %s", 
                        str(duration_m), str(inc.prazo), inc.id_chamado
                    )
                    self.logger.warn("skipping incident %s", inc.id_chamado)
                    continue
                ids = math.ceil(duration_m / (180.0 * 60))
                self.numerator   += ids
                self.denominator += 1
                self.update_details(inc, duration_m, ids)
                if inc.id_chamado in click.children_of:
                    for child_id in click.children_of[ inc.id_chamado ]:
                        child = click.get_incidente(child_id)
                        self.update_details(child, duration_m, None)

    def get_result(self):
        msg = self.get_description()
        if self.denominator == 0:
            return None, msg
        else:
            result = 100.0 * (self.numerator / self.denominator)
            return result, msg
            
class IdsV2(Ids):
    
    def __init__(self):
        super().__init__()
            
    def update_details(self, inc, duration_m, ids_factor):
        assert not inc.id_chamado.startswith('S')
        super().update_details(inc, duration_m, ids_factor)      
                
    def evaluate(self, click, start_dt, end_dt, mesa_filter=None):
        for mesa_name in self.MESAS_CONTRATO:
            mesa = click.get_mesa(mesa_name)
            if mesa is None:
                continue
            for inc in mesa.get_incidentes():
                inc = self.remap_mesas_by_last(inc, mesa_filter, self.MESAS_CONTRATO)
                if inc is None:
                    continue
                if inc.id_chamado.startswith("S"):
                    continue
                if not self.has_assignment_within_period(inc, start_dt, end_dt):
                    continue
                assert inc.status == 'ABERTO'
                categoria = self.categorizar(inc)
                prazo_m = self.calcular_prazo(inc)
                duration_m = click.calc_duration_mesas(inc.id_chamado, self.MESAS_CONTRATO)
                try:
                    if duration_m < prazo_m:
                        continue
                except TypeError:
                    # TODO: add test case
                    self.logger.error(
                        "invalid duration -> %s or SLA -> %s for inc %s", 
                        str(duration_m), str(inc.prazo), inc.id_chamado
                    )
                    self.logger.warn("skipping incident %s", inc.id_chamado)
                    continue
                ids = math.ceil(duration_m / (180.0 * 60))
                self.numerator   += ids
                self.denominator += 1
                self.update_details(inc, duration_m, ids)
                if inc.id_chamado in click.children_of:
                    for child_id in click.children_of[ inc.id_chamado ]:
                        child = click.get_incidente(child_id)
                        self.update_details(child, duration_m, None)

    def get_result(self):
        msg = self.get_description()
        if self.denominator == 0:
            return None, msg
        else:
            result = 100.0 * (self.numerator / self.denominator)
            return result, msg