import serial
import time
import sqlite3
import contextlib

with contextlib.closing(sqlite3.connect('test.db')) as con:
    now = time.time()
    con.execute('insert into requests (value, date, textstate, created) values (?,?,?,?)', [0, now, 'scheduled', now])
    con.commit()

print('opening')
with serial.Serial('/dev/ttyACM0', 9600, timeout=1) as ser:
    print('reading')
    print(ser.readline())
    print('writing')
    ser.write(b'1');
