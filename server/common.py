SCHEMAS = [
  'CREATE TABLE IF NOT EXISTS events_changes (date INTEGER, raw TEXT, fromstate INTEGER, tostate INTEGER)',
  'CREATE TABLE IF NOT EXISTS events_states (date INTEGER, raw TEXT, currentstate INTEGER, topsensor INTEGER, sidesensor INTEGER, bottomsensor INTEGER)',
  'CREATE TABLE IF NOT EXISTS events_unknown (date INTEGER, raw TEXT)',
  'CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, value INTEGER, date INTEGER UNIQUE, textstate TEXT, completed INTEGER, created INTEGER, createdgroup INTEGER)'
]

async def init_db(db):
    for sql in SCHEMAS:
        await db.execute(sql)
    await db.commit()