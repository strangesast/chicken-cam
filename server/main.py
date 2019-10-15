import os
from os.path import dirname, realpath, normpath, join
import json
import asyncio
import aiosqlite
from aiohttp import web
from pathlib import Path
from configparser import ConfigParser

from common.db import init_db


routes = web.RouteTableDef()

@routes.get('/requests')
async def handle(request):
    requests = []
    db = request.app['db']
    async with db.execute('SELECT * FROM requests') as cursor:
        keys = [d[0] for d in cursor.description]
        async for row in cursor:
            requests.append({key: value for key, value in zip(keys, row)})

    return web.json_response({'requests': requests})


@routes.get('/events')
async def handle(request):
    events = []
    db = request.app['db']
    async with db.execute('SELECT * FROM requests') as cursor:
        keys = [d[0] for d in cursor.description]
        async for row in cursor:
            events.append({key: value for key, value in zip(keys, row)})

    return web.json_response({'events': events})



async def setup():
    config = ConfigParser()
    config.read('config.ini')
    defaultConfig = config[config.default_section]
    app = web.Application()
    root = dirname(realpath(__file__))
    databaseFile = normpath(join(root, '../', defaultConfig['databasefile']))
    db = await aiosqlite.connect(databaseFile)
    await init_db(db)
    app['db'] = db
    app.add_routes(routes)
    app.router.add_static('/', dirname(realpath(__file__)))
    return app

web.run_app(setup(), port=3000)
