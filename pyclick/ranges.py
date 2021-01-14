import math
import bisect
import unittest
import datetime as dt
import pandas as pd

from pyclick.util import parse_datetime, parse_date, parse_time, datetime2tstmp, unparse_datetime

PRINT_TRANSITIONS = False

class WorkDay(object):
    
    # TODO: refactor to use mranges for working hours
    
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
    
    def has_working_hours(self):
        return self.start_time != self.end_time
        
class Schedule(object):
    
    SCHEDULES = {}
    
    def __init__(self):
        self.work_days = [ None ] * 7
        self.hollydays = set()
    
    @classmethod
    def load_spreadsheet(klass, xlsx_file):
        # TODO: point to the replicated database instead of a spreadsheet        
        df = pd.read_excel(xlsx_file)
        for row in df.itertuples():
            sched = klass()
            sched.set_workday(0, parse_time(row.MON_BEGIN), parse_time(row.MON_END))
            sched.set_workday(1, parse_time(row.TUE_BEGIN), parse_time(row.TUE_END))
            sched.set_workday(2, parse_time(row.WED_BEGIN), parse_time(row.WED_END))
            sched.set_workday(3, parse_time(row.THR_BEGIN), parse_time(row.THR_END))
            sched.set_workday(4, parse_time(row.FRI_BEGIN), parse_time(row.FRI_END))
            sched.set_workday(5, parse_time(row.SAT_BEGIN), parse_time(row.SAT_END))
            sched.set_workday(6, parse_time(row.SUN_BEGIN), parse_time(row.SUN_END))
            if not pd.isna(row.FERIADO_01):  sched.add_hollyday(parse_date(row.FERIADO_01))
            if not pd.isna(row.FERIADO_02):  sched.add_hollyday(parse_date(row.FERIADO_02))
            if not pd.isna(row.FERIADO_03):  sched.add_hollyday(parse_date(row.FERIADO_03))
            if not pd.isna(row.FERIADO_04):  sched.add_hollyday(parse_date(row.FERIADO_04))
            if not pd.isna(row.FERIADO_05):  sched.add_hollyday(parse_date(row.FERIADO_05))
            if not pd.isna(row.FERIADO_06):  sched.add_hollyday(parse_date(row.FERIADO_06))
            if not pd.isna(row.FERIADO_07):  sched.add_hollyday(parse_date(row.FERIADO_07))
            if not pd.isna(row.FERIADO_08):  sched.add_hollyday(parse_date(row.FERIADO_08))
            if not pd.isna(row.FERIADO_09):  sched.add_hollyday(parse_date(row.FERIADO_09))
            if not pd.isna(row.FERIADO_10):  sched.add_hollyday(parse_date(row.FERIADO_10))
            if not pd.isna(row.FERIADO_11):  sched.add_hollyday(parse_date(row.FERIADO_11))
            if not pd.isna(row.FERIADO_12):  sched.add_hollyday(parse_date(row.FERIADO_12))
            if not pd.isna(row.FERIADO_13):  sched.add_hollyday(parse_date(row.FERIADO_13))
            if not pd.isna(row.FERIADO_14):  sched.add_hollyday(parse_date(row.FERIADO_14))
            if not pd.isna(row.FERIADO_15):  sched.add_hollyday(parse_date(row.FERIADO_15))
            if not pd.isna(row.FERIADO_16):  sched.add_hollyday(parse_date(row.FERIADO_16))
            if not pd.isna(row.FERIADO_17):  sched.add_hollyday(parse_date(row.FERIADO_17))
            if not pd.isna(row.FERIADO_18):  sched.add_hollyday(parse_date(row.FERIADO_18))
            if not pd.isna(row.FERIADO_19):  sched.add_hollyday(parse_date(row.FERIADO_19))
            if not pd.isna(row.FERIADO_20):  sched.add_hollyday(parse_date(row.FERIADO_20))
            klass.SCHEDULES[ row.MESA ] = sched
        return klass.SCHEDULES.copy()
    
    @classmethod    
    def get_schedule_for(klass, mesa):
        return klass.SCHEDULES.get(mesa, None)
        
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
        if not skip_weekend:
            ww.set_workday(5, start_time, end_time)
            ww.set_workday(6, start_time, end_time)
        else:
            last_second = dt.time(23, 59, 59)
            ww.set_workday(5, last_second, last_second)
            ww.set_workday(6, last_second, last_second)
        return ww
        
    def set_workday(self, dow, start_time, end_time):
        self.work_days[ dow ] = self._get_work_day(dow, start_time, end_time)

    def add_hollyday(self, hd):
        self.hollydays.add(hd)
        
    def get_business_hours(self, start_dt, end_dt):
        assert start_dt <= end_dt
        if start_dt == end_dt:
            return []
        start_date  = start_dt.date() 
        end_date    = end_dt.date()
        curr_date   = start_date
        start_time  = start_dt.time()
        end_time    = end_dt.time()
        curr_time   = start_time
        one_day     = dt.timedelta(1)
        result      = []
        
        while curr_date <= end_date:
            dow = self.work_days[ curr_date.weekday() ]
            if curr_date in self.hollydays or not dow.has_working_hours():
                pass # no business hours in a holliday or in a weekend
                
            elif start_date == end_date:
                if end_time < dow.start_time:
                    pass # no business hours before dow start time
                elif start_time > dow.end_time:
                    pass # no business hours after dow end time
                else:
                    bh_start_time = max(start_time, dow.start_time)
                    bh_end_time = min(end_time, dow.end_time)
                    bh = (curr_date, bh_start_time, bh_end_time)
                    result.append(bh)
                    
            elif curr_date == start_date:
                if start_time > dow.end_time:
                    pass # no business hours after dow end time
                else:
                    bh = (curr_date, max(start_time, dow.start_time), dow.end_time)
                    result.append(bh)

            elif curr_date == end_date:
                if end_time < dow.start_time:
                    pass # no business hours before dow start time
                else:
                    bh = (curr_date, dow.start_time, min(end_time, dow.end_time))
                    result.append(bh)
            else:
                bh = (curr_date, dow.start_time, dow.end_time)
                result.append(bh)
                
            curr_date = curr_date + one_day
        
        c = dt.datetime.combine
        result2 = []
        for date, begin, end in result:
            if begin == end:
                continue
            bh = c(date, begin), c(date, end)
            result2.append(bh)
        return result2
        
