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
import json

current_year = datetime.now().year
today = time.strftime("%Y-%m-%d")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config['suppress_callback_exceptions']=True


connection = psycopg2.connect(user = "postgres",
                                    password = "1234",
                                    host = "localhost",
                                    database = "denver_temps")



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
    html.Div(id='temp-data', style={'display': 'none'}),
    html.Div(id='rec-highs', style={'display': 'none'}),
    html.Div(id='rec-lows', style={'display': 'none'})
])

try:
        connection = psycopg2.connect(user = "postgres",
                                    password = "1234",
                                    host = "localhost",
                                    database = "denver_temps")

        cursor = connection.cursor()

        postgreSQL_select_norms_Query = 'SELECT * FROM dly_max_norm'
        cursor.execute(postgreSQL_select_norms_Query)
        norms = cursor.fetchall()
except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
finally:
    #closing database connection.
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

df_norms = pd.DataFrame(norms)
print(df_norms.head())
high_norms = df_norms[4]
low_norms = df_norms[3]

@app.callback(Output('temp-data', 'children'),
             [Input('year', 'value'),
             Input('period', 'value')])
def all_temps(selected_year, period):
    
    try:
        connection 
        cursor = connection.cursor()

        postgreSQL_select_year_Query = 'SELECT * FROM temps WHERE EXTRACT(year FROM "DATE"::TIMESTAMP) = {}'.format(selected_year)
        cursor.execute(postgreSQL_select_year_Query)
        temp_records = cursor.fetchall()
        df = pd.DataFrame(temp_records)
        
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    return df.to_json()

@app.callback(Output('rec-highs', 'children'),
             [Input('year', 'value')])
def all_temps(selected_year):
    try:
        connection = psycopg2.connect(user = "postgres",
                                    password = "1234",
                                    host = "localhost",
                                    database = "denver_temps")

        cursor = connection.cursor()

        postgreSQL_select_record_high_Query = 'SELECT max(ALL "TMAX") AS rec_high, to_char("DATE"::TIMESTAMP,\'MM-DD\') AS day FROM temps GROUP BY day ORDER BY day ASC'
        cursor.execute(postgreSQL_select_record_high_Query)
        rec_highs = cursor.fetchall()
        df_rec_high = pd.DataFrame(rec_highs)

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    return df_rec_high.to_json()

    
@app.callback(Output('rec-lows', 'children'),
             [Input('year', 'value')])
def all_temps(selected_year):
    try:
        connection = psycopg2.connect(user = "postgres",
                                    password = "1234",
                                    host = "localhost",
                                    database = "denver_temps")

        cursor = connection.cursor()

        postgreSQL_select_record_low_Query = 'SELECT min(ALL "TMIN") AS rec_low, to_char("DATE"::TIMESTAMP,\'MM-DD\') AS day FROM temps GROUP BY day ORDER BY day ASC'
        cursor.execute(postgreSQL_select_record_low_Query)
        rec_lows = cursor.fetchall()
        df_rec_low = pd.DataFrame(rec_lows)
        
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    return df_rec_low.to_json()


@app.callback(Output('graph1', 'figure'),
             [Input('temp-data', 'children'),
             Input('rec-highs', 'children'),
             Input('rec-lows', 'children'),
             Input('year', 'value'),
             Input('period', 'value')])
def update_figure(temp_data, rec_highs,rec_lows, selected_year, period):
    temps = pd.read_json(temp_data)
    temps[5] = temps[3] - temps[4]
    df_record_highs_ly = pd.read_json(rec_highs)
    df_record_lows_ly = pd.read_json(rec_lows)
    df_record_highs_ry = df_record_highs_ly.drop(df_record_highs_ly.index[0])
    if int(selected_year) % 4 != 0:
        df_record_highs = df_record_highs_ly.drop(df_record_highs_ly.index[59])
        df_record_lows = df_record_lows_ly.drop(df_record_lows_ly.index[60])
    else:
        df_record_highs = df_record_highs_ly
        df_record_lows = df_record_lows_ly
        
    
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df_record_highs)
    trace = [
            go.Bar(
                y = temps[5],
                # x = data_period,
                base = temps[4],
                marker = {'color':'dodgerblue'},
                hovertemplate = "<b>STUFF</b>"
            ),
            # go.Scatter(
            #     y = high_norms,
            # ),
            # go.Scatter(
            #     y = low_norms
            # ),
            go.Scatter(
                y = df_record_highs[0]
            ),
            go.Scatter(
                y = df_record_lows[0]
            ),
        ]
    layout = go.Layout(
                xaxis = {'rangeslider': {'visible':True},},
                yaxis = {"title": 'Temperature F'},
                title ='Daily Temps',
                plot_bgcolor = 'lightgray',
                height = 700,
        )
    return {'data': trace, 'layout': layout}

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
    Output('graph-stuff', 'children'),
    [Input('product', 'value')])
def display_graph(value):
    if value == 'temp-graph':
        return dcc.Graph(id='graph1')

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



app.layout = html.Div(body)

if __name__ == "__main__":
    app.run_server(port=8050, debug=False)