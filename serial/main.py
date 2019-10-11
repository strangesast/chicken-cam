import os
import time
import serial
import sqlite3
import logging
import contextlib
from systemd.journal import JournalHandler

CLOSE = b'0'
OPEN = b'1'

if __name__ == '__main__':
    #logging.basicConfig(filename='coopdoor-serial.log',level=logging.DEBUG)
    log = logging.getLogger()
    log.addHandler(JournalHandler())
    log.setLevel(logging.DEBUG)

    PORT = os.environ.get('PORT') or '/dev/ttyACM0'
    DB_FILE = os.environ.get('DB_FILE') or os.path.join(os.path.dirname(__file__), '../test.db');
    TIMEOUT = 60

    log.info('Using serial port {}'.format(PORT))
    log.info('Using db file {}'.format(DB_FILE))
    with serial.Serial(PORT, 9600, timeout=TIMEOUT) as ser, contextlib.closing(sqlite3.connect(DB_FILE)) as con:
        log.debug('Creating necessary tables')
        con.execute('CREATE TABLE IF NOT EXISTS events (date INTEGER, raw TEXT, fromstate INTEGER, tostate INTEGER)')
        con.execute('CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, value INTEGER, date INTEGER UNIQUE, textstate TEXT, completed INTEGER, created INTEGER)')

        con.commit()
        while True:
            records = []
            log.debug('Waiting {}s for serial data'.format(TIMEOUT))
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
            
            log.debug('Checking for requests')
            cur = con.cursor()
            cur.execute('SELECT id, value FROM requests WHERE date < ? AND textstate = ?', (int(time.time()), 'scheduled'))
            command = cur.fetchone()
            if command:
                log.debug('Got request')
                _id, val = command
                log.info('writing request {} ({})'.format(_id, 'OPEN' if val == 1 else 'CLOSE'))
                ser.write(OPEN if val == 1 else CLOSE)
                ser.flush()
                con.execute('UPDATE requests SET textstate = ?, completed = ? WHERE id = ?', ('completed', int(time.time()), _id))
                con.commit()
