import sqlite3

db_path = 'smart_agriculture_backend/smart_agriculture.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS users;")
print("Dropped users table.")

conn.commit()
conn.close() 