import sys
import os
import os.path
import glob
import argparse
import logging
import datetime as dt
import pandas as pd

import pyclick.util as util

logger = util.get_logger('concat_dedup')

EXPECTED_COLUMNS = [ 
    'data_abertura_chamado',
    'data_resolucao_chamado',
    'id_chamado',
    'chamado_pai',
    'origem_chamado',
    'usuario_afetado',
    'nome_do_usuario_afetado',
    'usuario_informante',
    'nome_do_usuario_informante',
    'organizacao_cliente',
    'departamento_cliente',
    'estado',
    'site',
    'fcr',
    'status_de_evento',
    'categoria_maior',
    'resumo',
    #'descricao_detalhada',
    'servico_catalogo',
    'classe_de_produto_de_servico',
    'produto_de_servico',
    'item_de_servico',
    'categoria',
    'oferta_catalogo',
    'classe_generica_b',
    'classe_de_produto_b',
    'produto_b',
    'fabricante_b',
    'item_modelo_b',
    'item_b',
    'categoria_causa',
    'classe_generica_causa',
    'classe_de_produto_causa',
    'produto_causa',
    'fabricante_causa',
    'item_modelo_causa',
    'item_causa',
    'resolucao',
    'id_acao',
    'data_inicio_acao',
    'ultima_acao',
    'data_fim_acao',
    'tempo_total_da_acao_h',
    'tempo_total_da_acao_m',
    'ultima_acao_nome',
    'motivo_pendencia',
    'campos_alterados',
    'itens_alterados',
    'nome_do_ca',
    'contrato',
    'mesa',
    'designado',
    'grupo_default',
    'prioridade_do_ca',
    'descricao_da_prioridade_do_ca',
    'prazo_prioridade_ans_m',
    'prazo_prioridade_ans_h',
    'prazo_prioridade_ano_m',
    'prazo_prioridade_ano_h',
    'prazo_prioridade_ca_m',
    'prazo_prioridade_ca_h',
    'tempo_total_evento_m',
    'tempo_total_evento_h',
    'tempo_util_evento_m',
    'tempo_util_evento_h',
    'tempo_util_atribuicao_mesa_m',
    'tempo_util_atribuicao_mesa_h',
    'tempo_util_atribuicao_ca_m',
    'tempo_util_atribuicao_ca_h',
    'vinculo',
    'vinculo_com_incidente_grave',
    'incidente_grave'
]

EXIT_FILE_MISMATCH      = 1
EXIT_TOO_FEW_FILES      = 2

class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, output, input_dir, inputs):
        if len(inputs) == 1:
            if input_dir:
                currdir = os.getcwd()
                os.chdir(input_dir)
            inputs = list(sorted(glob.iglob(inputs[0])))
            if input_dir:
                os.chdir(currdir)
        self.output     = output
        self.input_dir  = input_dir
        self.inputs     = inputs
    
    def read_planilha(self, input_file):
        filename = os.path.join(self.input_dir, input_file)
        logger.info('lendo arquivo %s', filename)
        df = pd.read_excel(filename, verbose=False)
        headers = df.columns.to_list()
        if headers != EXPECTED_COLUMNS:
            self.report_file_mismatch(headers, EXPECTED_COLUMNS)
            sys.exit(EXIT_FILE_MISMATCH)
        return df
    
    def save_planilhao(self, df):
        logger.info('salvando planilhão')
        df.to_excel(self.output, index=False)
        
    def run(self):
        try:
            logger.info('concat_dedup - versão %d.%d.%d', *self.VERSION)
            if len(self.inputs) < 2:
                logger.error('especificar ao menos 2 arquivos')
                sys.exit(EXIT_TOO_FEW_FILES)      
            logger.info('iniciando loop de parsing')
            dfs = []
            for input_file in self.inputs:
                logger.info('processsando planilha %s', input_file)
                df = self.read_planilha(input_file)
                dfs.append(df)
            assert len(dfs) > 1
            logger.info('concatenando')
            df = pd.concat(dfs)
            logger.info('removendo linhas duplicadas')
            df.drop_duplicates(keep='last', inplace=True)
            logger.info('salvando resultado')
            self.save_planilhao(df)
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str, help='planilha saida', required=True)
    parser.add_argument('--input_dir', type=str, help='planilha saida', default='.')
    parser.add_argument('input', nargs='+', type=str, help='planilhas a serem consolidadas')
    args = parser.parse_args()
    app = App(args.output, args.input_dir, args.input)
    app.run()