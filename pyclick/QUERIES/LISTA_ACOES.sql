SELECT	data_abertura_chamado
,		data_resolucao_chamado
,		id_chamado
,		chamado_pai
,		origem_chamado
,		usuario_afetado
,		nome_do_usuario_afetado
,		usuario_informante
,		nome_do_usuario_informante
,		organizacao_cliente
,		departamento_cliente
,		estado
,		site
,		fcr
,		status_de_evento
,		categoria_maior
,		resumo
,		servico_catalogo
,		classe_de_produto_de_servico
,		produto_de_servico
,		item_de_servico
,		categoria
,		oferta_catalogo
,		classe_generica_b
,		classe_de_produto_b
,		produto_b
,		fabricante_b
,		item_modelo_b
,		item_b
,		categoria_causa
,		classe_generica_causa
,		classe_de_produto_causa
,		produto_causa
,		fabricante_causa
,		item_modelo_causa
,		item_causa
,		replace(replace(resolucao, CHAR(13), '\r'), CHAR(10), '\n') as resolucao
,		id_acao
,		data_inicio_acao
,		ultima_acao
,		data_fim_acao
,		cast(tempo_total_da_acao_m as integer) as tempo_total_da_acao_m 
,		ultima_acao_nome
,		replace(replace(motivo_pendencia, CHAR(13), '\r'), CHAR(10), '\n') as motivo_pendencia
,		replace(replace(campos_alterados, CHAR(13), '\r'), CHAR(10), '\n') as campos_alterados 
,		replace(replace(itens_alterados, CHAR(13), '\r'), CHAR(10), '\n') as itens_alterados
,		nome_do_ca
,		contrato
,		mesa
,		designado
,		grupo_default
,		prioridade_do_ca
,		descricao_da_prioridade_do_ca
,		cast(prazo_prioridade_ans_m as integer) as prazo_prioridade_ans_m 
,		cast(prazo_prioridade_ano_m as integer) as prazo_prioridade_ano_m 
,		cast(prazo_prioridade_ca_m as integer) as prazo_prioridade_ca_m 
,		cast(tempo_total_evento_m as integer) as tempo_total_evento_m 
,		cast(tempo_util_evento_m as integer) as tempo_util_evento_m 
,		cast(tempo_util_atribuicao_mesa_m as integer) as tempo_util_atribuicao_mesa_m 
,		cast(tempo_util_atribuicao_ca_m as integer) as tempo_util_atribuicao_ca_m
,		vinculo
,		vinculo_com_incidente_grave
,		incidente_grave
,		tipo
,		ultima_mesa
,		peso
,		cast(soma_duracoes_chamado as integer) as soma_duracoes_chamado
,		cast(prazo as integer) as prazo
from	rel_medicao_stg 
order 	by id_chamado
, 		data_inicio_acao
, 		id_acao