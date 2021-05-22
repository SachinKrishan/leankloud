import sqlite3

DB_PATH = './tdo.db' 
con = sqlite3.connect(DB_PATH)

cur = con.cursor()

customers_sql = """
	CREATE TABLE todo (
    id integer NOT NULL,
    task text NOT NULL,
	status text NOT NULL,
	due text NOT NULL) """

cur.execute(customers_sql)

print(cur.fetchall())

con.commit()
cur.close()
con.close()
del cur
del con
