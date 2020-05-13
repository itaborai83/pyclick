import bisect
import unittest
import datetime as dt
from pyclick.ranges import *
import pyclick.ranges as rng
from pyclick.util import parse_datetime, parse_date, parse_time

pd = parse_datetime

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
        self.assertEqual(result, weekdays)

    ###########################################################################
    ###########################################################################
    def test_it_returns_nothing_when_intersecting_against_an_empty_mrange(self):
        m1 = MRange().add(1, 2).add(3, 4)
        m2 = MRange()
        m3 = m1.intersection(m2)
        self.assertEqual(m3, m2)
    
    def test_it_returns_nothing_when_nothing_intersects_with_something(self):
        m1 = MRange().add(1, 2).add(3, 4)
        m2 = MRange()
        m3 = m1.intersection(m2)
        self.assertEqual(m3, m2)
    
    def test_it_returns_nothing_when_intersecting_against_a_non_overlapping_mrange(self):
        m1 = MRange().add(1, 2).add(5, 6)
        m2 = MRange().add(3, 4)
        m3 = MRange()
        m4 = m1.intersection(m2)
        self.assertEqual(m4, m3)
        m5 = m2.intersection(m1)
        self.assertEqual(m5, m3)
    
    def test_it_intersects_with_a_smaller_range(self):
        m1 = MRange().add(0, 6)
        m2 = MRange().add(3, 5)
        m3 = m1.intersection(m2)
        self.assertEqual(m2, m3)    
        
    
    def test_it_intersects_with_a_bigger_range(self):
        m1 = MRange().add(3, 5)
        m2 = MRange().add(0, 6)
        m3 = m1.intersection(m2)
        self.assertEqual(m1, m3)
    
    def test_it_removes_the_weekends_from_may_2020(self):
        may = MRange().add(1, 31)
        weekends = MRange().add(2, 3).add(9, 10).add(16, 17).add(23, 24).add(30, 31)
        weekdays = MRange().add(1, 1).add(4, 8).add(11, 15).add(18, 22).add(25, 29)
        result = may.difference(weekends)
        self.assertEqual(result, weekdays)
    
    ###########################################################################
    ###########################################################################    
