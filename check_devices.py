import sqlite3, os
db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
for t in cur.fetchall():
    print(t[0])
for tbl in ['device_pairing_paired', 'device_pairing_pending']:
    cur.execute(f'SELECT * FROM "{tbl}"')
    rows = cur.fetchall()
    print(f'\n{tbl}: {len(rows)}')
    for r in rows:
        print(r)
conn.close()
