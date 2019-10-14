async def init_db(db):
    await db.execute('CREATE TABLE IF NOT EXISTS events (date INTEGER, raw TEXT, fromstate INTEGER, tostate INTEGER)')
    await db.execute('CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, value INTEGER, date INTEGER UNIQUE, textstate TEXT, completed INTEGER, created INTEGER)')
    await db.commit()
