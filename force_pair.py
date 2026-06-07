import sqlite3, os, json, time

db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)

node_id = 'c22827e3-aae2-48a7-8034-486824e16352'
ts = int(time.time() * 1000)

# Delete any pending for this node
conn.execute('DELETE FROM node_pairing_pending WHERE node_id = ?', (node_id,))

# Check if already paired
cur = conn.cursor()
cur.execute('SELECT node_id, display_name FROM node_pairing_paired WHERE node_id = ?', (node_id,))
row = cur.fetchone()
if row:
    print(f'Already paired: {row}')
else:
    # Get all columns count
    cur.execute("PRAGMA table_info(node_pairing_paired)")
    col_defs = cur.fetchall()
    col_names = [c[1] for c in col_defs]
    placeholders = ','.join(['?'] * len(col_names))
    
    values = {
        'node_id': node_id, 'token': '', 'display_name': 'sunlifeng-Mac',
        'platform': 'darwin', 'version': '2026.6.1', 'core_version': '',
        'ui_version': '', 'device_family': 'macOS', 'model_identifier': '',
        'client_id': '', 'client_mode': '',
        'caps_json': json.dumps(['system']),
        'commands_json': json.dumps(['system.run.prepare', 'system.run', 'system.which']),
        'permissions_json': '', 'remote_ip': '', 'bins_json': '',
        'created_at_ms': ts, 'approved_at_ms': ts,
        'last_connected_at_ms': ts, 'last_seen_at_ms': ts,
        'last_seen_reason': 'approved'
    }
    
    vals = [values.get(c, '') for c in col_names]
    sql = f'INSERT INTO node_pairing_paired ({",".join(col_names)}) VALUES ({placeholders})'
    cur.execute(sql, vals)
    print('INSERTED paired')

conn.commit()
conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')

# Verify
cur.execute('SELECT node_id, display_name FROM node_pairing_paired WHERE node_id = ?', (node_id,))
print(f'Verified: {cur.fetchone()}')

conn.close()
print('DONE')
