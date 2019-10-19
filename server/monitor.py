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

def reader_handler(reader):
    while True:
        new = False
        while True:
            try:
                raw = await asyncio.wait_for(reader.readline(), timeout=5)
            except asyncio.TimeoutError:
                break
            date = datetime.now()
            if '->' in raw:
                # fromstate, tostate
                values = [int(v) if v.isdigit() else None for v in raw.split('->')]
                q = con.execute('''INSERT INTO events_changes
                (date,raw,fromstate,tostate) VALUES (?,?,?,?)''', (date, raw, *values))
            elif '|' in raw:
                # currentstate, topsensor, sidesensor, bottomsensor
                values = [int(v) if v.isdigit() else None for v in raw.split('|')]
                q = db.execute('''INSERT INTO events_states
                (date,raw,currentstate,topsensor,sidesensor,bottomsensor)
                VALUES (?,?,?,?,?,?)''', (date, raw, *values))
            else:
                q = db.execute('''INSERT INTO events_unknown
                (date,raw) VALUES (?,?)''', (date, raw))
            new = True
            await q

        if new:
            await db.commit()
        # insert line

def writer_handler(writer):
    while True:
        _id, value = await queue.get()
        b = value.encode('utf8')
        try:
            await writer.write(b)
            textstate = 'completed'
        except:
            textstate = 'failed'
        await db.execute('''UPDATE requests SET textstate = ?, completed = ?
        WHERE id = ?''', (textstate, date, _id))


if __name__ == '__main__':
    log = logging.getLogger()
    log.addHandler(JournalHandler())
    log.setLevel(logging.DEBUG)

    db = await aiosqlite.connect(os.environ.get('DB_FILE', 'test.db'))
    await init_db(db)

    reader, writer = await asyncio.open_connection('127.0.0.1',
            os.environ.get('MONITOR_PORT', '3333'))

    await asyncio.gather(reader_handler(reader), writer_handler)
