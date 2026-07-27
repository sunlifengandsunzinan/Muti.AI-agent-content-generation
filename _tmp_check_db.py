import sqlite3, json

conn = sqlite3.connect(r'D:\moto\data\gpx\processed_videos.db')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', tables)
for t in tables:
    cols = conn.execute(f'PRAGMA table_info("{t[0]}")').fetchall()
    print(f'  {t[0]}: cols={[c[1] for c in cols]}')
    cnt = conn.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
    print(f'    total rows: {cnt}')
    if cnt > 0:
        rows = conn.execute(f'SELECT * FROM "{t[0]}" LIMIT 3').fetchall()
        for i, r in enumerate(rows):
            print(f'    row{i}: {r}')
        # Check column names to find GPX/track data
        col_names = [c[1] for c in cols]
        print(f'    columns: {col_names}')
        tot_km = 0
        if 'distance' in col_names:
            di = col_names.index('distance')
            all_d = conn.execute(f'SELECT distance FROM "{t[0]}"').fetchall()
            for d in all_d:
                if d[0]:
                    try:
                        tot_km += float(d[0])
                    except:
                        pass
            print(f'    total distance: {tot_km:.1f} km')
conn.close()
