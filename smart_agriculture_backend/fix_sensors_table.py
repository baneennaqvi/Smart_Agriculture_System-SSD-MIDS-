import sqlite3
import re

db_path = 'smart_agriculture_backend/smart_agriculture.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

pattern = re.compile(r'^[a-zA-Z\s]+$')

c.execute('SELECT sensor_id, location FROM sensors')
invalid = []
for row in c.fetchall():
    if not pattern.match(str(row[1])):
        print(f'Invalid sensor location: {row}')
        invalid.append(row[0])

for sensor_id in invalid:
    c.execute('DELETE FROM sensors WHERE sensor_id=?', (sensor_id,))
    print(f'Deleted sensor with id {sensor_id}')

conn.commit()
conn.close() 