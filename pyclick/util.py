import logging

LOGGER_FORMAT = '%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d\n\t%(message)s\n'
LOGGER_FORMAT = '%(levelname)s - %(filename)s:%(funcName)s:%(lineno)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOGGER_FORMAT)

def get_logger(name):
    return logging.getLogger(name)