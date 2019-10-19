import os
from os.path import dirname, realpath, normpath, join
import json
import asyncio
import aiosqlite
from aiohttp import web
from datetime import datetime, timedelta
from pathlib import Path

from common import init_db


routes = web.RouteTableDef()


# list of requests
#   default some number, some range

# create request
#   extract value, when
#   default now

# get state history


DEFAULTS = {
    'offset': 0,
    'limit': 100,
    'range': 14
}


# get changes history
@routes.get('/state')
async def get_states(request: web.Request):
    db: aiosqlite.Connection = request.app['db']
    offset, limit, _range = [int(v) if (v := request.rel_url.query.get(s, '')).isdigit()
            else DEFAULTS[s] for s in ['offset', 'limit', 'range']]
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
async def get_requests(request):
    requests = []
    db = request.app['db']
    keys = ['date','completed','created','id','value','textstate']
    async with db.execute('SELECT {} FROM requests'.format(','.join(keys))) as cursor:
        async for row in cursor:
            values = [datetime.fromtimestamp(d).isoformat() if d else None for d in row[0:3]] + list(row[3:])
            requests.append(dict(zip(keys,values)))

    return web.json_response({'requests': requests})


async def setup():
    app = web.Application()
    db = await aiosqlite.connect(os.environ.get('DB_FILE', 'test.db'))
    await init_db(db)
    app['db'] = db
    app.add_routes(routes)
    app.router.add_static('/', dirname(realpath(__file__)))
    return app

if __name__ == '__main__':
    web.run_app(setup(), port=3000)
