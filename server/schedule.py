import os
import asyncio
import aiosqlite
import contextlib
from astral import Astral
from datetime import datetime, timedelta

astral = Astral()
city = astral['Buffalo']

OPEN = 1
CLOSE = 0

def get_commands(start=datetime.now(), count=7):
    for i in range(0, count):
        date = start + timedelta(days=i)
        # floor date (unnecessary)
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        # astral info for city & date
        s = city.sun(local=False, date=date) # by default use current date, utc time
        # utc sunrise / sunset
        times = s['sunrise'], s['sunset']
        # use local timezone
        times = [t.astimezone(tz=None) for t in times]
        # shift by an hour
        times = [t + timedelta(minutes=20) for t in times]
        # what do at time
        data = zip([OPEN, CLOSE], times)
        # only produce commands after now
        yield from filter(lambda v: v[1].replace(tzinfo=None) > start, data)


async def main():
    db_file = os.environ.get('DB_FILE', 'test.db')
    async with aiosqlite.connect(db_file) as db:
        cur = await db.cursor()
        now = int(datetime.now().timestamp())
        await cur.execute('insert into transactions (date) values (?)', (now,));

        transactionid = cur.lastrowid

        records = [(value, int(date.timestamp()), 'scheduled', now, transactionid)
                for value, date in get_commands()]
        await cur.executemany(''''insert into requests (value, scheduleddate,
                textstate, createddate, transactionid) values (?,?,?,?,?)''', records)
        await db.commit()


if __name__ == '__main__':
    asyncio.run(main())
