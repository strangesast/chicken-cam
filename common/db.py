import json

async def init_db(db):
    with open('schemas.json') as f:
        tables = json.load(f)
        for sql in tables:
            db.execute(sql)
    await db.commit()
