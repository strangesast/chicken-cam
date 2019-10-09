from datetime import datetime, timedelta, timezone
import time
from astral import Astral
import schedule
from freezegun import freeze_time


CLOSE = 0
OPEN = 1

astral = Astral()
city = astral['Buffalo']

def pretty(t):
  return t.strftime('%I:%M %p')


def get_times():
    s = city.sun(local=False)

    # get sunrise / sunset
    times = s['sunrise'], s['sunset']

    # offset by a bit as sunrise / sunset is still pretty dark / light
    offset = timedelta(minutes=45)
    times = [t + offset for t in times]

    # open or close now if past sunrise / sunset
    now = datetime.now(timezone.utc)
    times = [t if t > now else now for t in times]

    # adjust timezone to local
    times = [t.astimezone(tz=None) for t in times]
    o, c = [t.strftime('%H:%M') for t in times]
    n = pretty(datetime.now().astimezone(tz=None))
    print(f'started: {n}: open {o}, close {c}')

    if len(set(times)) == 1:
        arr = [(t, CLOSE) for t in times[1:]]
    else:
        arr = list(zip(times, (OPEN, CLOSE)))

    return arr;

with freeze_time("2019-09-21 23:49"): # utc
    val = get_times()
    a = [(pretty(t), v) for t, v in val]
    b = [('06:49 PM', 0)]
    print('a', a)
    print('b', b)
    assert a == b

with freeze_time("2012-09-21 21:49"): # utc
    val = get_times()
    a = [(pretty(t), v) for t, v in val]
    b = [('04:49 PM', 1), ('05:49 PM', 0)]
    assert a == b

with freeze_time("2012-09-21 13:49"): # utc
    val = get_times()
    print([(pretty(t), v) for t, v in val])
    print([('08:49 AM', 1), ('05:34 PM', 0)])

with freeze_time("2012-09-21 3:49"): # utc
    val = get_times()
    print([(pretty(t), v) for t, v in val])
    #[('08:13 AM', 1), ('05:34 PM', 0)]


#loc.sun(datetime.now())

    

#while True:
#    schedule.run_pendng()
#    time.sleep(1)
