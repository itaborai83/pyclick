import bisect
import unittest


class MRangeDiffInstant(object):
    
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
    
    def get_transition(self, collecting_self, collecting_other):
        consider, new_collecting_self, new_collecting_other = self.DIFFERENCE_CASES[ (
            self.begin_self,
            self.end_self,
            self.begin_other,
            self.end_other,
            collecting_self,
            collecting_other
        ) ]
        return consider, new_collecting_self, new_collecting_other
    

class Range(object):
    
    __slots__ = [ 'hi', 'low' ]
    
    def __init__(self, low, hi):
        assert low <= hi
        self.low = low
        self.hi = hi
                
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
    
    
        return self.add(Range(low, hi))
    
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
        
    def intersection(self, other):
        pass
    
    def difference(self, other):
        # beware when making changes
        # this is actually harder than it looks        
        
        # when differencing against nothing, yield a copy of yourself
        if len(other) == 0: 
            return self.copy() 
        
        # empty range always yields another empty range
        if len(self) == 0:
            return self.copy() 
        
        Row = MRangeDiffInstant
        whens = {}
        # list all time units contained within the total range
        for when in self.total_range.list_elements():
            whens[ when ] = Row()
        # for each range within the mrange, mark when it begins and end
        for range in self.ranges:
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
        collecting_self = False
        collecting_other = False
        result_tmp = []
        for when, row in whens.items():            
            consider, collecting_self, collecting_other = row.get_transition(collecting_self, collecting_other)
            if consider:
                result_tmp.append(when)
        # added the list of time units as ranges within an mrange
        # compacting it when necessary
        result = MRange()
        if len(result_tmp) == 0:
            return result
        low, hi = result_tmp[ 0 ], result_tmp[ 0 ]
        for when in result_tmp[ 1: ]:
            if hi + 1 == when: # contiguous
                hi = when
            else:
                result.add(low, hi)
                low, hi = when, when
        result.add(low, hi)
        return result
            
