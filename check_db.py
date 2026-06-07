import sqlite3, os
db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)
for t in tables:
    if 'pair' in t.lower() or 'node' in t.lower():
        print(f'\n=== {t} ===')
        cur.execute(f'SELECT * FROM "{t}"')
        rows = cur.fetchall()
        if rows:
            cols = [d[0] for d in cur.description]
            print('cols:', cols)
            for r in rows:
                print(r)
        else:
            print('(empty)')
conn.close()
