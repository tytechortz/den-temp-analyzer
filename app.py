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
            width = {'size': 1}
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
        return html.Div('Date:')
    elif product_value == 'temp-graph':
        return html.Div([html.H3('Year:')])

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
    if product_value == 'temp-graph':
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
                    value = 'annual',
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

        postgreSQL_select_norms_Query = 'SELECT * FROM dly_max_norm'
        cursor.execute(postgreSQL_select_norms_Query)
        norms = cursor.fetchall()

        postgreSQL_select_record_high_Query = 'SELECT max(ALL "TMAX") AS rec_high, to_char("DATE"::TIMESTAMP,\'MM-DD\') AS day FROM temps GROUP BY day ORDER BY day ASC'
        cursor.execute(postgreSQL_select_record_high_Query)
        rec_highs = cursor.fetchall()

        postgreSQL_select_record_low_Query = 'SELECT min(ALL "TMIN") AS rec_low, to_char("DATE"::TIMESTAMP,\'MM-DD\') AS day FROM temps GROUP BY day ORDER BY day ASC'
        cursor.execute(postgreSQL_select_record_low_Query)
        rec_lows = cursor.fetchall()

        df = pd.DataFrame(temp_records)
        df[5] = df[3] - df[4]
        print(df)
        print(df[5])
        df_norms = pd.DataFrame(norms)
        df_record_highs_ly = pd.DataFrame(rec_highs)
        df_record_lows_ly = pd.DataFrame(rec_lows)
        # print(df_record_lows)
        df_record_highs = df_record_highs_ly.drop(60)
        df_record_lows = df_record_lows_ly.drop(60)
        print(df.shape)

        # df_avgs = postgreSQL_select_normal_high_Query
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


    if period == 'annual':
        temps = df[5]
        base = df[4]
        print(temps)
        data_period = df[3]
        rec_highs = df_record_highs[0]
        rec_lows = df_record_lows[0]
        high_norms = df_norms[4]
        low_norms = df_norms[3]
    elif period == 'spring':
        temps = df[5].iloc[59:155]
        base = df[4].iloc[59:155]
        data_period = df.iloc[59:155, 2]
        rec_highs = df_record_highs[0].iloc[59:155]
        rec_lows = df_record_lows[0].iloc[59:155]
        high_norms = df_norms[4].iloc[59:155]
        low_norms = df_norms[3].iloc[59:155]
     
    if int(selected_year) % 4 == 0:
        print("leap year")
        trace = [
            go.Bar(
                y = temps,
                # x = data_period,
                base = df[4],
                marker = {'color':'dodgerblue'},
                hovertemplate = "<b>STUFF</b>"
            ),
            go.Scatter(
                y = high_norms,
            ),
            go.Scatter(
                y = low_norms
            ),
            go.Scatter(
                y = df_record_highs_ly[0]
            ),
            go.Scatter(
                y = df_record_lows_ly[0]
            ),
        ]
    else:
        print("non leap year")
        trace = [
            go.Bar(
                y = temps,
                # x = data_period,
                base = base,
                marker = {'color':'blue'},
                hovertemplate = "<b>STUFF</b>"
            ),
            go.Scatter(
                y = high_norms,
            ),
            go.Scatter(
                y = low_norms
            ),
            go.Scatter(
                y = rec_highs
            ),
            go.Scatter(
                y = rec_lows
            ),
        ]
    # print(trace)

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
