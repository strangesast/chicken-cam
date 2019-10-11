#!/usr/bin/python3
import time
from datetime import timedelta, datetime, timezone
import serial
import schedule
from astral import Astral

astral = Astral()
city = astral['Buffalo']

def send(what):
    print('sending...')
    with serial.Serial('/dev/ttyACM0', 9600, timeout=10) as ser:
        ser.read(100000) # may read 'ready', or not
        ser.write(what)

    return schedule.CancelJob


def get_times():
    s = city.sun(local=False) # by default use current date, utc time

    times = s['sunrise'], s['sunset']

    times = [t + timedelta(minutes=45) for t in times]

    now = datetime.now(timezone.utc) + timedelta(minutes=1)
    times = [t if t > now else now for t in times]

    times = [t.astimezone(tz=None) for t in times]

    times = [t.strftime('%H:%M') for t in times]

    if len(set(times)) > 1:
        times = list(zip(times, (1, 0)))
    else:
        times = [(times[0], 0)]

    #print([(t.strftime('%m/%d/%Y %H:%M'), v) for t, v in times])

    #times = [(b'1', s['sunrise']), (b'0', s['sunset'] + timedelta(minutes=60))]
    #times = [(b'1', datetime.now() + timedelta(seconds=60)), (b'0', s['sunset'])]
    
    # add a few retries after the initial opening
    #times = [(val, (base + timedelta(minutes=5*i)).strftime('%H:%M')) for val, base in times for i in range(3)]

    return times


def sched():
    for time, val in get_times():
        print('time', time, val)
        schedule.every().day.at(time).do(send, what=val)


if __name__ == '__main__':
    schedule.every().day.at('00:00').do(sched)
    sched()
    
    while True:
        schedule.run_pending()
        print(schedule.next_run())
        time.sleep(60)