class Range(object):
    
    __slots__ = [ 'hi', 'low' ]
    
    def __init__(self, low, hi):
        assert low <= hi
        self.low = low
        self.hi = hi
    
    def length(self):
        return self.hi - self.low
        
    def contains(self, elt):
        return self.low <= elt <= self.hi
    
    def copy(self):
        return Range(self.low, self.hi)
    
    def list_elements(self):
        return list(range(self.low, self.hi+1))
        
    def overlaps_with(self, other):
        # TODO: optimize
        return self.contains(other.hi) or self.contains(other.low) or \
               other.contains(self.hi) or other.contains(self.low)
    
    def disjoint_with(self, other):
        return not self.overlaps_with(other)
    
    def intersection(self, other):
        assert self.overlaps_with(other)
        low = max(self.low, other.low)
        hi = min(self.hi, other.hi)
        return Range(low, hi)
    
    def difference(self, other):
        if not self.overlaps_with(other):
            return Range(self.low, self.hi)
        if other.hi > self.low:
            return Range(other.hi, self.hi)
        if other.low < self.hi:
            return Range(self.low, self.low)
        assert 1 == 2 # should not happen
        
    def union(self, other):
        assert self.overlaps_with(other)
        low = min(self.low, other.low)
        hi = max(self.hi, other.hi)
        return Range(low, hi)

    def disjoint_union(self, other):
        low = min(self.low, other.low)
        hi = max(self.hi, other.hi)
        return Range(low, hi)
        
    def __eq__(self, other):
        return ((self.low, self.hi) == (other.low, other.hi))

    def __ne__(self, other):
        return ((self.low, self.hi) != (other.low, other.hi))

    def __lt__(self, other):
        return ((self.low, self.hi) < (other.low, other.hi))

    def __le__(self, other):
        return ((self.low, self.hi) <= (other.low, other.hi))

    def __gt__(self, other):
        return ((self.low, self.hi) > (other.low, other.hi))

    def __ge__(self, other):
        return ((self.low, self.hi) >= (other.low, other.hi))

    def __repr__(self):
        return "Range({}, {})".format(repr(self.low), repr(self.hi))
    
    def _check(self):
        assert self.low <= self.hi
        
