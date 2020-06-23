import os
import os.path
import time
import argparse
import subprocess
import logging
import pyclick.util as util

assert os.environ[ 'PYTHONUTF8' ] == "1"

logger = util.get_logger('dump_multi_days')

class DelayedExecution():
    
    MAX_RETRIES = 3
    
    def __init__(self, dir_staging, date, compress):
        self.dir_staging = dir_staging
        self.date = date
        self.compress = compress
        self.popen = None
        self.waiting = True
        self.running = False
        self.finished = False
        self.aborted = False
        self.retries = 0
        
    def start(self):
        assert self.popen is None
        assert self.waiting == True
        assert self.running == False
        assert self.finished == False
        assert self.aborted == False
        logger.info(f'starting process for dumping date {self.date}')
        stdout_file = os.path.join(self.dir_staging, self.date + ".out")
        stdout = open(stdout_file, "w")
        if self.compress:
            cmd = f"python -m pyclick.assyst.dump_daily --compress {self.dir_staging} {self.date}"
        else:
            cmd = f"python -m pyclick.assyst.dump_daily {self.dir_staging} {self.date}"
        self.popen = subprocess.Popen(
            args = cmd,
            stdout = stdout,
            stderr = subprocess.STDOUT,
            stdin = subprocess.DEVNULL,
            shell = True,
            cwd = os.getcwd(),
            env = os.environ
        )
        self.waiting = False
        self.running = True
    
    def poll(self):
        assert self.popen is not None
        assert self.waiting == False
        assert self.running == True
        assert self.finished == False
        assert self.aborted == False
        self.popen.poll()
        if self.popen.returncode is None:
            return "RUNNING"
        elif self.popen.returncode == 0:
            # success
            self.popen = None
            self.running = False
            self.finished = True
            self.aborted = False
            logger.info(f'process for dumping date {self.date} finished')
            return "FINISHED"
        elif self.popen.returncode != 0: # negative when killed by posix signals
            # aborted
            self.popen = None
            self.running = False
            self.aborted = True
            logger.info(f'process for dumping date {self.date} aborted')
            if self.retries > self.MAX_RETRIES:
                logger.info(f'cannot retry date {self.date} any longer')
                return "ABORTED"
            else:
                self.retry()
                return "RUNNING"
        else:
            assert 1 == 2
    
    def kill(self):
        if self.popen is None:
            return
        self.popen.poll()
        if self.popen.returncode != None:
            return
        self.popen.kill()
    def retry(self):
        assert self.popen is None
        assert self.waiting == False
        assert self.running == False
        assert self.finished == False
        assert self.aborted == True
        logger.info(f'retrying process for dumping date {self.date}')
        stdout_file = os.path.join(self.dir_staging, self.date + ".out")
        stdout = open(stdout_file, "a") # open for appending
        if self.compress:
            cmd = f"python -m pyclick.assyst.dump_daily --compress {self.dir_staging} {self.date}"
        else:
            cmd = f"python -m pyclick.assyst.dump_daily {self.dir_staging} {self.date}"
        self.popen = subprocess.Popen(
            args = cmd,
            stdout = stdout,
            stderr = subprocess.STDOUT,
            stdin = subprocess.DEVNULL,
            shell = False,
            cwd = os.getcwd(),
            env = os.environ
        )
        self.waiting = False
        self.running = True
        self.aborted = False
        self.retries += 1
    
class App(object):
    
    VERSION = (0, 0, 0)
    
    def __init__(self, dir_staging, begin_date, end_date, compress, parallel):
        self.dir_staging    = dir_staging
        self.begin_date     = begin_date
        self.end_date       = end_date
        self.compress       = compress
        self.parallel       = parallel
    
    def get_dates(self):
        logger.info('listing dates')
        assert self.begin_date <= self.end_date
        result = []
        date = self.begin_date
        while date <= self.end_date:
            result.append(date)
            date = util.next_date(date)
        return result
    
    def build_slaves(self, dates):
        logger.info('building slaves processes')
        result = []
        for date in dates:
            slave = DelayedExecution(self.dir_staging, date, self.compress)
            result.append(slave)
        return result
    
    def run_loop(self, slaves):
        waiting = slaves[ : ]
        running = [ ]
        finished = [ ]
        aborted = [ ]
        quota = self.parallel
        try:
            while True:
                # invariant to safeguard resources
                assert len(running) <= quota
                
                # poll loop
                running_copy = running[:]
                for slave in running_copy:
                    assert slave not in waiting
                    assert slave not in aborted
                    assert slave not in finished                
                    status = slave.poll()
                    if status == 'RUNNING':
                        continue
                    elif status == 'FINISHED':
                        running.remove(slave)
                        finished.append(slave)
                    elif status == 'ABORTED':
                        running.remove(slave)
                        aborted.append(slave)
                        
                # start loop
                waiters = len(waiting)
                if waiters > 0:
                    budget = quota - len(running)
                    if budget > waiters:
                        budget = waiters
                    waiting_copy = waiting[:]
                    for idx in range(budget):
                        slave = waiting_copy[ idx ]
                        assert slave not in running
                        assert slave not in aborted
                        assert slave not in finished
                        slave.start()
                        waiting.remove(slave)
                        running.append(slave)
                
                if len(running) == 0 and len(waiting) == 0:
                    break
                time.sleep(1)
        finally:
            if len(running) > 0:
                for slave in running:
                    slave.kill()
    def run(self):
        try:
            logger.info('starting multi days dumper - version %d.%d.%d', *self.VERSION)
            dates = self.get_dates()
            slaves = self.build_slaves(dates)
            self.run_loop(slaves)
            logger.info('finished')
        except:
            logger.exception('an error has occurred')
            raise
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--compress', action='store_true', help='comprimir arquivo de saída' )
    parser.add_argument('-p', '--parallel', type=int, default=4, help='nível de paralelismo' )
    parser.add_argument('dir_staging', type=str, help='diretório de staging')
    parser.add_argument('begin_date', type=str, help='data primeiro planilhão')
    parser.add_argument('end_date', type=str, help='data último planilhão')
    args = parser.parse_args()
    app = App(args.dir_staging, args.begin_date, args.end_date, args.compress, args.parallel)
    app.run()
    