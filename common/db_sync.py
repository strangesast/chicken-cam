import json

def init_db(db):
    with open('common/schemas.json') as f:
        tables = json.load(f)
        for sql in tables:
            db.execute(sql)
    db.commit()
