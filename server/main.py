import os
import sys
import asyncio
import logging
import aiosqlite
from aiohttp import web
from contextvars import ContextVar
from datetime import datetime, timedelta


QUERY_DEFAULTS = {
    'offset': 0,
    'limit': 100,
    'range': 14
}

SCHEMAS = [
  'CREATE TABLE IF NOT EXISTS events_changes (date INTEGER, raw TEXT, fromstate INTEGER, tostate INTEGER)',
  'CREATE TABLE IF NOT EXISTS events_states (date INTEGER, raw TEXT, currentstate INTEGER, topsensor INTEGER, sidesensor INTEGER, bottomsensor INTEGER)',
  'CREATE TABLE IF NOT EXISTS events_unknown (date INTEGER, raw TEXT)',
  'CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, value INTEGER, date INTEGER UNIQUE, textstate TEXT, completed INTEGER, created INTEGER, createdgroup INTEGER, reason TEXT)'
]

LOG_VAR = ContextVar('log')

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
        date = int(datetime.timestamp())
    except:
        return web.HTTPUnprocessableEntity(body='invalid when date')
    if value != '0' and value != '1':
        return web.HTTPUnprocessableEntity(body='invalid value')

    now = int(datetime.now().timestamp())
    record = [value, date, 'scheduled', now]
    value = int(value)
    r = await request.app['db'].execute('insert into requests (value, date, textstate, created) values (?,?,?,?)', record)

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
    log = LOG_VAR.get()
    while True:
        while True:
            log.debug('waiting for serial line')
            try:
                b = await asyncio.wait_for(reader.readline(), timeout=5)
            except asyncio.TimeoutError:
                log.debug('serial timeout')
                break
            date = int(datetime.now().timestamp())
            raw = b.decode('utf8', errors='ignore').strip()
            log.debug(f'got line: {raw}')
            if '->' in raw and len(values := split_nums(raw, '->')) == 2:
                log.debug(f'is change.  values: {values}')
                # fromstate, tostate
                await db.execute('''INSERT INTO events_changes
                        (date,raw,fromstate,tostate) VALUES (?,?,?,?)''', (date, raw, *values))
                await db.commit()
            if '|' in raw and len(values := split_nums(raw, '|')) == 4:
                log.debug(f'is state.  values: {values}')
                # currentstate, topsensor, sidesensor, bottomsensor
                await db.execute('''INSERT INTO events_states
                        (date,raw,currentstate,topsensor,sidesensor,bottomsensor)
                        VALUES (?,?,?,?,?,?)''', (date, raw, *values))
                await db.commit()
            else:
                log.debug(f'is unknown')
                await db.execute('''INSERT INTO events_unknown
                        (date,raw) VALUES (?,?)''', (date, raw))
                await db.commit()


async def writer_handler(writer, db: aiosqlite.Connection, queue: asyncio.Queue):
    log = LOG_VAR.get()
    while True:
        reason = None
        try:
            log.debug('got command')
            _id, value = await queue.get()
            b = str(value).encode('utf8')
            await writer.write(b)
            textstate = 'completed'
        except Exception as e:
            textstate = 'failed'
            reason = str(e)
        log.debug(f'command {value=} {textstate=} {reason=}')
        date = int(datetime.now().timestamp())
        await db.execute('''UPDATE requests SET textstate = ?, completed = ?, reason = ?
                WHERE id = ?''', (textstate, date, reason, _id))


async def poller(db: aiosqlite.Connection, queue: asyncio.Queue, timeout=60):
    log = LOG_VAR.get()
    log.debug(f'poller running with {timeout=}')
    while True:
        date = datetime.now() - timedelta(minutes=10)
        log.debug(f'checking for commands')
        async with db.execute('SELECT id, value FROM requests WHERE date < ? AND textstate = ?',
                (int(date.timestamp()), 'scheduled')) as cursor:
            command = await cursor.fetchone()

        if command:
            log.debug(f'got {command=}')
            await queue.put(command)
        else:
            log.debug(f'no commands')


        await asyncio.sleep(timeout)


async def main():
    log = logging.getLogger()
    try:
        from systemd.journal import JournalHandler
        log.addHandler(JournalHandler())
    except ImportError:
        from logging import StreamHandler
        log.addHandler(StreamHandler(sys.stdout))

    log.setLevel(logging.DEBUG)
    LOG_VAR.set(log)

    db_file = os.environ.get('DB_FILE', 'test.db')

    log.info('using db file {}'.format(db_file))
    db = await aiosqlite.connect(db_file)
    await init_db(db)

    MONITOR_SOCKET_HOST = '127.0.0.1'
    MONITOR_SOCKET_PORT = os.environ.get('MONITOR_PORT', '3333')
    log.info('connecting to serial-socket {}:{}'.format(MONITOR_SOCKET_HOST,
        MONITOR_SOCKET_PORT))
    reader, writer = await asyncio.open_connection(MONITOR_SOCKET_HOST,
            MONITOR_SOCKET_PORT)

    queue = asyncio.Queue()

    app = web.Application()
    app['db'] = db
    app.add_routes(routes)
    #app.router.add_static('/', os.path.dirname(os.path.realpath(__file__)))
    
    runner = web.AppRunner(app)
    await runner.setup()
    API_HOST, API_PORT = '0.0.0.0', 3000
    log.info('hosting api at {}:{}'.format(API_HOST, API_PORT))
    site = web.TCPSite(runner, API_HOST, API_PORT)
    await site.start()

    try:
        #log.info('waiting on bs header info')
        #b = await reader.read(12) # extra bullshit from ser2net
        #log.info(f'got it {b=}')

        await asyncio.gather(
            reader_handler(reader, db),
            writer_handler(writer, db, queue),
            poller(db, queue))

    finally:
        writer.close()
        await writer.wait_closed()
        await runner.cleanup()
        await db.close()


if __name__ == '__main__':
    asyncio.run(main())
