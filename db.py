import time
import asyncio
import sqlite3
import contextlib

async def gen():
    for i in range(0, 2):
        yield '0->2'
        await asyncio.sleep(0.5)
        yield '2->1'
        await asyncio.sleep(2.0)
        yield '1->4'
        await asyncio.sleep(0.5)
        yield '4->0'
        await asyncio.sleep(2.0)


async def empty_queue(queue: asyncio.Queue):
    while True:
        # create connection that lasts until timeout
        record = await queue.get()
        print('got first record', record)
        with contextlib.closing(sqlite3.connect('test.db')) as con:
            while True:
                con.execute('INSERT INTO events(date, raw, statefrom, stateto) VALUES(?,?,?,?)', record)
                try:
                    record = await asyncio.wait_for(queue.get(), timeout=0.8)
                    print('got another record', record)
                except asyncio.TimeoutError:
                    print('timeout')
                    break
            con.commit()


async def fill_queue(queue: asyncio.Queue):
    while True:
        raw: str = yield
        vals = raw.split('->') if '->' in raw else 2*[None]
        record = (time.time(), raw, vals)
        await queue.put(record)


async def main():
    print('creating table...')
    with contextlib.closing(sqlite3.connect('test.db')) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS events
                (date INTEGER, raw TEXT, statefrom INTEGER, stateto INTEGER)''')

    queue = asyncio.Queue()

    task = asyncio.create_task(empty_queue(queue))

    filler = fill_queue(queue)
    await filler.asend(None)

    async for val in gen():
        await filler.asend(val)

    task.cancel()


if __name__ == '__main__':
    asyncio.run(main())
