import sqlite3, os, json, time

db = os.path.expanduser(r'~/.openclaw/state/openclaw.sqlite')
conn = sqlite3.connect(db)

# Check table schema
cur = conn.cursor()
cur.execute("PRAGMA table_info(node_pairing_paired)")
cols = cur.fetchall()
print("node_pairing_paired columns:")
for c in cols:
    print(f"  {c[1]} ({c[2]})")

cur.execute("PRAGMA table_info(node_pairing_pending)")
cols2 = cur.fetchall()
print("\nnode_pairing_pending columns:")
for c in cols2:
    print(f"  {c[1]} ({c[2]})")

conn.close()
