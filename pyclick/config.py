INPUT_DIR               = "INPUT"
INPUT_FILES_GLOB        = "202*.csv"
CONSOLIDATED_DIR        = "CONSOLIDADO"
CONSOLIDATED_GLOB       = "MESA*.xlsx"
CONSOLIDATED_FILE       = "consolidado.xlsx"
PROCESSED_FILE          = "processado.xlsx"
PROCESSED_DB            = "medicao.db"
RESULT_SPREADSHEET      = "medicao.xlsx"
EXIT_FILE_MISMATCH      = 1
EXIT_RENAMED_MISMATCH   = 2
EXIT_TOO_FEW_FILES      = 3

SEPARATOR_HEADER        = "sep="
INPUT_FILENAME_PREFIX   = "Generate_Report_Query_Medicao_"

EXPECTED_COLUMNS = [
    'Data Abertura Chamado', 
    'Data Resolução Chamado', 
    'ID Chamado', 
    'Chamado Pai', 
    'Origem Chamado', 
    'Usuário Afetado', 
    'Nome do Usuário Afetado', 
    'Usuário Informante', 
    'Nome do Usuário Informante', 
    'Organização Cliente', 
    'Departamento Cliente', 
    'Estado', 
    'Site', 
    'FCR', 
    'Status de evento', 
    'Categoria Maior', 
    'Resumo', 
    'Serviço Catálogo', 
    'Classe de Produto de Serviço', 
    'Produto de Serviço', 
    'Item de Serviço', 
    'Categoria', 
    'Oferta Catálogo', 
    'Classe Genérica B', 
    'Classe de Produto B', 
    'Produto B', 
    'Fabricante B', 
    'Item Modelo B', 
    'Item B', 
    'Categoria Causa', 
    'Classe Genérica Causa', 
    'Classe de Produto Causa', 
    'Produto Causa', 
    'Fabricante Causa', 
    'Item Modelo Causa', 
    'Item Causa', 
    'Resolução', 
    'ID Ação', 
    'Data Inicio Ação', 
    'Ultima Ação', 
    'Data Fim Ação', 
    'Tempo Total da Ação (h)', 
    'Tempo Total da Ação (M)', 
    'Ultima Ação Nome', 
    'Motivo Pendencia', 
    'Campos alterados', 
    'Itens alterados', 
    'Nome do CA', 
    'Contrato', 
    'Mesa', 
    'Designado', 
    'Grupo Default', 
    'Prioridade do CA', 
    'Descrição da Prioridade do CA', 
    'Prazo Prioridade ANS (m)', 
    'Prazo Prioridade ANS (h)', 
    'Prazo Prioridade ANO (m)', 
    'Prazo Prioridade ANO (h)', 
    'Prazo Prioridade CA (m)', 
    'Prazo Prioridade CA (h)', 
    'Tempo Total Evento (m)', 
    'Tempo Total Evento (h)', 
    'Tempo Util Evento (m)', 
    'Tempo Util Evento (h)', 
    'Tempo Util Atribuição Mesa (m)', 
    'Tempo Util Atribuição Mesa (h)', 
    'Tempo Util Atribuição CA (m)', 
    'Tempo Util Atribuição CA (h)', 
    'Vinculo', 
    'Vinculo com Incidente Grave?', 
    'Incidente Grave?', 
]
   
