import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from datetime import datetime, date, timedelta
import json, csv, dash_table, time, operator
from conect import norm_records, rec_lows, rec_highs, all_temps
import pandas as pd
from numpy import arange,array,ones
from scipy import stats 
import psycopg2

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

current_year = datetime.now().year
today = time.strftime("%Y-%m-%d")
startyr = 1950
year_count = current_year-startyr

df_norms = pd.DataFrame(norm_records)

df_rec_lows = pd.DataFrame(rec_lows)

df_rec_highs = pd.DataFrame(rec_highs)

df_all_temps = pd.DataFrame(all_temps,columns=['dow','sta','Date','TMAX','TMIN'])

app.layout = html.Div(
    [
        html.Div([
            html.H1(
                'DENVER TEMPERATURE RECORD',
                className='twelve columns',
                style={'text-align': 'center'}
            ),
        ],
            className='row'
        ),
        html.Div([
            html.H4(
                id='title-date-range',
                className='twelve columns',
                style={'text-align': 'center'}
            ),
        ],
            className='row'
        ),
        html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
        html.Div([
            html.Div([
                html.Label('Select Product'),
                dcc.RadioItems(
                    id='product',
                    options=[
                        {'label':'Temperature graphs', 'value':'temp-graph'},
                        {'label':'Climatology for a day', 'value':'climate-for-day'},
                        {'label':'5 Year Moving Avgs', 'value':'fyma'},
                        {'label':'Calendar day summaries', 'value':'cal-day-summary'},
                    ],
                    value='temp-graph',
                    labelStyle={'display': 'block'},
                ),
            ],
                className='three columns',
            ),
            html.Div([
                html.Label('Options'),
                html.Div(
                    id='period-picker'
                ),
                html.Div(
                    id='year-picker'
                ),
                html.Div(
                    id='date-picker'
                ),
            ],
                className='two-columns',
            ),  
        ],
            className='row'
        ),
        html.Div([
            html.Div([
                html.Div(
                    id='graph-stuff'
                ),
            ],
                 className='eight columns'
            ),    
        ],
            className='row'
        ),
        html.Div([
            html.Div([
                html.Div(
                    id='climate-day-table'
                ),
            ],
                className='five columns'
            ),
            html.Div([
                html.Div([
                    html.Div(id='daily-max-t'),
                ],
                    className='twelve columns'
                ),
                html.Div([
                    html.Div(id='daily-min-t'),
                ],
                    className='twelve columns'
                ), 
            ],
                className='seven columns'
            ),     
        ],
            className='row'
        ),

        html.Div(id='temp-data', style={'display': 'none'}),
        html.Div(id='rec-highs', style={'display': 'none'}),
        html.Div(id='rec-lows', style={'display': 'none'}),
        html.Div(id='norms', style={'display': 'none'}),
        html.Div(id='all-data', style={'display': 'none'}),
        html.Div(id='df5', style={'display': 'none'}),
        html.Div(id='max-trend', style={'display': 'none'}),
        html.Div(id='min-trend', style={'display': 'none'}),
        html.Div(id='daily-max-max', style={'display': 'none'}),
        html.Div(id='avg-of-dly-highs', style={'display': 'none'}),
        html.Div(id='daily-min-max', style={'display': 'none'}),
        html.Div(id='daily-min-min', style={'display': 'none'}),
        html.Div(id='avg-of-dly-lows', style={'display': 'none'}),
        html.Div(id='daily-max-min', style={'display': 'none'}),
    ],
)

@app.callback(
    Output('graph-stuff', 'children'),
    [Input('product', 'value')])
def display_graph(value):
    if value == 'temp-graph':
        return dcc.Graph(id='graph1')
    elif value == 'fyma':
        return dcc.Graph(id='fyma-graph') 
   
@app.callback(
    Output('period-picker', 'children'),
    [Input('product', 'value')])
