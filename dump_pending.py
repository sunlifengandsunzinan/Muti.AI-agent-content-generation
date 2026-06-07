import sqlite3, os

db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute('SELECT request_id, node_id, display_name FROM node_pairing_pending')
rows = cur.fetchall()
print(f'Pending count: {len(rows)}')
for r in rows:
    print(f'  req={r[0]} node={r[1]} name={r[2]}')

cur.execute('SELECT node_id, display_name FROM node_pairing_paired')
rows2 = cur.fetchall()
print(f"\nPaired count: {len(rows2)}")
for r in rows2:
    print(f'  node={r[0]} name={r[1]}')

conn.close()
