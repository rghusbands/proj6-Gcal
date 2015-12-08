import main
import nose
import arrow
import datetime

#
# These test cases check the free time algorithm to ensure
# different scenarios are treated as they should be.
#


#base case with no events in the day. From 9am to 5pm.
def test1():
    start_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    end_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    events_list = []
    free_times = str(main.freeTimes(events_list,start_date,end_date))
    correct_result = ["[[<Arrow [2015-12-08T09:00:00-08:00]>, <Arrow [2015-12-08T17:00:00-08:00]>]]"]
    correct_result = ''.join(correct_result)
    print(correct_result)
    print("-------------------------------------------")
    print(free_times)
    assert free_times == correct_result

#Gap between event 1 and 2
def test2():
    start_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    end_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    event1 = {'start':arrow.get('2015-12-08T10:30:00-08:00'), 'end':arrow.get('2015-12-08T11:30:00-08:00')}
    event2 = {'start':arrow.get('2015-12-08T13:00:00-08:00'), 'end':arrow.get('2015-12-08T14:00:00-08:00')}
    events_list = [event1, event2]
    free_times = str(main.freeTimes(events_list,start_date,end_date))
    correct_result = ["[[<Arrow [2015-12-08T09:00:00-08:00]>, <Arrow [2015-12-08T10:30:00-08:00]>], ",
            "[<Arrow [2015-12-08T11:30:00-08:00]>, <Arrow [2015-12-08T13:00:00-08:00]>], ",
            "[<Arrow [2015-12-08T14:00:00-08:00]>, <Arrow [2015-12-08T17:00:00-08:00]>]]"]
    correct_result = ''.join(correct_result)
    print(correct_result)
    print("-------------------------------------------")
    print(free_times)
    assert free_times == correct_result

#Event 1 and event 2 are the same
def test3():
    start_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    end_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    event1 = {'start':arrow.get('2015-12-08T13:00:00-08:00'), 'end':arrow.get('2015-12-08T14:00:00-08:00')}
    event2 = {'start':arrow.get('2015-12-08T13:00:00-08:00'), 'end':arrow.get('2015-12-08T14:00:00-08:00')}
    events_list = [event1, event2]
    free_times = str(main.freeTimes(events_list,start_date,end_date))
    correct_result = ["[[<Arrow [2015-12-08T09:00:00-08:00]>, <Arrow [2015-12-08T13:00:00-08:00]>], ",
            "[<Arrow [2015-12-08T14:00:00-08:00]>, <Arrow [2015-12-08T17:00:00-08:00]>]]"]
    correct_result = ''.join(correct_result)
    print(correct_result)
    print("-------------------------------------------")
    print(free_times)
    assert free_times == correct_result

#Event 1 end time is the same as event 2's start time
def test4():
    start_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    end_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    event1 = {'start':arrow.get('2015-12-08T10:30-08:00'), 'end':arrow.get('2015-12-08T11:30:00-08:00')}
    event2 = {'start':arrow.get('2015-12-08T11:30-08:00'), 'end':arrow.get('2015-12-08T12:30:00-08:00')}
    events_list = [event1, event2]
    free_times = str(main.freeTimes(events_list,start_date,end_date))
    correct_result = ["[[<Arrow [2015-12-08T09:00:00-08:00]>, <Arrow [2015-12-08T10:30:00-08:00]>], ",
            "[<Arrow [2015-12-08T12:30:00-08:00]>, <Arrow [2015-12-08T17:00:00-08:00]>]]"]
    correct_result = ''.join(correct_result)
    print(correct_result)
    print("-------------------------------------------")
    print(free_times)
    assert free_times == correct_result

#Event 1 end time after event 2 start time. Slight overlap!
def test5():
    start_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    end_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    event1 = {'start':arrow.get('2015-12-08T10:30-08:00'), 'end':arrow.get('2015-12-08T11:30:00-08:00')}
    event2 = {'start':arrow.get('2015-12-08T11:00-08:00'), 'end':arrow.get('2015-12-08T12:30:00-08:00')}
    events_list = [event1, event2]
    free_times = str(main.freeTimes(events_list,start_date,end_date))
    correct_result = ["[[<Arrow [2015-12-08T09:00:00-08:00]>, <Arrow [2015-12-08T10:30:00-08:00]>], ",
            "[<Arrow [2015-12-08T12:30:00-08:00]>, <Arrow [2015-12-08T17:00:00-08:00]>]]"]
    correct_result = ''.join(correct_result)
    print(correct_result)
    print("-------------------------------------------")
    print(free_times)
    assert free_times == correct_result

