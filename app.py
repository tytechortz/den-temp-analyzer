import pandas as pd
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from data import NormalTMax
import psycopg2


today = time.strftime("%Y-%m-%d")

# df = pd.read_csv('https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&dataTypes=TMAX,TMIN&stations=USW00023062&startDate=2019-01-01&endDate=' + today + '&units=standard').round(1)
# print(df.head())

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config['suppress_callback_exceptions']=True

try:
    connection = psycopg2.connect(user = "postgres",
                                  password = "1234",
                                  host = "localhost",
                                  database = "denver_temps")
    cursor = connection.cursor()
    postgreSQL_select_Query = "select * from temps"

    cursor.execute(postgreSQL_select_Query)
    print("Selecting rows from mobile table using cursor.fetchall")
    temp_records = cursor.fetchall()

    print("Print each row and it's columns values")
    for row in temp_records:
        print("Id = ", row[0], )
        print("Station = ", row[1])
        print("Date = ", row[2])
        print("TMax = ", row[3])
        
except (Exception, psycopg2.Error) as error :
    print ("Error while fetching data from PostgreSQL", error)
 
finally:
    #closing database connection.
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
