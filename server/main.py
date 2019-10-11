import json
import asyncio
import aiosqlite
from aiohttp import web


'''
async def handleStream(request):
    db = request.app['db']
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={'Content-Type': 'text/plain'},
    )
    await response.prepare(request)

    async with db.execute('SELECT * FROM requests') as cursor:
        async for row in cursor:
            await response.write(json.dumps(row).encode('utf8'))

    await response.write_eof()
    return response

    #name = request.match_info.get('name', "Anonymous")
    #text = "Hello, " + name
    #return web.Response(text=text)
'''
async def handle(request):
    requests = []
    db = request.app['db']
    async with db.execute('SELECT * FROM requests') as cursor:
        keys = [d[0] for d in cursor.description]
        async for row in cursor:
            requests.append({key: value for key, value in zip(keys, row)})

    return web.json_response({'requests': requests})


async def setup(loop):
    app = web.Application(loop=loop)
    db = await aiosqlite.connect('../test.db')
    app['db'] = db
    app.add_routes([
        web.get('/requests', handle),
        #web.get('/{name}', handle)
        ])
    app.router.add_static('/', './')
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, port=3000)    
    return await site.start()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup(loop))

    try:
        loop.run_forever()
    finally:
        loop.close()
