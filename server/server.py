import os
import asyncio
import logging
import aiosqlite
from aiohttp import web
from datetime import datetime, timedelta
from systemd.journal import JournalHandler


QUERY_DEFAULTS = {
    'offset': 0,
    'limit': 100,
    'range': 14
}

SCHEMAS = [
  'CREATE TABLE IF NOT EXISTS events_changes (date INTEGER, raw TEXT, fromstate INTEGER, tostate INTEGER)',
  'CREATE TABLE IF NOT EXISTS events_states (date INTEGER, raw TEXT, currentstate INTEGER, topsensor INTEGER, sidesensor INTEGER, bottomsensor INTEGER)',
  'CREATE TABLE IF NOT EXISTS events_unknown (date INTEGER, raw TEXT)',
  'CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, value INTEGER, date INTEGER UNIQUE, textstate TEXT, completed INTEGER, created INTEGER, createdgroup INTEGER)'
]

routes = web.RouteTableDef()

# get changes history
@routes.get('/states')
async def get_states(request: web.Request):
    db: aiosqlite.Connection = request.app['db']
    offset, limit, _range = [int(v) if (v := request.rel_url.query.get(s, '')).isdigit()
            else QUERY_DEFAULTS[s] for s in ['offset', 'limit', 'range']]
    # by default today - this week - last week
    gt = int((datetime.now() - timedelta(days=14)).timestamp())
    keys = ['date','topsensor','sidesensor','bottomsensor']
    async with db.execute('SELECT {} FROM events_states'.format(','.join(keys))) as cursor:
        records = []
        last = None
        async for d,*v in cursor:
            if last != v:
                last = v
                d = datetime.fromtimestamp(d).isoformat()
                records.append(dict(zip(keys,[d]+v)))
    return web.json_response({'records': records})


@routes.get('/changes')
async def get_changes(request: web.Request):
    db: aiosqlite.Connection  = request.app['db']
    records = []
    keys = ['date','fromstate','tostate']
    async with db.execute('SELECT {},{},{} FROM events_changes'.format(*keys)) as cursor:
        async for d,*v in cursor:
            d = datetime.fromtimestamp(d).isoformat()
            records.append(dict(zip(keys, [d]+v)))
    return web.json_response({'records': records})


@routes.get('/requests')
async def get_requests(request: web.Request):
    requests = []
    db = request.app['db']
    keys = ['date','completed','created','id','value','textstate']
    async with db.execute('SELECT {} FROM requests'.format(','.join(keys))) as cursor:
        async for row in cursor:
            values = [datetime.fromtimestamp(d).isoformat() if d else None for d in row[0:3]] + list(row[3:])
            requests.append(dict(zip(keys,values)))

    return web.json_response({'requests': requests})


@routes.post('/requests')
async def post_requests(request: web.Request):
    data = await request.post()
    date, value = data['when'], data['value']
    try:
        date = datetime.fromisoformat(date)
    except:
        return web.HTTPUnprocessableEntity(body='invalid when date')
    if value != '0' and value != '1':
        return web.HTTPUnprocessableEntity(body='invalid value')

    now = int(datetime.now().timestamp())
    record = [value, date, 'scheduled', now]
    r = await con.execute('insert into requests (value, date, textstate, created) values (?,?,?,?)', record)
    print(r)

    return web.json_response({'record': record})


@routes.get('/')
async def index(request):
    return web.FileResponse('./index.html')


async def init_db(db):
    for sql in SCHEMAS:
        await db.execute(sql)
    await db.commit()


def split_nums(s, delim):
    return [int(v) if v.isdigit() else None for v in s.split(delim)]


async def reader_handler(reader, db: aiosqlite.Connection):
    while True:
        new = False
        while True:
            try:
                b = await asyncio.wait_for(reader.readline(), timeout=5)
            except asyncio.TimeoutError:
                break
            date = int(datetime.now().timestamp())
            raw = b.decode('utf8', errors='ignore').strip()
            if '->' in raw and len(values := split_nums(raw, '->')) == 2:
                # fromstate, tostate
                q = con.execute('''INSERT INTO events_changes
                        (date,raw,fromstate,tostate) VALUES (?,?,?,?)''', (date, raw, *values))
            if '|' in raw and len(values := split_nums(raw, '|')) == 4:
                # currentstate, topsensor, sidesensor, bottomsensor
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
                (int(date.timestamp()), 'scheduled')) as cursor:
            command = await cursor.fetchone()

        if command:
            await queue.put(command)

        await asyncio.sleep(timeout)


async def main():
    #log = logging.getLogger()
    #log.addHandler(JournalHandler())
    #log.setLevel(logging.DEBUG)


    db_file = os.environ.get('DB_FILE', 'test.db')
    print(f'{db_file=}')
    db = await aiosqlite.connect(db_file)
    await init_db(db)

    reader, writer = await asyncio.open_connection('127.0.0.1',
            os.environ.get('MONITOR_PORT', '3333'))

    queue = asyncio.Queue()

    app = web.Application()
    app['db'] = db
    app.add_routes(routes)
    app.router.add_static('/', dirname(realpath(__file__)))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 3000)
    await site.start()

    await reader.read(12) # extra bullshit from ser2net
    try:
        await asyncio.gather(
            reader_handler(reader, db),
            writer_handler(writer, db, queue),
            poller(db, queue))

    finally:
        await runner.cleanup()
        await db.close()


if __name__ == '__main__':
    asyncio.run(main())
