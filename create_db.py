import psycopg2
import pandas as pd
import time
import requests
import sqlalchemy



today = time.strftime("%Y-%m-%d")

df = pd.read_csv('https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&dataTypes=TMAX,TMIN&stations=USW00023062&startDate=1950-01-01&endDate=' + today + '&units=standard').round(1)


import sqlalchemy

engine = sqlalchemy.create_engine("postgresql://postgres:1234@localhost/denver_temps")
con = engine.connect()

# print(engine.table_names())

table_name = 'temps'
df.to_sql(table_name, con)
print(engine.table_names())

con.close()


# print(df)

# res = requests.get('https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&dataTypes=TMAX,TMIN&stations=USW00023062&startDate=1950-01-01&endDate=' + today + '&units=standard')
# print(type(res.text))
# print(res.text)


# conn = psycopg2.connect(host='localhost', database='denver_temps', user='postgres', password='1234')
# cur = conn.cursor()

# # cur.execute("""CREATE TABLE dly_max_norm(
# # id SERIAL PRIMARY KEY,
# # STATION text,
# # DATE DATE,
# # DLY_NORMAL_MAX FLOAT(2),
# # DLY_NORMAL_MIN FLOAT(2),
# # DLY_NORMAL_AVG FLOAT(2))""")


# with open('res', 'r') as f:
#     next(f)
#     cur.copy_from(f, 'data', sep=',')
# f = open(r'res', 'r')
# next(f)
# cur.copy_from(res, 'data', sep=',')
# f.close()


# conn.commit()
