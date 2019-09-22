#!/usr/bin/python3
import time
from datetime import timedelta, datetime
import serial
import schedule
from astral import Astral

astral = Astral()
city = astral['Buffalo']

def send(what):
    print('sending...')
    with serial.Serial('/dev/ttyACM0', 9600, timeout=10) as ser:
        ser.readline() # may read 'ready', or not
        ser.write(what)

    return schedule.CancelJob


def sched():
    s = city.sun(local=False) # by default use current date, utc time
    times = [(b'1', s['sunrise']), (b'0', s['sunset'] + timedelta(minutes=60))]
    #times = [(b'1', datetime.now() + timedelta(seconds=60)), (b'0', s['sunset'])]
    
    # add a few retries after the initial opening
    times = [(val, (base + timedelta(minutes=5*i)).strftime('%H:%M')) for val, base in times for i in range(3)]

    for val, time in times:
        print('time', time, val)
        schedule.every().day.at(time).do(send, what=val)


if __name__ == '__main__':
    schedule.every().day.at('05:00').do(sched)
    sched()
    
    while True:
        schedule.run_pending()
        print(schedule.next_run())
        time.sleep(60)