class TestSchedule(unittest.TestCase):

    """
        January 2000
    Sa Su Mo Tu We Th Fr
     1  2  3  4  5  6  7
     8  9 10 11 12 13 14
    15 16 17 18 19 20 21
    22 23 24 25 26 27 28
    29 30 31
    """
    
    def setUp(self):
        self.bh_start_time1 = parse_time("08:00:00")
        self.bh_end_time1 = parse_time("18:59:59")
        self.sched1 = Schedule.build(self.bh_start_time1, self.bh_end_time1)
    def tearDown(self):
        pass
    
    def test_it_returns_no_business_hours_when_after_hours(self):
        start_dt = parse_datetime('2000-01-03 19:00:00')
        end_dt = parse_datetime('2000-01-03 19:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        self.assertEqual(bh, [])
        
        start_dt = parse_datetime('2000-01-03 19:00:00')
        end_dt = parse_datetime('2000-01-04 09:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ ( pd('2000-01-04 08:00:00'), pd('2000-01-04 09:30:00') ) ]
        self.assertEqual(bh, expected)

        start_dt = parse_datetime('2000-01-03 19:00:00')
        end_dt = parse_datetime('2000-01-05 09:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ 
            ( pd('2000-01-04 08:00:00'), pd('2000-01-04 18:59:59') ),
            ( pd('2000-01-05 08:00:00'), pd('2000-01-05 09:30:00') ) 
        ]
        self.assertEqual(bh, expected)
        
        
    def test_it_returns_no_business_hours_when_before_hours(self):
        start_dt = parse_datetime('2000-01-03 07:00:00')
        end_dt = parse_datetime('2000-01-03 07:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        self.assertEqual(bh, [])

        start_dt = parse_datetime('2000-01-03 07:00:00')
        end_dt = parse_datetime('2000-01-04 09:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ 
            ( pd('2000-01-03 08:00:00'), pd('2000-01-03 18:59:59') ),
            ( pd('2000-01-04 08:00:00'), pd('2000-01-04 09:30:00') ) ,
        ]
        self.assertEqual(bh, expected)

        start_dt = parse_datetime('2000-01-03 07:00:00')
        end_dt = parse_datetime('2000-01-05 09:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ 
            ( pd('2000-01-03 08:00:00'), pd('2000-01-03 18:59:59') ),
            ( pd('2000-01-04 08:00:00'), pd('2000-01-04 18:59:59') ) ,
            ( pd('2000-01-05 08:00:00'), pd('2000-01-05 09:30:00') )
        ]
        self.assertEqual(bh, expected)
        
    def test_it_returns_the_day_business_hours_when_it_starts_too_early_and_ends_too_late(self):
        start_dt = pd('2000-01-03 07:00:00')
        end_dt = pd('2000-01-03 19:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ ( pd('2000-01-03 08:00:00'), pd('2000-01-03 18:59:59') ) ]
        self.assertEqual(bh, expected)

        start_dt = pd('2000-01-03 07:00:00')
        end_dt = pd('2000-01-04 19:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ 
                    ( pd('2000-01-03 08:00:00'), pd('2000-01-03 18:59:59') ), 
                    ( pd('2000-01-04 08:00:00'), pd('2000-01-04 18:59:59') )
        ]
        self.assertEqual(bh, expected)

        start_dt = pd('2000-01-03 07:00:00')
        end_dt = pd('2000-01-05 19:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ 
                    ( pd('2000-01-03 08:00:00'), pd('2000-01-03 18:59:59') ), 
                    ( pd('2000-01-04 08:00:00'), pd('2000-01-04 18:59:59') ),
                    ( pd('2000-01-05 08:00:00'), pd('2000-01-05 18:59:59') )
        ]
        self.assertEqual(bh, expected)
        
    def test_it_returns_the_business_when_it_starts_too_early(self):
        start_dt = pd('2000-01-03 07:00:00')
        end_dt = pd('2000-01-03 12:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ ( pd('2000-01-03 08:00:00'), pd('2000-01-03 12:30:00') ) ]
        self.assertEqual(bh, expected)

        start_dt = pd('2000-01-03 07:00:00')
        end_dt = pd('2000-01-04 12:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ 
            ( pd('2000-01-03 08:00:00'), pd('2000-01-03 18:59:59') ),
            ( pd('2000-01-04 08:00:00'), pd('2000-01-04 12:30:00') )

        ]
        self.assertEqual(bh, expected)

        start_dt = pd('2000-01-03 07:00:00')
        end_dt = pd('2000-01-05 12:30:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ 
            ( pd('2000-01-03 08:00:00'), pd('2000-01-03 18:59:59') ),
            ( pd('2000-01-04 08:00:00'), pd('2000-01-04 18:59:59') ),
            ( pd('2000-01-05 08:00:00'), pd('2000-01-05 12:30:00') )

        ]
        self.assertEqual(bh, expected)

    def test_it_returns_the_business_hours_when_it_ends_too_late(self):
        start_dt = pd('2000-01-03 12:30:00')
        end_dt = pd('2000-01-03 20:00:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ ( pd('2000-01-03 12:30:00'), pd('2000-01-03 18:59:59') ) ]
        self.assertEqual(bh, expected)

        start_dt = pd('2000-01-03 12:30:00')
        end_dt = pd('2000-01-04 20:00:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ 
            ( pd('2000-01-03 12:30:00'), pd('2000-01-03 18:59:59') ),
            ( pd('2000-01-04 08:00:00'), pd('2000-01-04 18:59:59') )
        ]
        self.assertEqual(bh, expected)

        start_dt = pd('2000-01-03 12:30:00')
        end_dt = pd('2000-01-05 20:00:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ 
            ( pd('2000-01-03 12:30:00'), pd('2000-01-03 18:59:59') ),
            ( pd('2000-01-04 08:00:00'), pd('2000-01-04 18:59:59') ), 
            ( pd('2000-01-05 08:00:00'), pd('2000-01-05 18:59:59') )
        ]
        self.assertEqual(bh, expected)
        
    def test_it_returns_no_business_hours_on_a_weekend(self):
        start_dt = pd('2000-01-01 12:30:00')
        end_dt = pd('2000-01-02 20:00:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ ]
        self.assertEqual(bh, expected)

        start_dt = pd('2000-01-01 12:30:00')
        end_dt = pd('2000-01-03 12:00:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ ( pd('2000-01-03 08:00:00'), pd('2000-01-03 12:00:00') ) ]
        self.assertEqual(bh, expected)

        start_dt = pd('1999-12-31 12:30:00')
        end_dt = pd('2000-01-03 12:00:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ 
            ( pd('1999-12-31 12:30:00'), pd('1999-12-31 18:59:59') ),
            ( pd('2000-01-03 08:00:00'), pd('2000-01-03 12:00:00') ) 
        ]
        self.assertEqual(bh, expected)

    def test_it_returns_no_business_hours_on_a_hollyday(self):
        hollyday = parse_date('2000-01-03')
        self.sched1.add_hollyday(hollyday)
        start_dt = pd('2000-01-01 12:30:00')
        end_dt = pd('2000-01-03 20:00:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ ]
        self.assertEqual(bh, expected)

        start_dt = pd('2000-01-01 12:30:00')
        end_dt = pd('2000-01-04 12:00:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ ( pd('2000-01-04 08:00:00'), pd('2000-01-04 12:00:00') ) ]
        self.assertEqual(bh, expected)
        
        start_dt = pd('1999-12-31 12:30:00')
        end_dt = pd('2000-01-04 12:00:00')
        bh = self.sched1.get_business_hours(start_dt, end_dt)
        expected = [ 
            ( pd('1999-12-31 12:30:00'), pd('1999-12-31 18:59:59') ), 
            ( pd('2000-01-04 08:00:00'), pd('2000-01-04 12:00:00') ) 
        
        ]
        self.assertEqual(bh, expected)

class CalcDurationTest(unittest.TestCase):
    
    """
        January 2000
    Sa Su Mo Tu We Th Fr
     1  2  3  4  5  6  7
     8  9 10 11 12 13 14
    15 16 17 18 19 20 21
    22 23 24 25 26 27 28
    29 30 31
    """
    
    def setUp(self):
        self.mesa24x7    = Schedule.build(dt.time(0, 0, 0), dt.time(23, 59, 59), skip_weekend=False)
        self.mesa_normal = Schedule.build(dt.time(8, 0, 0), dt.time(18, 59, 59), skip_weekend=True)
    
    def tearDown(self):
        pass
    
    def test_it_converts_a_datetime_range_into_minutes(self):
        minutes = convert_to_minutes('2000-01-01 00:00:00') - convert_to_minutes('2000-01-01 00:00:00')
        self.assertEqual(minutes, 0)
        minutes = convert_to_minutes('2000-01-01 00:00:30') - convert_to_minutes('2000-01-01 00:00:00')
        self.assertEqual(minutes, 0)
        minutes = convert_to_minutes('2000-01-01 00:00:31') - convert_to_minutes('2000-01-01 00:00:00')
        self.assertEqual(minutes, 0)
        minutes = convert_to_minutes('2000-01-01 00:01:29') - convert_to_minutes('2000-01-01 00:00:00')
        self.assertEqual(minutes, 1)
        
        minutes = convert_to_minutes('2000-01-01 00:00:15') - convert_to_minutes('2000-01-01 00:00:15')
        self.assertEqual(minutes, 0)
        minutes = convert_to_minutes('2000-01-01 00:00:45') - convert_to_minutes('2000-01-01 00:00:15')
        self.assertEqual(minutes, 0)
        minutes = convert_to_minutes('2000-01-01 00:00:46') - convert_to_minutes('2000-01-01 00:00:15')
        self.assertEqual(minutes, 0)
        minutes = convert_to_minutes('2000-01-01 00:01:44') - convert_to_minutes('2000-01-01 00:00:15')
        self.assertEqual(minutes, 1)
        
        minutes = convert_to_minutes('2000-01-01 01:00:15') - convert_to_minutes('2000-01-01 00:00:15')
        self.assertEqual(minutes, 60)
        minutes = convert_to_minutes('2000-01-01 01:00:45') - convert_to_minutes('2000-01-01 00:00:15')
        self.assertEqual(minutes, 60)
        minutes = convert_to_minutes('2000-01-01 01:00:46') - convert_to_minutes('2000-01-01 00:00:15')
        self.assertEqual(minutes, 60)
        minutes = convert_to_minutes('2000-01-01 01:01:44') - convert_to_minutes('2000-01-01 00:00:15')
        self.assertEqual(minutes, 61)
        
    def test_it_returns_a_zero_minutes_duration_within_office_hours(self):
        d = calc_duration(self.mesa_normal, False, '2000-01-03 09:00:00', '2000-01-03 09:00:00')
        self.assertEqual(d, 0)
        d = calc_duration(self.mesa24x7, False, '2000-01-03 09:00:00', '2000-01-03 09:00:00')
        self.assertEqual(d, 0)
    
    def test_it_returns_a_zero_minutes_duration_outside_office_hours(self):
        # saturday 0 minute duration
        d = calc_duration(self.mesa_normal, False, '2000-01-01 09:00:00', '2000-01-01 09:00:00')
        self.assertEqual(d, 0)
        # saturday 60 minute duration
        d = calc_duration(self.mesa_normal, False, '2000-01-01 09:00:00', '2000-01-01 10:00:00')
        self.assertEqual(d, 0)
        # saturday to sunday
        d = calc_duration(self.mesa_normal, False, '2000-01-01 09:00:00', '2000-01-02 09:00:00')
        self.assertEqual(d, 0)
        # saturday to early monday
        d = calc_duration(self.mesa_normal, False, '2000-01-01 07:00:00', '2000-01-03 07:59:59')
        self.assertEqual(d, 0)
    
    def test_it_returns_a_zero_minutes_when_a_schedule_is_not_given(self):
        d = calc_duration(None, False, '2000-01-03 09:00:00', '2099-01-03 10:00:00')
        self.assertEqual(d, 0)

    def test_it_returns_a_zero_minutes_when_it_is_on_hold(self):
        d = calc_duration(self.mesa_normal, True, '2000-01-03 09:00:00', '2001-01-03 10:00:00')
        self.assertEqual(d, 0)
        d = calc_duration(self.mesa24x7, True, '2000-01-03 09:00:00', '2099-01-03 10:00:00')
        self.assertEqual(d, 0)
        
    def test_it_returns_a_60_minutes_duration_within_office_hours(self):
        d = calc_duration(self.mesa_normal, False, '2000-01-03 09:00:00', '2000-01-03 10:00:00')
        self.assertEqual(d, 60)
        d = calc_duration(self.mesa24x7, False, '2000-01-03 09:00:00', '2000-01-03 10:00:00')
        self.assertEqual(d, 60)
    
    def test_it_returns_a_60_minutes_duration_within_office_hours(self):
        d = calc_duration(self.mesa_normal, False, '2000-01-03 09:00:00', '2000-01-03 10:00:00')
        self.assertEqual(d, 60)
        d = calc_duration(self.mesa24x7, False, '2000-01-03 09:00:00', '2000-01-03 10:00:00')
        self.assertEqual(d, 60)
        
        d = calc_duration(self.mesa_normal, False, '2000-01-03 09:00:00', '2000-01-03 09:59:31')
        self.assertEqual(d, 59)
        d = calc_duration(self.mesa24x7, False, '2000-01-03 09:00:00', '2000-01-03 09:59:30')
        self.assertEqual(d, 59)

    def test_it_returns_a_30_minutes_duration_within_office_hours(self):
        d = calc_duration(self.mesa_normal, False, '2000-01-03 07:30:00', '2000-01-03 08:30:00')
        self.assertEqual(d, 30)
        d = calc_duration(self.mesa_normal, False, '2000-01-03 18:30:00', '2000-01-03 19:30:59')
        self.assertEqual(d, 29) # FIXME: this should be 30