class RangeTest(unittest.TestCase):

    def setUp(self):
        self.r1 = Range(1, 3)
        self.r2 = Range(2, 4)
        self.r3 = Range(3, 5)
        self.r4 = Range(4, 6)
        self.r5 = Range(5, 7)
        self.r6 = Range(6, 8)
        self.r7 = Range(7, 9)
        self.r8 = Range(8, 10)
        
    def tearDown(self):
        pass
    
    def test_it_checks_when_a_point_is_contained_within(self):
        self.assertFalse(self.r1.contains(0), "should not contain 0")
        self.assertTrue(self.r1.contains(1), "does not contain 1")
        self.assertTrue(self.r1.contains(2), "does not contain 2")
        self.assertTrue(self.r1.contains(3), "does not contain 3")
        self.assertFalse(self.r1.contains(4), "should not contain 4")
    
    def test_it_checks_when_ranges_overlaps(self):
        self.assertFalse(self.r5.overlaps_with(self.r2))
        self.assertTrue(self.r5.overlaps_with(self.r3))
        self.assertTrue(self.r5.overlaps_with(self.r4))
        self.assertTrue(self.r5.overlaps_with(self.r5))
        self.assertTrue(self.r5.overlaps_with(self.r6))
        self.assertTrue(self.r5.overlaps_with(self.r6))
        self.assertTrue(self.r5.overlaps_with(self.r7))
        self.assertFalse(self.r5.overlaps_with(self.r8))
    
    def test_it_returns_the_elements_in_between(self):
        self.assertEqual(self.r1.list_elements(), [1, 2, 3])
        
    def test_it_adds_ranges_to_an_mrange(self):
        m = MRange().add_range(self.r4).add_range(self.r1)
        self.assertEqual(m.total_range, Range(1, 6))
        self.assertEqual(len(m), 2)
    
    def test_it_checks_when_a_point_is_contained_within_an_mrange(self):
        m = MRange().add_range(self.r2).add_range(self.r6)
        self.assertFalse(m.contains(1), "should not contain 1")
        self.assertTrue(m.contains(2), "should not contain 2")
        self.assertTrue(m.contains(3), "should not contain 3")
        self.assertTrue(m.contains(4), "should not contain 4")
        self.assertFalse(m.contains(5), "should not contain 5")
        self.assertTrue(m.contains(6), "should not contain 6")
        self.assertTrue(m.contains(7), "should not contain 7")
        self.assertTrue(m.contains(8), "should not contain 8")
        self.assertFalse(m.contains(9), "should not contain 9")
    
    def test_it_adds_a_range_to_an_empty_mrange(self):
        m = MRange().add_range(self.r1)
        total_range = Range(m.ranges[0].low, m.ranges[-1].hi)
        self.assertEqual(1, len(m), "incorrect mrange length")
        self.assertEqual(m.total_range, total_range)
    
    def test_it_adds_a_range_to_an_mrange_with_no_total_overlap(self):
        m = MRange().add(0, 1).add(2, 3).add(4, 5)
        total_range = Range(m.ranges[0].low, m.ranges[-1].hi)
        self.assertEqual(3, len(m), "incorrect mrange length")
        self.assertEqual(m.total_range, total_range)
    
    def test_it_adds_a_range_to_an_mrange_with_total_overlap_but_no_actual_overlap(self):        
        m = MRange()
        m.add(0, 1).add(4, 5).add(2, 3)
        total_range = Range(m.ranges[0].low, m.ranges[-1].hi)
        self.assertEqual(3, len(m), "incorrect mrange length")
        self.assertEqual(m.total_range, total_range)
    
    def test_id_adds_a_range_to_an_mrange_with_actual_overlap_extending_an_existing_range_to_its_left(self):
        m = MRange()
        m.add(0, 2).add(4, 6).add(3, 4)
        total_range = Range(0, 6)
        self.assertEqual(2, len(m), "incorrect mrange length")
        self.assertEqual(m.total_range, total_range)
    
    def test_id_adds_a_range_to_an_mrange_with_actual_overlap_extending_an_existing_range_to_its_left(self):
        m = MRange().add(0, 2).add(4, 6).add(2, 3)
        total_range = Range(0, 6)
        self.assertEqual(2, len(m), "incorrect mrange length")
        self.assertEqual(m.total_range, total_range)
    
    def test_it_adds_an_already_existing_range_to_an_mrange(self):
        m = MRange().add(0, 2).add(3, 4).add(5, 7).add(3, 4)
        total_range = Range(0, 7)
        self.assertEqual(3, len(m), "incorrect mrange length")
        self.assertEqual(m.total_range, total_range)
    
    def test_it_fails_to_add_a_range_overlapping_with_two_ranges(self):
        m = MRange().add(0, 2).add(3, 5)
        with self.assertRaises(ValueError):
            m.add(1, 4)
    
    def test_it_returns_itself_when_differencing_against_an_empty_mrange(self):
        m1 = MRange().add(1, 2).add(3, 4)
        m2 = MRange()
        m3 = m1.difference(m2)
        self.assertEqual(m3, m1)
    
    def test_it_returns_an_empty_range_when_differencing_and_itself_is_empty(self):
        m1 = MRange()
        m2 = MRange().add(1, 2).add(3, 4)
        m3 = m1.difference(m2)
        self.assertEqual(m3, m1)
    
    def test_it_returns_itself_when_differencing_against_a_non_overlapping_mrange(self):
        m1 = MRange().add(1, 2).add(5, 6)
        m2 = MRange().add(3, 4)
        m3 = m1.difference(m2)
        self.assertEqual(m1, m3)
        m4 = m2.difference(m1)
        self.assertEqual(m2, m4)
    
    def test_it_carves_out_a_difference_from_a_bigger_range(self):
        m1 = MRange().add(0, 6)
        m2 = MRange().add(3, 5)
        m3 = m1.difference(m2)
        m4 = MRange().add(0, 2).add(6, 6)
        self.assertEqual(m3, m4)
    
    def test_it_removes_the_weekends_from_may_2020(self):
        may = MRange().add(1, 31)
        weekends = MRange().add(2, 3).add(9, 10).add(16, 17).add(23, 24).add(30, 31)
        weekdays = MRange().add(1, 1).add(4, 8).add(11, 15).add(18, 22).add(25, 29)
        result = may.difference(weekends)
        #print()
        #print('may      ', may)
        #print('weekends ', weekends)
        #print('weekdays ', weekdays)
        #print('result   ', result)
        #print()
        self.assertEqual(result, weekdays)
        
        
    