import sqlite3, os, json, time

db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)
cur = conn.cursor()

req_id = '57987085-9048-41e2-9d47-9ad46e3aef3f'
ts = int(time.time() * 1000)

# First get the actual pending request data from the Mac log to see what node_id it uses
# Let's scan node_pairing_pending (might be empty now)
cur.execute('SELECT * FROM node_pairing_pending')
pending = cur.fetchall()
print(f'Pending count: {len(pending)}')
for r in pending:
    print(f'  {r}')

# Also check node_pairing_paired
cur.execute('SELECT * FROM node_pairing_paired')
paired = cur.fetchall()
print(f'\nPaired count: {len(paired)}')
for r in paired:
    print(f'  {r}')

conn.close()
