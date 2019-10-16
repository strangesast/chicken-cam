import os
import sys
import time
from serial import Serial
import sqlite3
import logging
import contextlib
from systemd.journal import JournalHandler

from common.db_sync import init_db

CLOSE = b'0'
OPEN = b'1'

if __name__ == '__main__':
    #logging.basicConfig(filename='coopdoor-serial.log',level=logging.DEBUG)
    #logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    log = logging.getLogger()
    log.addHandler(JournalHandler())
    log.setLevel(logging.DEBUG)

    PORT = os.environ.get('PORT') or '/dev/ttyACM0'
    DB_FILE = os.environ.get('DB_FILE') or os.path.join(os.path.dirname(__file__), '../test.db');
    TIMEOUT = 60

    log.info('Using serial port {}'.format(PORT))
    log.info('Using db file {}'.format(DB_FILE))
    with Serial(PORT, 9600, timeout=TIMEOUT) as ser, contextlib.closing(sqlite3.connect(DB_FILE)) as con:
        log.debug('Creating necessary tables')
        init_db_sync(db)
        lastCheck = 0;
        while True:
            records = []
            hasupdate = False
            log.debug('Waiting {}s for serial data'.format(TIMEOUT))
            while (time.time() - lastCheck) < TIMEOUT:
                raw = ser.readline().decode('utf8').strip()
                if not raw:
                    break
                hasupdate = True
                date = int(time.time())
                if '->' in raw:
                    # fromstate, tostate
                    values = [int(v) if v.isdigit() else None for v in raw.split('->')]
                    con.execute('INSERT INTO events_changes (date,raw,fromstate,tostate) VALUES (?,?,?,?)', (date, raw, *values))
                elif '|' in raw:
                    # currentstate, topsensor, sidesensor, bottomsensor
                    values = [int(v) if v.isdigit() else None for v in raw.split('|')]
                    con.execute('INSERT INTO events_states (date,raw,currentstate,topsensor,sidesensor,bottomsensor) VALUES (?,?,?,?,?,?)', (date, raw, *values))
                else:
                    con.execute('INSERT INTO events_unknown (date,raw) VALUES (?,?)', (date, raw))
    
            if hasupdate:
                con.commit()
            
            log.debug('Checking for requests')
            lastCheck = time.time()
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
