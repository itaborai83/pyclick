import os
import os.path
import shutil
import logging
import datetime as dt
import gzip
import shutil
import re
import pandas as pd
import warnings

LOGGER_FORMAT = '%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d\n\t%(message)s\n'
LOGGER_FORMAT = '%(levelname)s - %(filename)s:%(funcName)s:%(lineno)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOGGER_FORMAT)

DATETIME_WITH_MS_REGEX = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d{3}$")

import pyclick.config as config

def get_logger(name):
    return logging.getLogger(name)

def get_null_logger():
    logger = logging.getLogger('<null>')
    logger.addHandler(logging.NullHandler())
    return logger
    
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

def read_expurgos(dir_apuracao):
    path = os.path.join(dir_apuracao, config.EXPURGOS_FILE)
    if not os.path.exists(path):
        return []
    result = []
    with open(path) as fh:
        for line in fh:
            id_chamado = line.strip()
            if line.startswith("#"):
                continue
            elif id_chamado:
                result.append(id_chamado)
        return result
        
def parse_date(txt):
    if pd.isna(txt) or txt is None or txt == "":
        return txt
    return dt.datetime.strptime(txt, '%Y-%m-%d').date()

def parse_time(txt):
    if pd.isna(txt) or txt is None or txt == "":
        return txt
    return dt.datetime.strptime(txt, '%H:%M:%S').time()

def parse_datetime(txt):
    if pd.isna(txt) or txt is None or txt == "":
        return txt
    return dt.datetime.strptime(txt, '%Y-%m-%d %H:%M:%S')

def unparse_date(d):
    if pd.isna(d) or d is None:
        return d
    return d.strftime('%Y-%m-%d')

def unparse_time(d):
    if pd.isna(d) or d is None:
        return d
    return d.strftime('%H:%M:%S')
    
def unparse_datetime(d):
    if pd.isna(d) or d is None:
        return d
    return d.strftime('%Y-%m-%d %H:%M:%S')

def next_n_days(txt, days):
    return str((dt.datetime.strptime(txt, '%Y-%m-%d') + dt.timedelta(days)).date())

def prior_n_days(txt, days):
    return str((dt.datetime.strptime(txt, '%Y-%m-%d') + dt.timedelta(-days)).date())

def next_date(txt):
    return next_n_days(txt, 1)

def prior_date(txt):
    return prior_n_days(txt, 1)

def datetime2tstmp(txt):
    dt1 = parse_datetime(txt)
    return int(dt1.timestamp())

def tstmp2datetime(d):
    return dt.datetime.fromtimestamp(d).strftime('%Y-%m-%d %H:%M:%S')
    
def strip_ms(txt):
    if pd.isna(txt) or txt is None or txt == "":
        return txt
    m = DATETIME_WITH_MS_REGEX.match(txt)
    if not m:
        return txt
    return m[ 1 ]

def _decompress_to(filename, new_filename):
    with gzip.open(filename, 'rb') as f_in:
        with open(new_filename, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def _compress_to(filename, new_filename):
    with open(filename, 'rb') as f_in:
        with gzip.open(new_filename, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            
def decompress_to(filename, new_filename):
    assert filename.endswith(".gz") # file needs to be gzipped
    assert os.path.exists(filename) # file needs to exist
    parts = filename.split(".") # file needs to have a name, an extension and .gzip
    assert len(parts) == 3 
    _, extension = parts[0], parts[1]
    assert new_filename.endswith(extension)
    # actually decompress
    _decompress_to(filename, new_filename)

def compress_to(filename, new_filename):
    assert not filename.endswith(".gz") # file needs to not be gzipped
    assert os.path.exists(filename) # file needs to exist
    parts = filename.split(".") # file needs to have a name and an extension
    assert len(parts) == 2 
    _, extension = parts[0], parts[1]
    assert new_filename.ends_with(extension + ".gz")
    # actually compress
    _compress_to(filename, new_filename)
            
def decompress(filename, keep_original=False):
    assert filename.endswith(".gz") # file needs to be gzipped
    assert os.path.exists(filename) # file needs to exist
    parts = filename.split(".") 
    
    assert len(parts) == 3 # file needs to have a name, an extension and .gzip
    name, extension = parts[0], parts[1]
    decompressed_filename = name + "." + extension
    assert not os.path.exists(decompressed_filename) # the decompressed file must not exist
    # actually decompress
    _decompress_to(filename, decompressed_filename)
    if not keep_original:
        os.unlink(filename)
    return decompressed_filename
    
def compress(filename, keep_original=False):
    assert not filename.endswith(".gz") # file needs to not be gzipped
    assert os.path.exists(filename) # file needs to exist
    parts = filename.split(".") # file needs to have a name and an extension
    assert len(parts) == 2 
    name, extension = parts[0], parts[1]
    compressed_filename = name + "." + extension + ".gz"    
    assert not os.path.exists(compressed_filename) # the compressed file must not exist
    # actually compress
    _compress_to(filename, compressed_filename)
    if not keep_original:
        os.unlink(filename)
    return compressed_filename

def shallow_equality_test(self, other, attrs):
    for attr in attrs:
        if not hasattr(self, attr) or not hasattr(other, attr):
            msg = f"objects {repr(self)} and {repr(other)} compared but one of them lack the attribute {attr}"
            raise ValueError(msg)
        elif getattr(self, attr) != getattr(other, attr):
            return False
    return True

def build_str(self, attrs, indent=True):
    result = []
    result.append("<")
    result.append(type(self).__name__)
    for i,attr in enumerate(attrs):
        value = getattr(self, attr)
        if i > 0:
            if indent:
                txt = f",\n\t{attr}={repr(value)}"
            else:
                txt = f", {attr}={repr(value)}"
        else:
            if indent:
                txt = f"\n\t{attr}={repr(value)}"
            else:
                txt = f",\n\t{attr}={repr(value)}"        
        result.append(txt)
    result.append(">")
    return "".join(result)