#Event 1 start and event 2 start at same time. Event 1 ends early
def test6():
    start_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    end_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    event1 = {'start':arrow.get('2015-12-08T11:00-08:00'), 'end':arrow.get('2015-12-08T11:30:00-08:00')}
    event2 = {'start':arrow.get('2015-12-08T11:00-08:00'), 'end':arrow.get('2015-12-08T12:30:00-08:00')}
    events_list = [event1, event2]
    free_times = str(main.freeTimes(events_list,start_date,end_date))
    correct_result = ["[[<Arrow [2015-12-08T09:00:00-08:00]>, <Arrow [2015-12-08T11:00:00-08:00]>], ",
            "[<Arrow [2015-12-08T12:30:00-08:00]>, <Arrow [2015-12-08T17:00:00-08:00]>]]"]
    correct_result = ''.join(correct_result)
    print(correct_result)
    print("-------------------------------------------")
    print(free_times)
    assert free_times == correct_result

#Event 1 start and event 2 start at same time. Event 2 ends early
def test7():
    start_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    end_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    event1 = {'start':arrow.get('2015-12-08T11:00-08:00'), 'end':arrow.get('2015-12-08T12:30:00-08:00')}
    event2 = {'start':arrow.get('2015-12-08T11:00-08:00'), 'end':arrow.get('2015-12-08T11:30:00-08:00')}
    events_list = [event1, event2]
    free_times = str(main.freeTimes(events_list,start_date,end_date))
    correct_result = ["[[<Arrow [2015-12-08T09:00:00-08:00]>, <Arrow [2015-12-08T11:00:00-08:00]>], ",
            "[<Arrow [2015-12-08T12:30:00-08:00]>, <Arrow [2015-12-08T17:00:00-08:00]>]]"]
    correct_result = ''.join(correct_result)
    print(correct_result)
    print("-------------------------------------------")
    print(free_times)
    assert free_times == correct_result

#Event 2 is fully engulfed by event 1.
def test8():
    start_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    end_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    event1 = {'start':arrow.get('2015-12-08T11:00-08:00'), 'end':arrow.get('2015-12-08T14:00:00-08:00')}
    event2 = {'start':arrow.get('2015-12-08T12:00-08:00'), 'end':arrow.get('2015-12-08T13:00:00-08:00')}
    events_list = [event1, event2]
    free_times = str(main.freeTimes(events_list,start_date,end_date))
    correct_result = ["[[<Arrow [2015-12-08T09:00:00-08:00]>, <Arrow [2015-12-08T11:00:00-08:00]>], ",
            "[<Arrow [2015-12-08T14:00:00-08:00]>, <Arrow [2015-12-08T17:00:00-08:00]>]]"]
    correct_result = ''.join(correct_result)
    print(correct_result)
    print("-------------------------------------------")
    print(free_times)
    assert free_times == correct_result

#Event 1 starts before 2 but both end at the same time
def test9():
    start_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    end_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    event1 = {'start':arrow.get('2015-12-08T10:00-08:00'), 'end':arrow.get('2015-12-08T12:00:00-08:00')}
    event2 = {'start':arrow.get('2015-12-08T11:00-08:00'), 'end':arrow.get('2015-12-08T12:00:00-08:00')}
    events_list = [event1, event2]
    free_times = str(main.freeTimes(events_list,start_date,end_date))
    correct_result = ["[[<Arrow [2015-12-08T09:00:00-08:00]>, <Arrow [2015-12-08T10:00:00-08:00]>], ",
            "[<Arrow [2015-12-08T12:00:00-08:00]>, <Arrow [2015-12-08T17:00:00-08:00]>]]"]
    correct_result = ''.join(correct_result)
    print(correct_result)
    print("-------------------------------------------")
    print(free_times)
    assert free_times == correct_result

#more realistic case with three events
def test10():
    start_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    end_date = arrow.get('2015-12-08T00:00:00-08:00').isoformat()
    event1 = {'start':arrow.get('2015-12-08T10:30-08:00'), 'end':arrow.get('2015-12-08T11:30:00-08:00')}
    event2 = {'start':arrow.get('2015-12-08T13:00-08:00'), 'end':arrow.get('2015-12-08T14:00:00-08:00')}
    event3 = {'start':arrow.get('2015-12-08T13:30:00-08:00'), 'end':arrow.get('2015-12-08T14:30:00-08:00')}
    events_list = [event1, event2, event3]
    free_times = str(main.freeTimes(events_list,start_date,end_date))
    correct_result = ["[[<Arrow [2015-12-08T09:00:00-08:00]>, <Arrow [2015-12-08T10:30:00-08:00]>], ",
            "[<Arrow [2015-12-08T11:30:00-08:00]>, <Arrow [2015-12-08T13:00:00-08:00]>], ",
            "[<Arrow [2015-12-08T14:30:00-08:00]>, <Arrow [2015-12-08T17:00:00-08:00]>]]"]
    correct_result = ''.join(correct_result)
    print(correct_result)
    print("-------------------------------------------")
    print(free_times)
    assert free_times == correct_result
