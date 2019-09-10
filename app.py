import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import sqlite3
from dash.dependencies import Input, Output, State
import time
from datetime import datetime
from pandas import Series
from scipy import stats
from scipy.stats import norm 
from numpy import arange,array,ones 
import dash_table 
import psycopg2
import operator

current_year = datetime.now().year
today = time.strftime("%Y-%m-%d")

# df = pd.read_csv('https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&dataTypes=TMAX,TMIN&stations=USW00023062&startDate=2019-01-01&endDate=' + today + '&units=standard').round(1)
# print(df.head())

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config['suppress_callback_exceptions']=True

# year list for dropdown selector
year = []
for YEAR in range(1950, current_year+1):
    year.append({'label':(YEAR), 'value':YEAR})

body = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.Div(
                className='app-header',
                children=[
                    html.Div('DENVER TEMPERATURE RECORD', className="app-header--title"),
                ]
            ),
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='product', options=[
                {'label':'Calendar day summaries', 'value':'Calendar day summaries'},
                {'label':'Temperature graphs', 'value':'Temperature graphs'}
            ]
            ),
            width = {'size': 3}
    # justify='around',
    ),
        dbc.Col(
            dcc.Input(
                id='year',
                value = 0,
                type = "number"
            ),
            width = {'size': 3}
        ),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([
                dcc.Graph(id='graph1'),
            ]),
            width={'size':9}
        ),
    ],
    # justify='around',
    ),
    dbc.Row([
        dbc.Col(
            html.H5('SELECT YEAR', style={'text-align':'center'})
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(id='year-picker', options=year
            ),
            width = {'size': 3}), 
    ],
    justify='around',
    )
])




@app.callback(Output('graph1', 'figure'),
             [Input('year-picker', 'value')])
def update_figure(selected_year):
    traces = []
    try:
        connection = psycopg2.connect(user = "postgres",
                                    password = "1234",
                                    host = "localhost",
                                    database = "denver_temps")
        cursor = connection.cursor()
        postgreSQL_select_Query = 'SELECT * FROM temps WHERE EXTRACT(year FROM "DATE"::TIMESTAMP) = {}'.format(selected_year)

        cursor.execute(postgreSQL_select_Query)
        temp_records = cursor.fetchall()
        # print(temp_records)
        df = pd.DataFrame(temp_records)
        df[5] = df[3] - df[4]
        print(data.head(10))
        daily_temp_range = df[3]
        # print(daily_max)
        
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    trace = [
        go.Bar(
            y = df[5],
            base = df[4],
            marker = {'color':'dodgerblue'},
            hovertemplate = "<b>STUFF</b>"
        )
    ]
    layout = go.Layout(
            xaxis = {'rangeslider': {'visible':True},},
            yaxis = {"title": 'Temperature F'},
            title ='Daily Temps',
            plot_bgcolor = 'lightgray',
            height = 900,
        )
    return {'data': trace, 'layout': layout}
   
app.layout = html.Div(body)

if __name__ == "__main__":
    app.run_server(port=8050, debug=False)


# def getRecordTemp(month, day):
#     try:
#         connection = psycopg2.connect(user = "postgres",
#                                     password = "1234",
#                                     host = "localhost",
#                                     database = "denver_temps")
#         cursor = connection.cursor()
#         postgreSQL_select_Query = 'SELECT ("TMAX"), "DATE" FROM temps WHERE EXTRACT(month FROM "DATE"::TIMESTAMP) = {} AND EXTRACT(day FROM "DATE"::TIMESTAMP) = {} GROUP BY "TMAX", "DATE"'.format(month, day) 

#         cursor.execute(postgreSQL_select_Query)
#         print("Selecting rows from temps using fetchone")
#         temp_records = cursor.fetchall()

#         print("Print each row and it's columns values")
#         print(temp_records[0])
            
#     except (Exception, psycopg2.Error) as error :
#         print ("Error while fetching data from PostgreSQL", error)
    
#     finally:
#         #closing database connection.
#         if(connection):
#             cursor.close()
#             connection.close()
#             print("PostgreSQL connection is closed")

# getRecordTemp(2, 2)