def display_period_selector(product_value):
    if product_value == 'temp-graph':
        return  dcc.RadioItems(
                    id = 'period',
                    options = [
                        {'label':'Annual (Jan-Dec)', 'value':'annual'},
                        {'label':'Winter (Dec-Feb)', 'value':'winter'},
                        {'label':'Spring (Mar-May)', 'value':'spring'},
                        {'label':'Summer (Jun-Aug)', 'value':'summer'},
                        {'label':'Fall (Sep-Nov)', 'value':'fall'},
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

@app.callback(Output('all-data', 'children'),
            [Input('product', 'value')])
def all_temps_cleaner(product_value):
    print(product_value)
    cleaned_all_temps = df_all_temps
    cleaned_all_temps.columns=['dow','sta','Date','TMAX','TMIN']
    cleaned_all_temps['Date'] = pd.to_datetime(cleaned_all_temps['Date'])
    cleaned_all_temps = cleaned_all_temps.drop(['dow','sta'], axis=1)

    return cleaned_all_temps.to_json(date_format='iso')

@app.callback(
    Output('max-trend', 'children'),
    [Input('df5', 'children'),
    Input('product', 'value')])
def all_max_trend(df_5, product_value):
    
    df5 = pd.read_json(df_5)
    xi = arange(0,year_count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,df5['TMAX'])
    # print(product_value)
    return (slope*xi+intercept)

@app.callback(
    Output('df5', 'children'),
    [Input('all-data', 'children'),
    Input('product', 'value')])
def display_climate_day_table(all_data, product_value):
    # print(product_value)
    title_temps = pd.read_json(all_data)
    title_temps['Date']=title_temps['Date'].dt.strftime("%Y-%m-%d")
    df_date_index = df_all_temps.set_index(['Date'])
    df_ya_max = df_date_index.resample('Y').mean()
    df5 = df_ya_max[:-1]
    df5 = df5.drop(['dow'], axis=1)

    return df5.to_json(date_format='iso')

@app.callback(
    Output('min-trend', 'children'),
    [Input('df5', 'children'),
    Input('product', 'value')])
def all_min_trend(df_5, product_value):
    # print(product_value)
    df5 = pd.read_json(df_5)
    xi = arange(0,year_count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,df5['TMIN'])
    
    return (slope*xi+intercept)


@app.callback(Output('fyma-graph', 'figure'),
             [Input('temp-param', 'value'),
             Input('year', 'value'),
             Input('max-trend', 'children'),
             Input('min-trend', 'children'),
             Input('df5', 'children'),
             Input('all-data', 'children')])
def update_figure1(selected_param, selected_year, max_trend, min_trend, df_5, all_data,):
# def update_figure1(selected_param, selected_year, max_trend, min_trend, all_data,):
    print(all_data)
    fyma_temps = pd.read_json(all_data)
    fyma_temps['Date']=fyma_temps['Date'].dt.strftime("%Y-%m-%d") 
    fyma_temps.set_index(['Date'], inplace=True)
    df_5 = pd.read_json(df_5)
    all_max_temp_fit = pd.DataFrame(max_trend)
   
    all_max_temp_fit.index = df_5.index
    all_max_temp_fit.index = all_max_temp_fit.index.strftime("%Y-%m-%d")
   
    all_min_temp_fit = pd.DataFrame(min_trend)
    all_min_temp_fit.index = df_5.index
    all_min_temp_fit.index = all_min_temp_fit.index.strftime("%Y-%m-%d")
   
    all_max_rolling = fyma_temps['TMAX'].dropna().rolling(window=1825)
    all_max_rolling_mean = all_max_rolling.mean()

    all_min_rolling = fyma_temps['TMIN'].dropna().rolling(window=1825)
    all_min_rolling_mean = all_min_rolling.mean()
  

    if param == 'Tmax':
        trace = [
            go.Scatter(
                y = all_max_rolling_mean,
                x = fyma_temps.index,
                name='Max Temp'
            ),
            go.Scatter(
                y = all_max_temp_fit[0],
                x = all_max_temp_fit.index,
                name = 'trend',
                line = {'color':'red'}
            ),
        ]
    elif param == 'Tmin':
        trace = [
            go.Scatter(
                y = all_min_rolling_mean,
                x = fyma_temps.index,
                name='Min Temp'
            ),
            go.Scatter(
                y = all_min_temp_fit[0],
                x = all_min_temp_fit.index,
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



   
if __name__ == "__main__":
    app.run_server(port=8050, debug=False)