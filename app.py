import psycopg2
conn = psycopg2.connect(host='localhost', database='tutorial', user='postgres', password='1234')
cur = conn.cursor()
cur.execute("""CREATE TABLE users(
id integer PRIMARY KEY,
email text,
name text,
address text)""")
conn.commit()

