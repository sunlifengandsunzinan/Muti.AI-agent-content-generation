import sqlite3, os

db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
if not os.path.exists(db):
    print(f'DB not found: {db}')
    exit(1)

conn = sqlite3.connect(db)
conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
conn.execute('DELETE FROM node_pairing_pending')
conn.execute('DELETE FROM node_pairing_paired')
conn.execute('DELETE FROM device_pairing_pending')
conn.execute('DELETE FROM device_pairing_paired')
conn.commit()
conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')

cur = conn.cursor()
for t in ['node_pairing_pending', 'node_pairing_paired', 'device_pairing_pending', 'device_pairing_paired']:
    cur.execute(f'SELECT COUNT(*) FROM "{t}"')
    cnt = cur.fetchone()[0]
    print(f'{t}: {cnt} rows')

conn.close()
print('DONE')
