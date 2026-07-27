import sqlite3
import os

db_path = 'D:/MediaCrawler/browser_data/dy_user_data_dir/Default/Network/Cookies'

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("PRAGMA table_info(cookies)")
cols = c.fetchall()
print("Columns in cookies table:")
for col in cols:
    print(f"  {col}")

c.execute("SELECT host_key, name, encrypted_value FROM cookies LIMIT 10")
rows = c.fetchall()
for row in rows:
    ev = row[2]
    print(f"  {row[0]:30s} | {row[1]:30s} | encrypted_len={len(ev)}")
conn.close()
