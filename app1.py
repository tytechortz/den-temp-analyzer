import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import sqlite3
from dash.dependencies import Input, Output, State
import time
from datetime import datetime, date, timedelta
from pandas import Series
from scipy import stats
from scipy.stats import norm 
from numpy import arange,array,ones 
import dash_table 
import psycopg2
from psycopg2 import pool
import operator
from dash.exceptions import PreventUpdate
from sqlalchemy import create_engine
import json
import csv
from conect import norm_records, rec_lows, rec_highs, all_temps
 
# print(rec_lows)
current_year = datetime.now().year
today = time.strftime("%Y-%m-%d")

startyr = 1950
year_count = current_year-startyr

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config['suppress_callback_exceptions']=True

df_norms = pd.DataFrame(norm_records)


df_rec_lows = pd.DataFrame(rec_lows)


df_rec_highs = pd.DataFrame(rec_highs)


df_all_temps = pd.DataFrame(all_temps)
df_all_temps[2] = pd.to_datetime(df_all_temps[2])
df_all_temps = df_all_temps.set_index([2])


df_ya_max = df_all_temps.resample('Y').mean()
df5 = df_ya_max[:-1]
# print(df5)


# trend line equations for all temp graphs
def all_max_temp_fit():
    xi = arange(0,year_count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,df5[3])
    return (slope*xi+intercept)

def all_min_temp_fit():
    xi = arange(0,year_count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,df5[4])
    return (slope*xi+intercept)


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
        dbc.Col(
            html.Button('Update Data', id='data-button'),
        ),
        dbc.Col(
            html.Div(id='output-data-button')
        )
    ]),
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(id='product', options=[
                {'label':'Daily data for a month', 'value':'daily-data-month'},
                {'label':'Temperature graphs', 'value':'temp-graph'},
                {'label':'Calendar day summaries', 'value':'cal-day-summary'},
                {'label':'5 Year Moving Avgs', 'value':'fyma'},
            ],
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
        )
    ]),
    html.Div(id='temp-data', style={'display': 'none'}),
    html.Div(id='rec-highs', style={'display': 'none'}),
    html.Div(id='rec-lows', style={'display': 'none'}),
    html.Div(id='norms', style={'display': 'none'}),
])


# @app.callback(Output('output-data-button', 'children'),
#              [Input('data-button', 'n_clicks')])
# def update_data(n_clicks):

#     temperatures = pd.read_csv('https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&dataTypes=TMAX,TMIN&stations=USW00023062&startDate=1950-01-01&endDate=' + today + '&units=standard')

    # print(temperatures)

    # most_recent_data_date = temperatures['DATE'].iloc[-1]

    # print(most_recent_data_date)
    # engine = create_engine('postgresql://postgres:1234@localhost:5432/denver_temps')
    # temperatures.to_sql('temps', engine, if_exists='do nothing')


    
    # try:
        # connection = psycopg2.connect(user = "postgres",
        #                             password = "1234",
        #                             host = "localhost",
        #                             database = "denver_temps")
        # cursor = connection.cursor()

        # temperatures.to_sql('temps', engine, if_exists='replace')
    
    # except (Exception, psycopg2.Error) as error :
    #     print ("Error while fetching data from PostgreSQL", error)
    
    # finally:
    #     #closing database connection.
    #     if(connection):
    #         cursor.close()
    #         connection.close()
    #         print("PostgreSQL connection is closed")

    # return "Data Through {}".format(most_recent_data_date)

@app.callback(Output('temp-data', 'children'),
             [Input('year', 'value'),
             Input('period', 'value')])
def all_temps(selected_year, period):
    previous_year = int(selected_year) - 1
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
    if int(selected_year) % 4 == 0:
        rec_lows = df_rec_lows
    else:
        rec_lows = df_rec_lows.drop(df_rec_lows.index[59])
    return rec_lows.to_json()

@app.callback(Output('norms', 'children'),
             [Input('year', 'value')])
def norm_highs(selected_year):
    if int(selected_year) % 4 == 0:
        norms = df_norms
    else:
        norms = df_norms.drop(df_norms.index[59])
    return norms.to_json()

@app.callback(Output('fyma', 'figure'),
             [Input('year', 'value'),
             Input('temp-param', 'value')])
