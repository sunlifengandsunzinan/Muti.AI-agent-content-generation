import sqlite3, os, json, time

db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)
cur = conn.cursor()

req_id = '57987085-9048-41e2-9d47-9ad46e3aef3f'
node_id = 'c22827e3-aae2-48a7-8034-486824e16352'
ts = int(time.time() * 1000)

# Delete this pending request
cur.execute('DELETE FROM node_pairing_pending WHERE request_id = ?', (req_id,))
print(f'Deleted pending: {cur.rowcount}')

# Check paired
cur.execute('SELECT node_id FROM node_pairing_paired WHERE node_id = ?', (node_id,))
if cur.fetchone():
    print('Already paired')
else:
    col_names = [c[1] for c in cur.execute("PRAGMA table_info(node_pairing_paired)").fetchall()]
    placeholders = ','.join(['?'] * len(col_names))
    vals = {
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
    vals_list = [vals.get(c, '') for c in col_names]
    sql = f'INSERT INTO node_pairing_paired ({",".join(col_names)}) VALUES ({placeholders})'
    cur.execute(sql, vals_list)
    print('Inserted paired')

conn.commit()
conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
conn.close()
print('DONE')
