import sqlite3

conn = sqlite3.connect('SAFETEXT.db')
cur = conn.cursor()
#cur.execute("DROP TABLE IF EXISTS Users")
#cur.execute("CREATE TABLE Users (id INTEGER PRIMARY KEY AUTOINCREMENT, pseudo TEXT, email TEXT, password TEXT)")

cur.execute("""INSERT INTO Users(id, pseudo, email, password) 
VALUES (1, 'User1', 'user1@gmail.com', 'user1')""")

conn.commit()

conn.close()

