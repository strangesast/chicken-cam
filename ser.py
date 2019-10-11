import time
import serial
import sqlite3
import contextlib

CLOSE = b'0'
OPEN = b'1'

with serial.Serial('/dev/ttyACM0', 9600, timeout=60) as ser, contextlib.closing(sqlite3.connect('test.db')) as con:
    con.execute('CREATE TABLE IF NOT EXISTS events (date INTEGER, raw TEXT, fromstate INTEGER, tostate INTEGER)')
    con.execute('CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, value INTEGER, date INTEGER, textstate TEXT, completed INTEGER, created INTEGER)')
    con.commit()
    while True:
        records = []
        print('waiting')
        while True:
            line = ser.readline()
            if not line:
                break
            line = line.decode('utf8')
            val = line.split('->') if '->' in line else 2*[None]
            records.append((int(time.time()), line, *val))

        if len(records) > 0:
            con.executemany('INSERT INTO events VALUES (?,?,?,?)', records)
            con.commit()
        
        print('checking')
        cur = con.cursor()
        cur.execute('SELECT id, value FROM requests WHERE date < ? AND textstate = ?', (int(time.time()), 'scheduled'))
        command = cur.fetchone()
        if command:
            _id, val = command
            print('writing request {} ({})'.format(_id, 'OPEN' if val == 1 else 'CLOSE'))
            ser.write(OPEN if val == 1 else CLOSE)
            ser.flush()
            con.execute('UPDATE requests SET textstate = ?, completed = ? WHERE id = ?', ('completed', int(time.time()), _id))
            con.commit()
