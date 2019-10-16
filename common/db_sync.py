import json

def init_db(db):
    with open('schemas.json') as f:
        tables = json.load(f)
        for sql in tables:
            db.execute(sql)
    db.commit()
