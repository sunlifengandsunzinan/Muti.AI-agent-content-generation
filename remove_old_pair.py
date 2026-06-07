import sqlite3, os

db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute('DELETE FROM node_pairing_paired WHERE node_id = ?', ('c22827e3-aae2-48a7-8034-486824e16352',))
cur.execute('DELETE FROM node_pairing_pending')
cur.execute('DELETE FROM device_pairing_pending')

conn.commit()
conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')

cur.execute('SELECT COUNT(*) FROM node_pairing_paired')
print(f'Paired remaining: {cur.fetchone()[0]}')
cur.execute('SELECT COUNT(*) FROM node_pairing_pending')
print(f'Pending remaining: {cur.fetchone()[0]}')

conn.close()
print('CLEARED')
