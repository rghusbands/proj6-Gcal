
import arrow
import datetime
from dateutil import tz

import main

#11/11/2015 nighttime times
morning_start = arrow.get('11/11/2015 00:00', 'MM/DD/YYYY HH:mm')
morning_end = arrow.get('11/11/2015 09:00', 'MM/DD/YYYY HH:mm')
night_start = arrow.get('11/11/2015 17:00', 'MM/DD/YYYY HH:mm')
night_end = arrow.get('11/12/2015 00:00', 'MM/DD/YYYY HH:mm')

night_event = [{'start':morning_start, 'end':morning_end},
                {'start':night_start, 'end':night_end}
              ]

#overlapping times
date1 = arrow.get('11/11/2015 10:00', 'MM/DD/YYYY HH:mm')
date2 = arrow.get('11/11/2015 11:00', 'MM/DD/YYYY HH:mm')
date3 = arrow.get('11/11/2015 10:30', 'MM/DD/YYYY HH:mm')
date4 = arrow.get('11/11/2015 11:30', 'MM/DD/YYYY HH:mm')

#engulfed event
date5 = arrow.get('11/11/2015 18:40', 'MM/DD/YYYY HH:mm')
date6 = arrow.get('11/11/2015 18:40', 'MM/DD/YYYY HH:mm')
date7 = arrow.get('11/11/2015 18:40', 'MM/DD/YYYY HH:mm')
date8 = arrow.get('11/11/2015 18:40', 'MM/DD/YYYY HH:mm')
date9 = arrow.get('11/11/2015 18:40', 'MM/DD/YYYY HH:mm')
date10 = arrow.get('11/11/2015 18:40', 'MM/DD/YYYY HH:mm')

event1 = [{'start':date1, 'end':date2},
          {'start':date3, 'end':date4},
          {'start':date5, 'end':date6}
         ]



def test1():
    print("")


#currently failing test
def test2():
    print("lol")
    freeTimes(event1)
    print(event1)
    string = "lol"
    assert()


