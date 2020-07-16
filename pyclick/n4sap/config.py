OVERRIDE_SPREADSHEET = "override.xlsx"
KPI_SPREADSHEET = "indicadores.xlsx"
OVERRIDE_COLUMNS = [ 'ID_CHAMADO', 'STATUS', 'CATEGORIA', 'MESA', 'PESO', 'PRAZO', 'DURACAO', 'ESTORNO', 'OBS_OVERRIDE' ]

MESAS = [
    'N4-SAP-SUSTENTACAO-ABAST_GE', 
    'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 
    'N4-SAP-SUSTENTACAO-CORPORATIVO', 
    'N4-SAP-SUSTENTACAO-FINANCAS', 
    'N4-SAP-SUSTENTACAO-GRC', 
    'N4-SAP-SUSTENTACAO-PORTAL', 
    'N4-SAP-SUSTENTACAO-SERVICOS', 
    'N4-SAP-SUSTENTACAO-ESCALADOS', 
    'N4-SAP-SUSTENTACAO-PRIORIDADE'
]

MESAS_NAO_PRIORITARIAS = [
    'N4-SAP-SUSTENTACAO-ABAST_GE', 
    'N4-SAP-SUSTENTACAO-APOIO_OPERACAO', 
    'N4-SAP-SUSTENTACAO-CORPORATIVO', 
    'N4-SAP-SUSTENTACAO-FINANCAS', 
    'N4-SAP-SUSTENTACAO-GRC', 
    'N4-SAP-SUSTENTACAO-PORTAL', 
    'N4-SAP-SUSTENTACAO-SERVICOS'
]


SLA_KPIS = {
    'PRP': 10.0,
    'PRS': 10.0,
    'PRC': 25.0,
    'PRO': 15.0,
    'PRE': 10.0,
    'IDS': 170.0
}

START_CSAT_DT = '2020-01-31'