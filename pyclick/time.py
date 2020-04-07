import bisect
import datetime as dt
import unittest

class Event(object):
    
    def __init__(self, when):
        self.when = when
    
    def process(self, state):
        raise NotImplemetedError
        
class StartClock(Event):
    pass

class StopClock(Event):
    pass

class DayStart(Event):
    pass

class DayEnd(Event):
    pass

class SetWorkHours(Event):
    pass

class TimeRunner(object):
    
    def __init__(self):
        self.clocks = {}


class WorkDay(BaseDay):

    FIRST_SECOND    = dt.time(0, 0, 0)
    LAST_SECOND     = dt.time(23, 59, 59)
    SECONDS_IN_DAY  = 24 * 60 * 60
        
    def __init__(self, dow, start_time, end_time):
        # Monday == 0 ... Sunday == 6
        assert 0 <= dow <= 6
        assert start_time <= end_time
        self.dow        = dow
        self.start_time = start_time
        self.end_time   = end_time
    
    def calc_tick(self, when):
        assert when.weekday() == seld.dow
        date = when.date()
        t = when.time()
        dt_first = dt.datetime.combine(date, self.FIRST_SECOND)
        dt_start = dt.datetime.combine(date, self.start_time)
        dt_end   = dt.datetime.combine(date, self.end_time)
        dt_last  = dt.datetime.combine(date, self.LAST_SECOND)
        if when < dt_start:
            duration    = dt.timedelta(0) # non working hours
            next_tick   = dt_start
            next_day    = False
        elif self.start_time <= t < self.end_time:
            duration    = when - self.dt_start
            next_tick   = dt_end
            next_day    = False
        elif t == self.end_time:
            duration    = dt.timedelta(0)
            next_tick   = dt_start
            next_day    = False
        elif t > self.end_time:
            duration    = dt.timedelta(0) # non working hours
            next_tick   = dt_start
            next_day    = False
        else:
            assert 1 == 2
        return duration, next_tick, next_day
        
class Schedule(object):
    
    def __init__(self):
        self.work_days = []
        self.hollydays = set()
        
    @classmethod
    def _get_work_day(klass, dow, start_time, end_time):
        return WorkDay(dow, start_time, end_time)
    
    @classmethod
    def build(klass, start_time, end_time, skip_weekend=True):
        ww = klass()
        ww.set_workday(0, start_time, end_time)
        ww.set_workday(1, start_time, end_time)
        ww.set_workday(2, start_time, end_time)
        ww.set_workday(3, start_time, end_time)
        ww.set_workday(4, start_time, end_time)
        if skip_weekend:
            ww.set_workday(5, start_time, end_time)
            ww.set_workday(6, start_time, end_time)
        else:
            ww.set_workday(5, dt.time(23, 59, 59))
            ww.set_workday(6, dt.time(23, 59, 59))
        return ww
        
    def set_workday(self, dow, start_time, end_time):
        self.work_days[ dow ] = self._get_work_day(dow, start_time, end_time)
    
    def iterdates(self, start, end):
        pass 
        
    def add_hollyday(self, hd):
        self.hollydays.add(hd)

class TestWorkDay(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_it_returns_the_next_working_hour_for_week_day(self):
        wd = WorkDay(0, dt.time(8), dt.time(17, 59, 59))
        
        
if __name__ == '__main__':
    unittest.main()