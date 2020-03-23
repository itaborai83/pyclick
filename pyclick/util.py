import logging

LOGGER_FORMAT = '%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d\n\t%(message)s\n'
LOGGER_FORMAT = '%(levelname)s - %(filename)s:%(funcName)s:%(lineno)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOGGER_FORMAT)

def get_logger(name):
    return logging.getLogger(name)
    
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
