DROP TABLE IF EXISTS "rel_medicao";
CREATE TABLE "rel_medicao" (
	"data_abertura_chamado" 			TEXT
,	"data_resolucao_chamado" 			TEXT
,	"id_chamado" 						TEXT
,	"chamado_pai" 						TEXT
,	"origem_chamado" 					TEXT
,	"usuario_afetado" 					TEXT
,	"nome_do_usuario_afetado" 			TEXT
,	"usuario_informante" 				TEXT
,	"nome_do_usuario_informante" 		TEXT
,	"organizacao_cliente" 				TEXT
,	"departamento_cliente" 				TEXT
,	"estado" 							TEXT
,	"site" 								TEXT
,	"fcr" 								TEXT
,	"status_de_evento" 					TEXT
,	"categoria_maior" 					TEXT
,	"resumo" 							TEXT
,	"servico_catalogo" 					TEXT
,	"classe_de_produto_de_servico" 		TEXT
,	"produto_de_servico" 				TEXT
,	"item_de_servico" 					TEXT
,	"categoria" 						TEXT
,	"oferta_catalogo" 					TEXT
,	"prazo_oferta_m" 					TEXT -- nao existe na base de dados de IMPORT
,	"classe_generica_b" 				TEXT
,	"classe_de_produto_b" 				TEXT
,	"produto_b" 						TEXT
,	"fabricante_b" 						TEXT
,	"item_modelo_b" 					TEXT
,	"item_b" 							TEXT
,	"categoria_causa" 					TEXT
,	"classe_generica_causa" 			TEXT
,	"classe_de_produto_causa" 			TEXT
,	"produto_causa" 					TEXT
,	"fabricante_causa" 					TEXT
,	"item_modelo_causa" 				TEXT
,	"item_causa" 						TEXT
,	"resolucao" 						TEXT
,	"id_acao" 							INTEGER
,	"data_inicio_acao" 					TEXT
,	"ultima_acao" 						TEXT
,	"data_fim_acao" 					TEXT
,	"duracao_m"							INTEGER  -- não existe na base de dados de IMPORT
,	"tempo_total_da_acao_h" 			TEXT
,	"tempo_total_da_acao_m" 			REAL
,	"ultima_acao_nome" 					TEXT
,	"user_status"						TEXT -- não existe na base de dados de IMPORT
,	"pendencia"							TEXT -- não existe na base de dados de IMPORT
,	"motivo_pendencia" 					TEXT
,	"campos_alterados" 					TEXT
,	"itens_alterados" 					TEXT
,	"nome_do_ca" 						TEXT
,	"contrato" 							TEXT
,	"mesa" 								TEXT
,	"mesa_atual" 						TEXT -- nao existe na base de dados de IMPORT
,	"designado" 						TEXT
,	"grupo_default" 					TEXT
,	"prioridade_do_ca" 					TEXT
,	"descricao_da_prioridade_do_ca" 	TEXT
,	"prazo_prioridade_ans_m" 			INTEGER
,	"prazo_prioridade_ans_h" 			TEXT
,	"prazo_prioridade_ano_m" 			REAL
,	"prazo_prioridade_ano_h" 			TEXT
,	"prazo_prioridade_ca_m" 			REAL
,	"prazo_prioridade_ca_h" 			TEXT
,	"tempo_total_evento_m" 				REAL
,	"tempo_total_evento_h" 				TEXT
,	"tempo_util_evento_m" 				INTEGER
,	"tempo_util_evento_h" 				TEXT
,	"tempo_util_atribuicao_mesa_m" 		REAL
,	"tempo_util_atribuicao_mesa_h" 		TEXT
,	"tempo_util_atribuicao_ca_m" 		REAL
,	"tempo_util_atribuicao_ca_h" 		TEXT
,	"vinculo" 							TEXT
,	"vinculo_com_incidente_grave" 		TEXT
,	"incidente_grave" 					TEXT
,	primary key("id_chamado", "id_acao")
);