def update_figure(selected_year, selected_param):
    temps = df_all_temps.loc['1950-1-1':str(selected_year)+'-1-1']

    all_max_rolling = temps[3].dropna().rolling(window=1825)
    all_max_rolling_mean = all_max_rolling.mean()

    all_min_rolling = temps[4].dropna().rolling(window=1825)
    all_min_rolling_mean = all_min_rolling.mean()

    if selected_param == 'Tmax':
        trace = [
            go.Scatter(
                y = all_max_rolling_mean,
                x = temps.index,
                name='Max Temp'
            ),
            go.Scatter(
                y = all_max_temp_fit(),
                x = df5.index,
                name = 'trend',
                line = {'color':'red'}
            ),
        ]
    elif selected_param == 'Tmin':
        trace = [
            go.Scatter(
                y = all_min_rolling_mean,
                x = temps.index,
                name='Min Temp'
            ),
            go.Scatter(
                y = all_min_temp_fit(),
                x = df5.index,
                name = 'trend',
                line = {'color':'red'}
            ),
    ]
    layout = go.Layout(
        xaxis = {'rangeslider': {'visible':True},},
        yaxis = {"title": 'Temperature F'},
        title ='5 Year Rolling Mean',
        plot_bgcolor = 'lightgray',
        height = 500,
    )
    return {'data': trace, 'layout': layout}

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
   
    temps = df_all_temps

    date_range = []
    date_time = []
    sdate = date(int(selected_year), 1, 1)
    edate = date(int(selected_year), 12, 31)

    delta = edate - sdate

    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        date_range.append(day)
    for j in date_range:
        day = j.strftime("%Y-%m-%d")
        date_time.append(day)
   
    temps[6] = temps.index.day_name()
    temps[5] = temps[3] - temps[4]
   
    temps_cy = temps[temps.index.year.isin([selected_year])]
    temps_py = temps[temps.index.year.isin([previous_year])]
    df_record_highs_ly = pd.read_json(rec_highs)
    df_record_highs_ly = df_record_highs_ly.set_index(1)
    df_record_lows_ly = pd.read_json(rec_lows)
   
    df_record_lows_ly = df_record_lows_ly.set_index(1)
    df_norms = pd.read_json(norms)
   
    if period == 'spring':
        temps = temps_cy[temps_cy.index.month.isin([3,4,5])]
        df_record_highs_ly = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(03-)|(04-)|(05-)')]
        df_record_lows_ly = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(03-)|(04-)|(05-)')]
        df_high_norms = df_norms[3][59:152]
        df_low_norms = df_norms[59:152]
      
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
        temp_frames = [temps_py, temps_cy]
        temps = pd.concat(temp_frames)

        df_record_highs_jan_feb = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(01-)|(02-)')]
        df_record_highs_dec = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(12-)')]
        high_frames = [df_record_highs_dec, df_record_highs_jan_feb]
        df_record_highs_ly = pd.concat(high_frames)
        df_record_lows_jan_feb = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(01-)|(02-)')]
        df_record_lows_dec = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(12-)')]
        low_frames = [df_record_lows_dec, df_record_lows_jan_feb]
        df_record_lows_ly = pd.concat(low_frames)
        df_high_norms_jan_feb = df_norms[3][0:60]
        df_high_norms_dec = df_norms[3][335:]
        high_norm_frames = [df_high_norms_dec, df_high_norms_jan_feb]
        df_high_norms = pd.concat(high_norm_frames)
        df_low_norms_jan_feb = df_norms[4][0:60]
        df_low_norms_dec = df_norms[4][335:]
        low_norm_frames = [df_low_norms_dec, df_low_norms_jan_feb]
        df_low_norms = pd.concat(low_norm_frames)
    
    else:
        temps = temps_cy
        df_high_norms = df_norms[3]
        df_low_norms = df_norms[4]
      
    trace = [
            go.Bar(
                y = temps[5],
                x = temps_cy.index,
                # x = date_time,
                base = temps[4],
                name='Temp Range',
                marker = {'color':'dodgerblue'},
                hovertemplate = 'Temp Range: %{y} - %{base}<extra></extra>'
                                
            ),
            go.Scatter(
                y = df_high_norms,
                x = date_time,
                # hoverinfo='none',
                name='Normal High'
            ),
            go.Scatter(
                y = df_low_norms,
                x = date_time,
                # hoverinfo='none',
                name='Normal Low'
            ),
            go.Scatter(
                y = df_record_highs_ly[0],
                x = date_time,
                # hoverinfo='none',
                name='Record High'
            ),
            go.Scatter(
                y = df_record_lows_ly[0],
                x = date_time,
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
    if product_value == 'temp-graph' or 'fyma':
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
    elif value == 'fyma':
        return dcc.Graph(id='fyma') 
    

# @app.callback(
#     Output('year-slider', 'children'),
#     [Input('temp-param', 'value')])
# def display_slider(value):
#     return dcc.Slider(
#         id='fyma-slider',
#         min=df_all_temps.index.year.min(),
#         max=df_all_temps.index.year.max(),
#         marks={str(year): str(year) for year in df_all_temps.index.year.unique()}
#     )

@app.callback(
    Output('graph-info-row', 'children'),
    [Input('product', 'value')])
def display_graph_info_row(product_value):
    print(product_value)
    if product_value == 'temp-graph':
        return html.Div('Select Period')
    elif product_value == 'fyma':
        return html.Div('Select Parameter')

@app.callback(
    Output('period-picker', 'children'),
    [Input('product', 'value')])
    # Input('year', 'value')])
def display_period_selector(product_value):
    if product_value == 'temp-graph':
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
    elif product_value == 'fyma':
        return  dcc.RadioItems(
                    id = 'temp-param',
                    options = [
                        {'label':'Max Temp', 'value':'Tmax'},
                        {'label':'Min Temp', 'value':'Tmin'},
                    ],
                    value = 'Tmax',
                    labelStyle = {'display':'block'}
                )

# @app.callback(
#     Output('year-slider', 'children'),
#     [Input('temp-param', 'value')])
# def display_year_selector(product_value):
    




app.layout = html.Div(body)

if __name__ == "__main__":
    app.run_server(port=8050, debug=False)