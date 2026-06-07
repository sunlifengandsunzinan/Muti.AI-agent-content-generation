import sqlite3, os
db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)
cur = conn.cursor()

# Check if Mac's device is creating identity records
for tbl in ['device_identities', 'device_auth_tokens']:
    cur.execute(f'SELECT * FROM "{tbl}"')
    rows = cur.fetchall()
    print(f'\n=== {tbl}: {len(rows)} rows ===')
    for r in rows:
        print(r)

# Also look at instance_id
cur.execute('SELECT device_id FROM device_pairing_paired')
print(f'\nPaired devices: {cur.fetchall()}')
cur.execute('SELECT device_id FROM device_pairing_pending')
print(f'Pending devices: {cur.fetchall()}')
    
conn.close()
