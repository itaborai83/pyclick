SELECT	id_chamado
,		chamado_pai
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
,		tipo
,		ultima_mesa
,		peso
,		cast(soma_duracoes_chamado as integer) as soma_duracoes_chamado
,		cast(prazo as integer) as prazo
FROM	REL_MEDICAO_STG AS r 
 
select	ultima_acao_nome
,		ultima_acao 
,		count(*)
from 	rel_medicao_stg rms 
WHERE	ultima_acao = 'y'
group	by 1, 2
order	by 2, 3 desc

select	count(*)
from	(
	select	distinct id_chamado
	from	rel_medicao_stg
	where	ultima_acao_nome in ('Cancelado', 'Cancelar')
	and		ultima_acao = 'n'
	--
	INTERSECT 
	--
	select	distinct id_chamado
	from	rel_medicao_stg
	where	ultima_acao_nome in ('Cancelado', 'Cancelar')
	and		ultima_acao = 'y'
) as t

ORDER 	BY ID_CHAMADO
, 		DATA_INICIO_ACAO
, 		ID_ACAO

 	
pragma table_info('rel_medicao')

with counts as (
	select	id_chamado
	,		count(distinct data_abertura_chamado) 			as data_abertura_chamado
	,		count(distinct data_resolucao_chamado) 			as data_resolucao_chamado
	,		count(distinct id_chamado) 						as id_chamado
	,		count(distinct chamado_pai) 					as chamado_pai
	,		count(distinct origem_chamado) 					as origem_chamado
	,		count(distinct usuario_afetado) 				as usuario_afetado
	,		count(distinct nome_do_usuario_afetado) 		as nome_do_usuario_afetado
	,		count(distinct usuario_informante) 				as usuario_informante
	,		count(distinct nome_do_usuario_informante) 		as nome_do_usuario_informante
	,		count(distinct organizacao_cliente) 			as organizacao_cliente
	,		count(distinct departamento_cliente) 			as departamento_cliente
	,		count(distinct estado) 							as estado
	,		count(distinct site) 							as site
	,		count(distinct fcr) 							as fcr
	,		count(distinct status_de_evento) 				as status_de_evento
	,		count(distinct categoria_maior) 				as categoria_maior
	,		count(distinct resumo) 							as resumo
	,		count(distinct servico_catalogo) 				as servico_catalogo
	,		count(distinct classe_de_produto_de_servico) 	as classe_de_produto_de_servico
	,		count(distinct produto_de_servico) 				as produto_de_servico
	,		count(distinct item_de_servico) 				as item_de_servico
	,		count(distinct categoria) 						as categoria
	,		count(distinct oferta_catalogo) 				as oferta_catalogo
	,		count(distinct classe_generica_b) 				as classe_generica_b
	,		count(distinct classe_de_produto_b) 			as classe_de_produto_b
	,		count(distinct produto_b) 						as produto_b
	,		count(distinct fabricante_b) 					as fabricante_b
	,		count(distinct item_modelo_b) 					as item_modelo_b
	,		count(distinct item_b) 							as item_b
	,		count(distinct categoria_causa) 				as categoria_causa
	,		count(distinct classe_generica_causa) 			as classe_generica_causa
	,		count(distinct classe_de_produto_causa) 		as classe_de_produto_causa
	,		count(distinct produto_causa) 					as produto_causa
	,		count(distinct fabricante_causa) 				as fabricante_causa
	,		count(distinct item_modelo_causa) 				as item_modelo_causa
	,		count(distinct item_causa) 						as item_causa
	,		count(distinct resolucao) 						as resolucao
	,		count(distinct id_acao) 						as id_acao
	,		count(distinct data_inicio_acao) 				as data_inicio_acao
	,		count(distinct ultima_acao) 					as ultima_acao
	,		count(distinct data_fim_acao) 					as data_fim_acao
	,		count(distinct tempo_total_da_acao_m) 			as tempo_total_da_acao_m
	,		count(distinct ultima_acao_nome) 				as ultima_acao_nome
	,		count(distinct motivo_pendencia) 				as motivo_pendencia
	,		count(distinct campos_alterados) 				as campos_alterados
	,		count(distinct itens_alterados) 				as itens_alterados
	,		count(distinct nome_do_ca) 						as nome_do_ca
	,		count(distinct contrato) 						as contrato
	,		count(distinct mesa) 							as mesa
	,		count(distinct designado) 						as designado
	,		count(distinct grupo_default) 					as grupo_default
	,		count(distinct prioridade_do_ca) 				as prioridade_do_ca
	,		count(distinct descricao_da_prioridade_do_ca) 	as descricao_da_prioridade_do_ca
	,		count(distinct prazo_prioridade_ans_m) 			as prazo_prioridade_ans_m
	,		count(distinct prazo_prioridade_ano_m) 			as prazo_prioridade_ano_m
	,		count(distinct prazo_prioridade_ca_m) 			as prazo_prioridade_ca_m
	,		count(distinct tempo_total_evento_m) 			as tempo_total_evento_m
	,		count(distinct tempo_util_evento_m) 			as tempo_util_evento_m
	,		count(distinct tempo_util_atribuicao_mesa_m) 	as tempo_util_atribuicao_mesa_m
	,		count(distinct tempo_util_atribuicao_ca_m) 		as tempo_util_atribuicao_ca_m
	,		count(distinct vinculo) 						as vinculo
	,		count(distinct vinculo_com_incidente_grave) 	as vinculo_com_incidente_grave
	,		count(distinct incidente_grave) 				as incidente_grave
	from	rel_medicao rm 
	group	by id_chamado
)
select	max(data_abertura_chamado) 				as data_abertura_chamado
,		max(data_resolucao_chamado) 			as data_resolucao_chamado
,		max(chamado_pai) 						as chamado_pai
,		max(origem_chamado) 					as origem_chamado
,		max(usuario_afetado) 					as usuario_afetado
,		max(nome_do_usuario_afetado) 			as nome_do_usuario_afetado
,		max(usuario_informante) 				as usuario_informante
,		max(nome_do_usuario_informante) 		as nome_do_usuario_informante
,		max(organizacao_cliente) 				as organizacao_cliente
,		max(departamento_cliente) 				as departamento_cliente
,		max(estado) 							as estado
,		max(site) 								as site
,		max(fcr) 								as fcr
,		max(status_de_evento) 					as status_de_evento
,		max(categoria_maior) 					as categoria_maior
,		max(resumo) 							as resumo
,		max(servico_catalogo) 					as servico_catalogo
,		max(classe_de_produto_de_servico) 		as classe_de_produto_de_servico
,		max(produto_de_servico) 				as produto_de_servico
,		max(item_de_servico) 					as item_de_servico
,		max(categoria) 							as categoria
,		max(oferta_catalogo) 					as oferta_catalogo
,		max(classe_generica_b) 					as classe_generica_b
,		max(classe_de_produto_b) 				as classe_de_produto_b
,		max(produto_b) 							as produto_b
,		max(fabricante_b) 						as fabricante_b
,		max(item_modelo_b) 						as item_modelo_b
,		max(item_b) 							as item_b
,		max(categoria_causa) 					as categoria_causa
,		max(classe_generica_causa) 				as classe_generica_causa
,		max(classe_de_produto_causa) 			as classe_de_produto_causa
,		max(produto_causa) 						as produto_causa
,		max(fabricante_causa) 					as fabricante_causa
,		max(item_modelo_causa) 					as item_modelo_causa
,		max(item_causa) 						as item_causa
,		max(resolucao) 							as resolucao
,		max(id_acao) 							as id_acao
,		max(data_inicio_acao) 					as data_inicio_acao
,		max(ultima_acao) 						as ultima_acao
,		max(data_fim_acao) 						as data_fim_acao
,		max(tempo_total_da_acao_m) 				as tempo_total_da_acao_m
,		max(ultima_acao_nome) 					as ultima_acao_nome
,		max(motivo_pendencia) 					as motivo_pendencia
,		max(campos_alterados) 					as campos_alterados
,		max(itens_alterados) 					as itens_alterados
,		max(nome_do_ca) 						as nome_do_ca
,		max(contrato) 							as contrato
,		max(mesa) 								as mesa
,		max(designado) 							as designado
,		max(grupo_default) 						as grupo_default
,		max(prioridade_do_ca)	 				as prioridade_do_ca
,		max(descricao_da_prioridade_do_ca) 		as descricao_da_prioridade_do_ca
,		max(prazo_prioridade_ans_m) 			as prazo_prioridade_ans_m
,		max(prazo_prioridade_ano_m) 			as prazo_prioridade_ano_m
,		max(prazo_prioridade_ca_m) 				as prazo_prioridade_ca_m
,		max(tempo_total_evento_m) 				as tempo_total_evento_m
,		max(tempo_util_evento_m) 				as tempo_util_evento_m
,		max(tempo_util_atribuicao_mesa_m) 		as tempo_util_atribuicao_mesa_m
,		max(tempo_util_atribuicao_ca_m) 		as tempo_util_atribuicao_ca_m
,		max(vinculo) 							as vinculo
,		max(vinculo_com_incidente_grave) 		as vinculo_com_incidente_grave
,		max(incidente_grave) 					as incidente_grave
from	counts

