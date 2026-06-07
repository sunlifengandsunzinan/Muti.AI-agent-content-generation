import sqlite3, os, json

db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)
cur = conn.cursor()

# Show all paired nodes
cur.execute('SELECT node_id, display_name FROM node_pairing_paired')
print('=== All paired nodes ===')
for r in cur.fetchall():
    print(f'  {r[0]} - {r[1]}')

# Show all pending  
cur.execute('SELECT request_id, node_id, display_name, ts FROM node_pairing_pending')
print('\n=== All pending requests ===')
for r in cur.fetchall():
    print(f'  request: {r[0][:20]}... node: {r[1][:20]}... name: {r[2]} ts: {r[3]}')

conn.close()
