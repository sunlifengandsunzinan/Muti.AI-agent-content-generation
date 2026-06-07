import sqlite3, os

db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)
cur = conn.cursor()

# Delete ALL node and device pairing records
cur.execute('DELETE FROM node_pairing_pending')
cur.execute('DELETE FROM node_pairing_paired')
cur.execute('DELETE FROM device_pairing_pending')
cur.execute('DELETE FROM device_pairing_paired')
cur.execute('DELETE FROM device_bootstrap_tokens')

conn.commit()
conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')

# Verify
for t in ['node_pairing_pending', 'node_pairing_paired', 'device_pairing_pending', 'device_pairing_paired']:
    cur.execute(f'SELECT COUNT(*) FROM "{t}"')
    print(f'{t}: {cur.fetchone()[0]}')

conn.close()
print('ALL PAIRING RECORDS DELETED')
