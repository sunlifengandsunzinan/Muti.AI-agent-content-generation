import sqlite3, os
db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)
cur = conn.cursor()

for tbl in ['device_auth_tokens', 'device_identities', 'device_bootstrap_tokens']:
    cur.execute(f'PRAGMA table_info("{tbl}")')
    cols = [c[1] for c in cur.fetchall()]
    print(f'\n=== {tbl} ({", ".join(cols)}) ===')
    cur.execute(f'SELECT * FROM "{tbl}"')
    rows = cur.fetchall()
    print(f'Count: {len(rows)}')
    for r in rows[:5]:
        print(r)

conn.close()
