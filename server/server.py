import os
import sys
import asyncio
import logging
import aiosqlite
from datetime import datetime
from systemd.journal import JournalHandler

from common import init_db


async def reader_handler(reader, db: aiosqlite.Connection):
    while True:
        new = False
        while True:
            try:
                b = await asyncio.wait_for(reader.readline(), timeout=5)
            except asyncio.TimeoutError:
                break
            date = datetime.now()
            raw = b.decode('utf8', errors='ignore').strip()
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


async def writer_handler(writer, db: aiosqlite.Connection, queue: asyncio.Queue):
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


async def poller(db: aiosqlite.Connection, queue: asyncio.Queue, timeout=60):
    while True:
        date = datetime.now()
        async with db.execute('SELECT id, value FROM requests WHERE date < ? AND textstate = ?',
                (int(datetime.timestamp()), 'scheduled')) as cursor:
            command = await cursor.fetchone()

        if command:
            await queue.put(command)

        await asyncio.sleep(timeout)


async def main():
    log = logging.getLogger()
    log.addHandler(JournalHandler())
    log.setLevel(logging.DEBUG)

    db = await aiosqlite.connect(os.environ.get('DB_FILE', 'test.db'))
    await init_db(db)

    reader, writer = await asyncio.open_connection('127.0.0.1',
            os.environ.get('MONITOR_PORT', '3333'))

    queue = asyncio.Queue()

    await reader.read(12) # greeting? extra bullshit
    await asyncio.gather(
        reader_handler(reader, db),
        writer_handler(writer, db, queue),
        poller(db, queue))


if __name__ == '__main__':
    asyncio.run(main())
