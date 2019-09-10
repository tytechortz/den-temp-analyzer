import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import sqlite3
from dash.dependencies import Input, Output, State
import time
# import datetime
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

# def getMaxTempYear():
#     try:
#         connection = psycopg2.connect(user = "postgres",
#                                     password = "1234",
#                                     host = "localhost",
#                                     database = "denver_temps")
#         cursor = connection.cursor()
#         postgreSQL_select_Query = 'SELECT * FROM temps WHERE EXTRACT(year FROM "DATE"::TIMESTAMP) = 1972'

#         cursor.execute(postgreSQL_select_Query)
#         temp_records = cursor.fetchall()
#         print(temp_records)

#     except (Exception, psycopg2.Error) as error :
#         print ("Error while fetching data from PostgreSQL", error)
    
#     finally:
#         #closing database connection.
#         if(connection):
#             cursor.close()
#             connection.close()
#             print("PostgreSQL connection is closed")
# getMaxTempYear()


body = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.Div([
                dcc.Graph(id='graph1'),
            ]),
            width={'size':12}
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
        data = pd.DataFrame(temp_records)
        print(data.head(10))
        daily_temp_range = data[3]
        # print(daily_max)
        top = data[3].tolist()
        print(top)
        
        bottom = data[4].tolist()
        print(bottom)
        t = list(map(operator.sub, top, bottom))
        print(t)
        ran = []
        

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    trace = [
        # go.Candlestick(
        #     # x=data[2],
        #     open='Null',high=top,low=bottom, close='Null'
        # ),
        go.Bar(
            y=t,
            base=bottom,
            marker = {'color':'dodgerblue'}
        )
    ]
    layout = go.Layout(
            xaxis={'rangeslider': {'visible':True},},
            yaxis={"title": 'stuff'},
            title='Daily Temps',
            plot_bgcolor = 'lightgray',
            height = 600,
            # barmode='stack'
        )
    return {'data': trace, 'layout': layout}
    # traces.append(go.Scatter(
    #     y = daily_max,
    #     # name = param,
    #     line = {'color':'dodgerblue'}
    #     ))

    # return {
    #     'data': data,
    #     'layout': go.Layout(
    #         xaxis = {'title': 'DAY'},
    #         yaxis = {'title': 'TEMP'},
    #         hovermode = 'closest',
    #         title = 'Daily Temps',
    #         height = 600,

    #     )
    # }







app.layout = html.Div(body)

if __name__ == "__main__":
    app.run_server(port=8050, debug=False)