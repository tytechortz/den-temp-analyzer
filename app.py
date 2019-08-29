import psycopg2
conn = psycopg2.connect(host='localhost', database='dvdrental', user='postgres', password='1234')
cur = conn.cursor()
cur.execute('SELECT * FROM notes')
one = cur.fetchone()
all = cur.fetchall()