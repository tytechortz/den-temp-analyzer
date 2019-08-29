import psycopg2
# conn = psycopg2.connect(host='localhost', database='tutorial', user='postgres', password='1234')
# cur = conn.cursor()
# cur.execute("""CREATE TABLE users(
# id integer PRIMARY KEY,
# email text,
# name text,
# address text)""")
# conn.commit()

conn = psycopg2.connect(host='localhost', database='denver_temps', user='postgres', password='1234')
cur = conn.cursor()
cur.execute("""CREATE TABLE dly_avg_norm(
id integer PRIMARY KEY,
STATION text,
DATE DATE,
DLY_AVG_NORMAL float)""")
conn.commit()
