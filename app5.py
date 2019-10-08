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
        html.Div(id='all-data', style={'display': 'none'}),
    ]
)
       
@app.callback(Output('title-date-range', 'children'),
            [Input('all-data', 'children')])
def all_temps_cleaner(temps):
    title_temps = pd.read_json(temps)
    title_temps['Date']=title_temps['Date'].dt.strftime("%Y-%m-%d")
    last_day = title_temps.iloc[-1, 0] 
    
    return '1950-01-01 through {}'.format(last_day)   
@app.callback(Output('all-data', 'children'),
            [Input('product', 'value')])
def all_temps_cleaner(product):
    # print(product)
    cleaned_all_temps = df_all_temps
    cleaned_all_temps.columns=['dow','sta','Date','TMAX','TMIN']
    cleaned_all_temps['Date'] = pd.to_datetime(cleaned_all_temps['Date'])
    cleaned_all_temps = cleaned_all_temps.drop(['dow','sta'], axis=1)

    return cleaned_all_temps.to_json(date_format='iso')

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

        postgreSQL_select_year_Query = 'SELECT * FROM temps WHERE EXTRACT(year FROM "DATE"::TIMESTAMP) IN ({},{}) ORDER BY "DATE" ASC'.format(selected_year, previous_year)
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

if __name__ == "__main__":
    app.run_server(port=8050, debug=True)

