import os
import os.path
import shutil
import logging
import datetime as dt

LOGGER_FORMAT = '%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d\n\t%(message)s\n'
LOGGER_FORMAT = '%(levelname)s - %(filename)s:%(funcName)s:%(lineno)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOGGER_FORMAT)

import pyclick.config as config

def get_logger(name):
    return logging.getLogger(name)
    
def get_processed_file(dir_apuracao):
    return os.path.join(dir_apuracao, config.PROCESSED_FILE)

def get_processed_db(dir_apuracao):
    return os.path.join(dir_apuracao, config.PROCESSED_DB)

def get_query(query_name):
    assert '.' not in query_name and '/' not in query_name and '\\' not in query_name
    path = os.path.join('./pyclick/QUERIES', query_name + '.sql')
    return open(path).read()

def get_result_spreadsheet(dir_apuracao):
    return os.path.join(dir_apuracao, config.RESULT_SPREADSHEET)
    
def report_file_mismatch(logger, headers, expected_columns):
    set_expected    = set(expected_columns)
    set_actual      = set(headers)
    set_missing     = set_expected.difference(set_actual)
    set_unexpected  = set_actual.difference(set_expected)
    missing_cols    = list([ col for col in expected_columns if col in set_missing ])
    unexpected_cols = list([ col for col in headers if col in set_unexpected ])
    logger.error('the input file does not match the expected format')
    logger.error('missing columns >> %s', str(missing_cols))
    logger.error('unexpected_cols columns >> %s', str(unexpected_cols))
    for i, (c1, c2) in enumerate(zip(expected_columns, headers)):
        i += 1
        if c1 != c2:
            logger.error('column on position %d is the first mismatch >> %s != %s', i, repr(c1), repr(c2))
            break

def sort_rel_medicao(df):
    df.sort_values(by=[ "id_chamado", "chamado_pai", "data_inicio_acao", "id_acao", "status_de_evento" ], inplace=True, kind="mergesort", ignore_index=True)

def read_mesas(dir_apuracao):
    path = os.path.join(dir_apuracao, config.MESAS_FILE)
    result = []
    with open(path) as fh:
        for line in fh:
            mesa = line.strip()
            if mesa.startswith("#"):
                continue
            elif mesa:
                result.append(mesa)
        return result

def next_date(d):
    return str((dt.datetime.strptime(d, '%Y-%m-%d') + dt.timedelta(1)).date())
