# -*- coding: utf8 -*-
# please set the environment variable PYTHONUTF8=1
import sys
import os
import os.path
import glob
import shutil
import argparse
import logging
import datetime as dt
import pandas as pd
import sqlite3

import pyclick.util as util
import pyclick.config as config

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('gzip')

class App(object):
    
    VERSION = (1, 0, 0)
    
    def __init__(self, filename):
        self.filename = filename
    
    def run(self):
        try:
            logger.info('gzip - version %d.%d.%d', *self.VERSION)
            util.compress(self.filename)
        except:
            logger.exception('an error has occurred')
            sys.exit(1)
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='file to be compressed')
    args = parser.parse_args()
    app = App(args.filename)
    app.run()