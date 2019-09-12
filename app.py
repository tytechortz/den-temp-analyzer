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
from dash.exceptions import PreventUpdate

current_year = datetime.now().year
today = time.strftime("%Y-%m-%d")

# df = pd.read_csv('https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&dataTypes=TMAX,TMIN&stations=USW00023062&startDate=2019-01-01&endDate=' + today + '&units=standard').round(1)
# print(df.head())

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config['suppress_callback_exceptions']=True

# year list for dropdown selector
# year = []
# for YEAR in range(1950, current_year+1):
#     year.append({'label':(YEAR), 'value':YEAR})

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
            html.Div('Select Product'),
            width = 4
        ),
        dbc.Col(
            html.Div('Options')
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='product', options=[
                {'label':'Daily data for a month', 'value':'daily-data-month'},
                {'label':'Temperature graphs', 'value':'temp-graph'},
                {'label':'Calendar day summaries', 'value':'cal-day-summary'},
            ],
            value = 'daily_data_month'
            ),
            width = {'size': 3}
    # justify='around',
        ),
        dbc.Col(
            html.Div(
                id = 'time-param'
            ),
            width = {'size': 1}
        ), 
        dbc.Col(
            html.Div(
                id = 'year-picker'
            ),
        )     
    ]),
    dbc.Row([
        dbc.Col(
            html.Div(
                id = 'graph-info-row'
            )
        ),
    ]),
    dbc.Row([
        dbc.Col(
            html.Div(
                id = 'period-picker'
            ),
            width = {'size': 3}
        ),
        dbc.Col(
            html.Div(
                id='graph-stuff'
            ),
            width={'size':8}
        ),
    ]),
    dbc.Row([
        dbc.Col(
            html.H5('SELECT YEAR', style={'text-align':'center'})
        ),
    ]),
])

@app.callback(
    Output('time-param', 'children'),
    [Input('product', 'value')])
def display_time_param(product_value):
    if product_value == 'daily-data-month':
        return html.Div('Date: ')

@app.callback(
    Output('year-picker', 'children'),
    [Input('product', 'value')])
def display_year_selector(product_value):
    if product_value == 'temp-graph':
        return dcc.Input(
                    id = 'year',
                    type = 'number',
                    value = str(current_year),
                    min = 1950, max = current_year
                )
    elif product_value == 'daily-data-month':
        return 

@app.callback(
    Output('graph-info-row', 'children'),
    [Input('product', 'value')])
def display_graph_info_row(product_value):
    print(product_value)
    if product_value == 'temp_graph':
        return html.Div('Select Period')
        

@app.callback(
    Output('period-picker', 'children'),
    [Input('product', 'value')])
    # Input('year', 'value')])
   
def display_period_selector(product_value):
    if product_value == 'temp-graph':
        # def labeler():
        #     return 
        return  dcc.RadioItems(
                    id = 'period',
                    options = [
                        {'label':'Annual (Jan-Dec)', 'value':'annual'},
                        {'label':'Spring (Mar-May)', 'value':'spring'},
                        {'label':'Summer (Jun-Aug)', 'value':'summer'},
                        {'label':'Fall (Sep-Nov)', 'value':'fall'},
                        {'label':'Winter (Dec-Feb)', 'value':'winter'},
                    ],
                    labelStyle = {'display':'block'}
                )


@app.callback(
    Output('graph-stuff', 'children'),
    [Input('product', 'value')])
def display_graph(value):
    if value == 'temp-graph':
        return dcc.Graph(id='graph1')


@app.callback(Output('graph1', 'figure'),
             [Input('year', 'value'),
             Input('period', 'value')])
def update_figure(selected_year, period):
    print(period)
    traces = []
    try:
        connection = psycopg2.connect(user = "postgres",
                                    password = "1234",
                                    host = "localhost",
                                    database = "denver_temps")
        cursor = connection.cursor()
        postgreSQL_select_year_Query = 'SELECT * FROM temps WHERE EXTRACT(year FROM "DATE"::TIMESTAMP) = {}'.format(selected_year)

        cursor.execute(postgreSQL_select_year_Query)
        temp_records = cursor.fetchall()
        df = pd.DataFrame(temp_records)
        df[5] = df[3] - df[4]
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    if period == 'annual':
        data_period = df[5]
    # elif period == 'spring':

    trace = [
        go.Bar(
            y = data_period,
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
            height = 700,
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
