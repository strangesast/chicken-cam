import serial
import time
from datetime import datetime, timedelta
import sqlite3
import contextlib
from astral import Astral

astral = Astral()
city = astral['Buffalo']

OPEN = 1
CLOSE = 0

def get_commands(start=datetime.now(), count=7):
    for i in range(0, count):
        date = start + timedelta(days=i)
        # floor date (unnecessary)
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        # astral info for city & date
        s = city.sun(local=False, date=date) # by default use current date, utc time
        # utc sunrise / sunset
        times = s['sunrise'], s['sunset']
        # use local timezone
        times = [t.astimezone(tz=None) for t in times]
        # shift by an hour
        times = [t + timedelta(hours=1) for t in times]
        # what do at time
        data = zip([OPEN, CLOSE], times)
        # only produce commands after now
        yield from filter(lambda v: v[1].replace(tzinfo=None) > start, data)


with contextlib.closing(sqlite3.connect('test.db')) as con:
    now = int(datetime.now().timestamp())
    records = [(value, int(date.timestamp()), 'scheduled', now) for value, date in get_commands()]
    con.executemany('insert into requests (value, date, textstate, created) values (?,?,?,?)', records)
    con.commit()

#print('opening')
#with serial.Serial('/dev/ttyACM0', 9600, timeout=1) as ser:
#    print('reading')
#    print(ser.readline())
#    print('writing')
#    ser.write(b'1');
