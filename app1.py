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
# print(df_rec_highs)


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
    html.Div(id='norms', style={'display': 'none'}),
    # html.Div(id='low-norms', style={'display': 'none'}),
])


@app.callback(Output('temp-data', 'children'),
             [Input('year', 'value'),
             Input('period', 'value')])
def all_temps(selected_year, period):
    print(type(selected_year))
    previous_year = int(selected_year) - 1
    print(previous_year)
    try:
        connection = psycopg2.connect(user = "postgres",
                                    password = "1234",
                                    host = "localhost",
                                    database = "denver_temps")

        cursor = connection.cursor()

        postgreSQL_select_year_Query = 'SELECT * FROM temps WHERE EXTRACT(year FROM "DATE"::TIMESTAMP) IN ({},{})'.format(selected_year, previous_year)
        cursor.execute(postgreSQL_select_year_Query)
        temp_records = cursor.fetchall()
        df = pd.DataFrame(temp_records)
        print(df)
        
        
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

@app.callback(Output('norms', 'children'),
             [Input('year', 'value')])
def norm_highs(selected_year):
    if int(selected_year) % 4 == 0:
        norms = df_norms
    else:
        norms = df_norms.drop(df_norms.index[59])
    return norms.to_json()

# @app.callback(Output('low-norms', 'children'),
#              [Input('year', 'value')])
# def norm_lows(selected_year):
#     if int(selected_year) % 4 == 0:
#         low_norms = df_norms[4]
#     else:
#         low_norms = df_norms[4].drop(df_norms.index[59])
#     return low_norms.to_json()

@app.callback(Output('graph1', 'figure'),
             [Input('temp-data', 'children'),
             Input('rec-highs', 'children'),
             Input('rec-lows', 'children'),
             Input('norms', 'children'),
            #  Input('low-norms', 'children'),
             Input('year', 'value'),
             Input('period', 'value')])
def update_figure(temp_data, rec_highs, rec_lows, norms, selected_year, period):
    previous_year = int(selected_year) - 1
    # spans = {'spring': [59,152], 'spring_ly': [60,153]}
    # print(spans['spring'][0])
    temps = pd.read_json(temp_data)
    temps[2] = pd.to_datetime(temps[2])
    # print(temps)
    temps = temps.set_index(2)
    # print(temps)
    temps[6] = temps.index.day_name()
    temps[5] = temps[3] - temps[4]
    # print(temps)
    temps_cy = temps[temps.index.year.isin([selected_year])]
    print(temps_cy)
    temps_py = temps[temps.index.year.isin([previous_year])]
    print(temps_py)
    df_record_highs_ly = pd.read_json(rec_highs)
    df_record_highs_ly = df_record_highs_ly.set_index(1)
    # print(df_record_highs_ly)
    df_record_lows_ly = pd.read_json(rec_lows)
    df_record_lows_ly = df_record_lows_ly.set_index(1)
    df_norms = pd.read_json(norms)
    # print(df_norms)
    # df_high_norms = df_high_norms.set_index(1)
    # df_low_norms = pd.read_json(low_norms, typ='series')
    # span = [spans[period]]
    # if period == 'winter':

        
    if period == 'spring':
        temps = temps_cy[temps_cy.index.month.isin([3,4,5])]
        df_record_highs_ly = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(03-)|(04-)|(05-)')]
        df_record_lows_ly = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(03-)|(04-)|(05-)')]
        df_high_norms = df_norms[3][59:152]
        df_low_norms = df_norms[4][59:152]
    elif period == 'summer':
        temps = temps_cy[temps_cy.index.month.isin([6,7,8])]
        df_record_highs_ly = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(06-)|(07-)|(08-)')]
        df_record_lows_ly = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(06-)|(07-)|(08-)')]
        df_high_norms = df_norms[3][151:244]
        df_low_norms = df_norms[4][151:244]
    elif period == 'fall':
        temps = temps_cy[temps_cy.index.month.isin([9,10,11])]
        df_record_highs_ly = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(09-)|(10-)|(11-)')]
        df_record_lows_ly = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(09-)|(10-)|(11-)')]
        df_high_norms = df_norms[3][243:335]
        df_low_norms = df_norms[4][243:335]
    elif period == 'winter':
        temps_py = temps_py[temps_py.index.month.isin([12])]
        temps_cy = temps_cy[temps_cy.index.month.isin([1,2])]
        frames = [temps_py, temps_cy]
        temps = pd.concat(frames)
        df_record_highs_ly = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(01-)|(02-)|(12-)')]
        df_record_lows_ly = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(01-)|(02-)|(12-)')]
        df_high_norms = df_norms[3][334:60]
        df_low_norms = df_norms[4][334:60]
        print(temps)
        
        
        

        # print(df_record_highs_ly)
    
    
    # if int(selected_year) % 4 != 0:
    #     df_record_highs = df_record_highs_ly.drop(df_record_highs_ly.index[59])
    #     df_record_lows = df_record_lows_ly.drop(df_record_lows_ly.index[59])
    # else:
    #     df_record_highs = df_record_highs_ly
    #     df_record_lows = df_record_lows_ly
        
    
    trace = [
            go.Bar(
                y = temps[5],
                # x = data_period,
                base = temps[4],
                name='Temp Range',
                marker = {'color':'dodgerblue'},
                hovertemplate = 'Temp Range: %{y} - %{base}<extra></extra>'
                                
            ),
            go.Scatter(
                y = df_high_norms,
                # hoverinfo='none',
                name='Normal High'
            ),
            go.Scatter(
                y = df_low_norms,
                # hoverinfo='none',
                name='Normal Low'
            ),
            go.Scatter(
                y = df_record_highs_ly[0],
                # hoverinfo='none',
                name='Record High'
            ),
            go.Scatter(
                y = df_record_lows_ly[0],
                # hoverinfo='none',
                name='Record Low'
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