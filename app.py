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


def getRecordTemp(month, day):
    try:
        connection = psycopg2.connect(user = "postgres",
                                    password = "1234",
                                    host = "localhost",
                                    database = "denver_temps")
        cursor = connection.cursor()
        postgreSQL_select_Query = 'SELECT ("TMAX"), "DATE" FROM temps WHERE EXTRACT(month FROM "DATE"::TIMESTAMP) = {} AND EXTRACT(day FROM "DATE"::TIMESTAMP) = {} GROUP BY "TMAX", "DATE"'.format(month, day) 

        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows from temps using fetchone")
        temp_records = cursor.fetchall()

        print("Print each row and it's columns values")
        print(temp_records[0])
            
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

getRecordTemp(2, 2)


body = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.Div([
                dcc.Graph(id='graph1'),
            ]),
            width={'size':6}
        ),
    ],
    justify='around',
    ),
])


app.layout = html.Div(body)

if __name__ == "__main__":
    app.run_server(port=8050, debug=True)