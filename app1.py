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
from psycopg2 import pool
import operator
from dash.exceptions import PreventUpdate
import json
# import conect
from conect import norm_records, rec_lows, rec_highs, all_temps
# from conect import rec_lows
 

current_year = datetime.now().year
today = time.strftime("%Y-%m-%d")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config['suppress_callback_exceptions']=True

df_norms = pd.DataFrame(norm_records)
# print(df_norms)

df_rec_lows = pd.DataFrame(rec_lows)

df_rec_highs = pd.DataFrame(rec_highs)


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
    html.Div(id='rec-lows', style={'display': 'none'}),
    html.Div(id='high-norms', style={'display': 'none'}),
    html.Div(id='low-norms', style={'display': 'none'}),
])


@app.callback(Output('temp-data', 'children'),
             [Input('year', 'value'),
             Input('period', 'value')])
def all_temps(selected_year, period):
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
def rec_high_temps(selected_year):
    return df_rec_highs.to_json()

@app.callback(Output('rec-lows', 'children'),
             [Input('year', 'value')])
def rec_low_temps(selected_year):
    return df_rec_lows.to_json()

@app.callback(Output('high-norms', 'children'),
             [Input('year', 'value')])
def norm_highs(selected_year):
    if int(selected_year) % 4 == 0:
        high_norms = df_norms[3]
    else:
        high_norms = df_norms[3].drop(df_norms.index[59])
    return high_norms.to_json()

@app.callback(Output('low-norms', 'children'),
             [Input('year', 'value')])
def norm_lows(selected_year):
    if int(selected_year) % 4 == 0:
        low_norms = df_norms[4]
    else:
        low_norms = df_norms[4].drop(df_norms.index[59])
    return low_norms.to_json()

@app.callback(Output('graph1', 'figure'),
             [Input('temp-data', 'children'),
             Input('rec-highs', 'children'),
             Input('rec-lows', 'children'),
             Input('high-norms', 'children'),
             Input('low-norms', 'children'),
             Input('year', 'value'),
             Input('period', 'value')])
def update_figure(temp_data, rec_highs, rec_lows, high_norms, low_norms, selected_year, period):
    temps = pd.read_json(temp_data)
    # print(temps[2])
    temps[2] = pd.to_datetime(temps[2])
    temps[6] = temps[2].dt.day_name()
    print(temps)
    # days = temps['day_name']
   
    temps[5] = temps[3] - temps[4]
    df_record_highs_ly = pd.read_json(rec_highs)
    df_record_lows_ly = pd.read_json(rec_lows)
    df_high_norms = pd.read_json(high_norms, typ='series')
    df_low_norms = pd.read_json(low_norms, typ='series')
    
    if int(selected_year) % 4 != 0:
        df_record_highs = df_record_highs_ly.drop(df_record_highs_ly.index[59])
        df_record_lows = df_record_lows_ly.drop(df_record_lows_ly.index[59])
    else:
        df_record_highs = df_record_highs_ly
        df_record_lows = df_record_lows_ly
        
    
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(df_record_highs)
    trace = [
            go.Bar(
                y = temps[5],
                # x = data_period,
                base = temps[4],
                marker = {'color':'dodgerblue'},
                hovertemplate = '<b>%{temps[6]}</b>'
            ),
            go.Scatter(
                y = df_high_norms,
                hoverinfo='none'
                
            ),
            go.Scatter(
                y = df_low_norms,
                hoverinfo='none'
            ),
            go.Scatter(
                y = df_record_highs[0],
                hoverinfo='none'
            ),
            go.Scatter(
                y = df_record_lows[0],
                hoverinfo='none'
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