COLUMN_MAPPING = {
    'Data Abertura Chamado':            'data_abertura_chamado',
    'Data Resolução Chamado':           'data_resolucao_chamado',
    'ID Chamado':                       'id_chamado',
    'Chamado Pai':                      'chamado_pai',
    'Origem Chamado':                   'origem_chamado',
    'Usuário Afetado':                  'usuario_afetado',
    'Nome do Usuário Afetado':          'nome_do_usuario_afetado',
    'Usuário Informante':               'usuario_informante',
    'Nome do Usuário Informante':       'nome_do_usuario_informante',
    'Organização Cliente':              'organizacao_cliente',
    'Departamento Cliente':             'departamento_cliente',
    'Estado':                           'estado',
    'Site':                             'site',
    'FCR':                              'fcr',
    'Status de evento':                 'status_de_evento',
    'Categoria Maior':                  'categoria_maior',
    'Resumo':                           'resumo',
    'Serviço Catálogo':                 'servico_catalogo',
    'Classe de Produto de Serviço':     'classe_de_produto_de_servico',
    'Produto de Serviço':               'produto_de_servico',
    'Item de Serviço':                  'item_de_servico',
    'Categoria':                        'categoria',
    'Oferta Catálogo':                  'oferta_catalogo',
    'Classe Genérica B':                'classe_generica_b',
    'Classe de Produto B':              'classe_de_produto_b',
    'Produto B':                        'produto_b',
    'Fabricante B':                     'fabricante_b',
    'Item Modelo B':                    'item_modelo_b',
    'Item B':                           'item_b',
    'Categoria Causa':                  'categoria_causa',
    'Classe Genérica Causa':            'classe_generica_causa',
    'Classe de Produto Causa':          'classe_de_produto_causa',
    'Produto Causa':                    'produto_causa',
    'Fabricante Causa':                 'fabricante_causa',
    'Item Modelo Causa':                'item_modelo_causa',
    'Item Causa':                       'item_causa',
    'Resolução':                        'resolucao',
    'ID Ação':                          'id_acao',
    'Data Inicio Ação':                 'data_inicio_acao',
    'Ultima Ação':                      'ultima_acao',
    'Data Fim Ação':                    'data_fim_acao',
    'Tempo Total da Ação (h)':          'tempo_total_da_acao_h',
    'Tempo Total da Ação (M)':          'tempo_total_da_acao_m',
    'Ultima Ação Nome':                 'ultima_acao_nome',
    'Motivo Pendencia':                 'motivo_pendencia',
    'Campos alterados':                 'campos_alterados',
    'Itens alterados':                  'itens_alterados',
    'Nome do CA':                       'nome_do_ca',
    'Contrato':                         'contrato',
    'Mesa':                             'mesa',
    'Designado':                        'designado',
    'Grupo Default':                    'grupo_default',
    'Prioridade do CA':                 'prioridade_do_ca',
    'Descrição da Prioridade do CA':    'descricao_da_prioridade_do_ca',
    'Prazo Prioridade ANS (m)':         'prazo_prioridade_ans_m',
    'Prazo Prioridade ANS (h)':         'prazo_prioridade_ans_h',
    'Prazo Prioridade ANO (m)':         'prazo_prioridade_ano_m',
    'Prazo Prioridade ANO (h)':         'prazo_prioridade_ano_h',
    'Prazo Prioridade CA (m)':          'prazo_prioridade_ca_m',
    'Prazo Prioridade CA (h)':          'prazo_prioridade_ca_h',
    'Tempo Total Evento (m)':           'tempo_total_evento_m',
    'Tempo Total Evento (h)':           'tempo_total_evento_h',
    'Tempo Util Evento (m)':            'tempo_util_evento_m',
    'Tempo Util Evento (h)':            'tempo_util_evento_h',
    'Tempo Util Atribuição Mesa (m)':   'tempo_util_atribuicao_mesa_m',
    'Tempo Util Atribuição Mesa (h)':   'tempo_util_atribuicao_mesa_h',
    'Tempo Util Atribuição CA (m)':     'tempo_util_atribuicao_ca_m',
    'Tempo Util Atribuição CA (h)':     'tempo_util_atribuicao_ca_h',
    'Vinculo':                          'vinculo',
    'Vinculo com Incidente Grave?':     'vinculo_com_incidente_grave',
    'Incidente Grave?':                 'incidente_grave',
}

RENAMED_COLUMNS = list([ COLUMN_MAPPING[ col ] for col in EXPECTED_COLUMNS ])

MESAS_TEMPORIZADAS = set([
    'N4-SAP-SUSTENTACAO-ABAST_GE',
    'N4-SAP-SUSTENTACAO-APOIO_OPERACAO',
    'N4-SAP-SUSTENTACAO-CORPORATIVO',
    'N4-SAP-SUSTENTACAO-ESCALADOS',
    'N4-SAP-SUSTENTACAO-FINANCAS',
    'N4-SAP-SUSTENTACAO-PRIORIDADE',
    'N4-SAP-SUSTENTACAO-SERVICOS',
    'N4-SAP-SUSTENTACAO-GRC',
    'N4-SAP-SUSTENTACAO-PORTAL'
])

MESAS_INVALIDAS = set([
    'A DEFINIR',
    'Atendimento de RH',
    'Mesa Padrão',
    'SVD Manager Template',
    'Usuários Finais',
])

CORRECTION_CATEGORIES = [
    'CORRIGIR-NÃO EMERGENCIAL',
    'CORRIGIR-PESO30',
    'CORRIGIR-PESO35',
    'CORRIGIR-SEVERIDADE1',
    'CORRIGIR-SEVERIDADE2',
    'REPARAR FALHA',
]