class MRange(object):
    
    # TODO: Treat non disjoint ranges
    __slots__ = [ 'ranges', 'total_range' ]
    
    class MRangeInstant(object):
        
        """
            from mrange_analysis.xlsx on ./docs
            invalid states are not represented
            
            BEGIN SELF           - bs
            END SELF             - es
            BEGIN OTHER          - bo
            END OTHER            - eo
            COLLECTING SELF IN   - in_cs
            COLLECTING OTHER IN  - in_co
            ->
            CONSIDER             - cons
            COLLECTING SELF OUT  - out_cs
            COLLECTING OTHER OUT - out_co
        """
        
        INTERSECTION_CASES = {
            # non valid cases are not represented
            ( True,  True,  True,  True,  False, False ) : ( True,  False, False ),
            ( True,  True,  True,  False, False, False ) : ( True,  False, True  ),
            ( True,  True,  False, True,  False, True  ) : ( True,  False, False ),
            ( True,  True,  False, False, False, True  ) : ( True,  False, False ),
            ( True,  True,  False, False, False, False ) : ( False, False, False ),
            ( True,  False, True,  True,  False, False ) : ( True,  True,  False ),
            ( True,  False, True,  False, False, False ) : ( True,  True,  True  ),
            ( True,  False, False, True,  False, True  ) : ( True,  True,  False ),
            ( True,  False, False, False, False, True  ) : ( True,  True,  True  ),
            ( True,  False, False, False, False, False ) : ( False, True,  False ),
            ( False, True,  True,  True,  True,  False ) : ( True,  False, False ),
            ( False, True,  True,  False, True,  False ) : ( True,  False, True  ),
            ( False, True,  False, True,  True,  True  ) : ( True,  False, False ),
            ( False, True,  False, False, True,  True  ) : ( True,  False, True  ),
            ( False, True,  False, False, True,  False ) : ( False, False, False ),
            ( False, False, True,  True,  True,  False ) : ( True,  True,  False ),
            ( False, False, True,  True,  False, False ) : ( False, False, False ),
            ( False, False, True,  False, True,  False ) : ( True,  True,  True  ),
            ( False, False, True,  False, False, False ) : ( False, False, True  ),
            ( False, False, False, True,  True,  True  ) : ( True,  True,  False ),
            ( False, False, False, True,  False, True  ) : ( False, False, False ),
            ( False, False, False, False, True,  True  ) : ( True,  True,  True  ),
            ( False, False, False, False, True,  False ) : ( False, True,  False ),
            ( False, False, False, False, False, True  ) : ( False, False, True  ),
            ( False, False, False, False, False, False ) : ( False, False, False )            
        }
        
        DIFFERENCE_CASES = {
            # non valid cases are not represented
            ( True,  True,  True,  True,  False, False ) : ( False, False, False ),
            ( True,  True,  True,  False, False, False ) : ( False, False, True  ),
            ( True,  True,  False, True,  False, True  ) : ( False, False, False ),
            ( True,  True,  False, False, False, True  ) : ( False, False, True  ),
            ( True,  True,  False, False, False, False ) : ( True,  False, False ),
            ( True,  False, True,  True,  False, False ) : ( False, True,  False ),
            ( True,  False, True,  False, False, False ) : ( False, True,  True  ),
            ( True,  False, False, True,  False, True  ) : ( False, True,  False ),
            ( True,  False, False, False, False, True  ) : ( False, True,  True  ),
            ( True,  False, False, False, False, False ) : ( True,  True,  False ),
            ( False, True,  True,  True,  True,  False ) : ( False, False, False ),
            ( False, True,  True,  False, True,  False ) : ( False, False, True  ),
            ( False, True,  False, True,  True,  True  ) : ( False, False, False ),
            ( False, True,  False, False, True,  True  ) : ( False, False, True  ),
            ( False, True,  False, False, True,  False ) : ( True,  False, False ),
            ( False, False, True,  True,  True,  False ) : ( False, True,  False ),
            ( False, False, True,  True,  False, False ) : ( False, False, True  ),
            ( False, False, True,  False, True,  False ) : ( False, True,  True  ),
            ( False, False, True,  False, False, False ) : ( False, False, True  ),
            ( False, False, False, True,  True,  True  ) : ( False, True,  False ),
            ( False, False, False, True,  False, True  ) : ( False, False, False ),
            ( False, False, False, False, True,  True  ) : ( False, True,  True  ),
            ( False, False, False, False, True,  False ) : ( True,  True,  False ),
            ( False, False, False, False, False, True  ) : ( False, False, True  ),
            ( False, False, False, False, False, False ) : ( False, False, False ),
        }
        
        __slots__ = [ 'begin_self', 'end_self', 'begin_other', 'end_other' ]
        
        def __init__(self):
            self.begin_self     = False
            self.end_self       = False
            self.begin_other    = False
            self.end_other      = False
            
        def __repr__(self):
            return f"Row({repr(self.begin_self)}, {repr(self.end_self)}, {repr(self.begin_other)}, {repr(self.end_other)})"
        
        def get_transition(self, collecting_self, collecting_other, state_transitions):
            consider, new_collecting_self, new_collecting_other = state_transitions[ (
                self.begin_self,
                self.end_self,
                self.begin_other,
                self.end_other,
                collecting_self,
                collecting_other
            ) ]
            return consider, new_collecting_self, new_collecting_other
        
    def __init__(self):
        self.ranges = []
        self.total_range = None
        
    def __len__(self):
        return len(self.ranges)

    def __eq__(self, other):
        return self.ranges == other.ranges

    def __ne__(self, other):
        return self.ranges != other.ranges

    def __repr__(self):
        return "MRange({})".format(
            ", ".join(map(repr, self.ranges))
        )
    
    def __iter__(self):
        return iter([ r.copy() for r in self.ranges ])
        
    def _create_range(self, low, hi):
        return Range(low, hi)
    
    def _add_empty(self, r):
        # no ranges seem so far. Just add it
        self.total_range = self._create_range(r.low, r.hi)
        bisect.insort(self.ranges, r.copy())
    
    def _add_no_overlap(self, r):
        # the added range does not overlap with the total range or any particular range.
        # Just add it.
        low = min(self.total_range.low, r.low)
        hi = max(self.total_range.hi, r.hi)
        self.total_range = self._create_range(low, hi)
        bisect.insort(self.ranges, r)
    
    def _find_overlap_idx(self, r):
        overlap_idx = -1
        for i in range(len(self.ranges)):
            curr = self.ranges[ i ]
            if curr.overlaps_with(r):
                return i
        return -1
    
    def _find_overlap_count(self, r, overlap_idx):
        overlap_count = 0
        qty = len(self.ranges)
        for i in range(overlap_idx, qty):
            curr = self.ranges[ i ]
            if curr.overlaps_with(r):
                overlap_count += 1
        return overlap_count
    
    def copy(self):
        copy = MRange()
        for range in self.ranges:
            copy.add_range(range)
        return copy
        
    def add(self, low, hi):
        return self.add_range(Range(low, hi))
        
    def add_range(self, r):
        # beware when making changes
        # this is actually harder than it looks
        if self.total_range is None:
            self._add_empty(r)
            return self
            
        low = min(self.total_range.low, r.low)
        hi = max(self.total_range.hi, r.hi)
        cand_total_range = self._create_range(low, hi)
        if not cand_total_range.overlaps_with(r):
            self._add_no_overlap(r)
            return self
        
        qty = len(self.ranges)
        assert qty > 0
        overlap_idx = self._find_overlap_idx(r)
        assert overlap_idx < qty
        if overlap_idx < 0: # no overlaps
            self._add_no_overlap(r)
            return self
        
        overlap_count = self._find_overlap_count(r, overlap_idx)
        assert overlap_count > 0
        assert overlap_idx > -1
        assert overlap_idx + overlap_count - 1 < qty 
        
        if overlap_count > 1:
            raise ValueError("too many overlaps")
        curr = self.ranges[ overlap_idx ]
        if r.low >= curr.low and r.hi <= curr.hi: # is equal or contained wholy within
            return self
        elif curr.low >= r.low and curr.hi <= r.hi: # is equal or contained wholy within
            self.ranges[ overlap_idx ] =  Range(r.low, r.hi) # merge left
        elif r.hi == curr.low:
            self.ranges[ overlap_idx ] =  Range(r.low, curr.hi) # merge left
            return self
        elif r.low == curr.hi:
            self.ranges[ overlap_idx ] =  Range(curr.low, r.hi) # merge hi
            return self
        else:
            raise ValueError("unmergeable overlap")
        assert 1 == 2 # should not happen            
            
    def contains(self, elmt):
        if not self.total_range.contains(elmt):
            return False
        for range in self.ranges:
            if range.contains(elmt):
                return True
        return False
    
    def _do_set_operation(self, other, state_transitions):
        # beware when making changes
        # this is actually harder than it looks        
                
        Row = self.MRangeInstant
        whens = {}
        # list all time units contained within the total range
        #for when in self.total_range.list_elements():
        #    whens[ when ] = Row()
        # for each range within the mrange, mark when it begins and end
        for range in self.ranges:
            if range.low not in whens:
                whens[ range.low ] = Row()
            if range.hi not in whens:
                whens[ range.hi ] = Row()
            whens[ range.low ].begin_self = True
            whens[ range.hi ].end_self = True
        
        # for each range within the mrange, mark when it begins and end,
        # adding it if needed
        for range in other.ranges:
            if range.low not in whens:
                whens[ range.low ] = Row()
            if range.hi not in whens:
                whens[ range.hi ] = Row()
            whens[ range.low ].begin_other = True
            whens[ range.hi ].end_other = True
        
        # for each time unit, check if has a valid transition
        collecting_self  = False
        collecting_other = False
        last_when        = None
        result_tmp       = []
        implied_row      = Row() # nothing begins and nothing ends
        for when, row in sorted(whens.items()): # not sorting this was a nasty bug
            
            # for performance reasons, reconstruct the implied ranges when nothing changes
            if last_when is not None: # no implied rows at the start. --> Nasty bug here when testing thruthiness instead of nothingness
                consider, still_collecting_self, still_collecting_other = implied_row.get_transition(collecting_self, collecting_other, state_transitions)
                assert still_collecting_self == collecting_self # not allowed to change in an implied row
                assert still_collecting_other == collecting_other # not allowed to change in an implied row
                if consider: # if we're adding time units in the implied rows
                    low = last_when + 1 # add 1 to start the implied value
                    hi = when - 1
                    if low <= hi:
                        result_tmp.append( (low, hi) )
            
            if PRINT_TRANSITIONS:
                print(when, ')', row, collecting_self, collecting_other, end=' -> ', sep=', ')
            consider, collecting_self, collecting_other = row.get_transition(collecting_self, collecting_other, state_transitions)
            if PRINT_TRANSITIONS:
                print(consider, collecting_self, collecting_other, sep=', ')
            if consider:
                result_tmp.append( (when, when) )
            last_when = when
        # added the list of time units as ranges within an mrange
        result = MRange()
        if len(result_tmp) == 0:
            return result
        last_low, last_hi = result_tmp[ 0 ][ 0 ], result_tmp[ 0 ][ 1 ] 
        assert last_low == last_hi # first is never an implied range
        for curr_low, curr_hi in result_tmp[ 1: ]:
            if last_hi + 1 < curr_low: # range does not "touch"
                result.add(last_low, last_hi)
                last_low, last_hi = curr_low, curr_hi
            elif last_hi + 1 == curr_low: # ranges "touch"
                last_hi = curr_hi
            else:
                assert 1 == 2 # should not happen
        result.add(last_low, last_hi)
        return result
        
    def difference(self, other):
        # when differencing against nothing, yield a copy of yourself
        if len(other) == 0: 
            return self.copy()         
        # empty range always yields another empty range
        if len(self) == 0:
            return self.copy() 
        return self._do_set_operation(other, self.MRangeInstant.DIFFERENCE_CASES)
    
    def intersection(self, other):
        # when intersecting with nothing, yield nothing
        if len(other) == 0: 
            return other.copy() 
        # empty range always yields another empty range
        if len(self) == 0:
            return self.copy()         
        return self._do_set_operation(other, self.MRangeInstant.INTERSECTION_CASES)

def convert_to_seconds(datetime_txt):
    return datetime2tstmp(datetime_txt)

def load_spreadsheet(xlsx_file):
    return Schedule.load_spreadsheet(xlsx_file)
    
def calc_duration(sched, on_hold, start, end):
    assert start <= end
    
    if sched is None:
        return 0
    if on_hold:
        return 0
    
    start_s, end_s = convert_to_seconds(start), convert_to_seconds(end)
    if start_s == end_s:
        return 0
    
    business_hours = sched.get_business_hours(parse_datetime(start), parse_datetime(end))
    if len(business_hours) == 0:
        return 0
    
    action_range = MRange().add(start_s, end_s)
    
    business_hours_range = MRange()
    for bh_begin, bh_end in business_hours:
        bh_begin_txt, bh_end_txt = unparse_datetime(bh_begin), unparse_datetime(bh_end)
        bh_begin_s, bh_end_s = convert_to_seconds(bh_begin_txt), convert_to_seconds(bh_end_txt)
        business_hours_range.add(bh_begin_s, bh_end_s)
    result_range = business_hours_range.intersection(action_range)
    result_s = sum([ r.length() for r in result_range ])
    result_m = result_s // 60
    return result_m
    