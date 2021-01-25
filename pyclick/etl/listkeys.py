import os
import argparse
import logging
import pyclick.util as util
import pyclick.etl.load_repo as repo

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('listkeys')

class App():
    
    VERSION = (0, 0, 0)
    
    def __init__(self, env, dbname, intkey):
        self.env    = env
        self.dbname = dbname
        self.intkey = intkey
    
    def run(self):
        logger.info('starting key lister - version %d.%d.%d', *self.VERSION)
        r = repo.LoadRepo(self.env)
        for key in r.list_keys(self.dbname, self.intkey):
            print(key)
        logger.info('finished')

            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--intkey', action='store_true', default=False, help='parse keys as integers')
    parser.add_argument('env', type=str, help='environment')
    parser.add_argument('--dbname', type=str, default=None, help='db name')
    args = parser.parse_args()
    app = App(args.env, args.dbname, args.intkey)
    app.run()