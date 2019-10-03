import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from datetime import datetime, date, timedelta
import json, csv, psycopg2, dash_table, time, operator
from conect import norm_records, rec_lows, rec_highs, all_temps
import pandas as pd
from numpy import arange,array,ones
from scipy import stats 


app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

current_year = datetime.now().year
today = time.strftime("%Y-%m-%d")
startyr = 1950
year_count = current_year-startyr

df_norms = pd.DataFrame(norm_records)

df_rec_lows = pd.DataFrame(rec_lows)

df_rec_highs = pd.DataFrame(rec_highs)

df_all_temps = pd.DataFrame(all_temps)
df_all_temps[2] = pd.to_datetime(df_all_temps[2])
last_day = df_all_temps.iloc[-1, 2] + timedelta(days=1)
ld = last_day.strftime("%Y-%m-%d")
df_all_temps = df_all_temps.set_index([2])

df_ya_max = df_all_temps.resample('Y').mean()
df5 = df_ya_max[:-1]

# trend line equations for all temp graphs
def all_max_temp_fit():
    xi = arange(0,year_count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,df5[3])
    return (slope*xi+intercept)

def all_min_temp_fit():
    xi = arange(0,year_count)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,df5[4])
    return (slope*xi+intercept)



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
                '1950-01-01 to {}'.format(ld),
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
                        {'label':'Climatology for a day', 'value':'climate-for-day'},
                        {'label':'Temperature graphs', 'value':'temp-graph'},
                        {'label':'Calendar day summaries', 'value':'cal-day-summary'},
                        {'label':'5 Year Moving Avgs', 'value':'fyma'},
                    ],
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
                html.Div(
                    id='climate-day-stuff'
                ),
            ],
                 className='eight columns'
            ),     
        ],
            className='row'
        ),
        html.Div(id='temp-data', style={'display': 'none'}),
        html.Div(id='rec-highs', style={'display': 'none'}),
        html.Div(id='rec-lows', style={'display': 'none'}),
        html.Div(id='norms', style={'display': 'none'}),
    ],
    # style={
    #     'width': '85%',
    #     'max-width': '1200',
    #     'margin-left': 'auto',
    #     'margin-right': 'auto',
    #     'font-family': 'overpass',
    #     'background-color': '#F3F3F3',
    #     'padding': '40',
    #     'padding-top': '20',
    #     'padding-bottom': '20',
    # },
)

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
    if int(selected_year) % 4 == 0:
        rec_highs = df_rec_highs
    else:
        rec_highs = df_rec_highs.drop(df_rec_highs.index[59])
    return rec_highs.to_json()

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
    # elif product_value == 'daily-data-month':
    #     return

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

@app.callback(
    Output('date-picker', 'children'),
    [Input('product', 'value')])
    # Input('year', 'value')])
def display_date_selector(product_value):
    if product_value == 'climate-for-day':
        return  dcc.DatePickerSingle(
                    id = 'climate-date-picker-single',
                    display_format='MM-DD'
                )
    # elif product_value == 'fyma':
    #     return  dcc.RadioItems(
    #                 id = 'temp-param',
    #                 options = [
    #                     {'label':'Max Temp', 'value':'Tmax'},
    #                     {'label':'Min Temp', 'value':'Tmin'},
    #                 ],
    #                 value = 'Tmax',
    #                 labelStyle = {'display':'block'}
    #             )

@app.callback(
    Output('graph-stuff', 'children'),
    [Input('product', 'value')])
def display_graph(value):
    if value == 'temp-graph':
        return dcc.Graph(id='graph1')
    elif value == 'fyma':
        return dcc.Graph(id='fyma') 

@app.callback(
    Output('climate-day-stuff', 'children'),
    [Input('product', 'value')])
def display_climate_stuff(value):
    if value == 'climate-for-day':
        return dash_table.DataTable(id='climate-day-table')
    # elif value == 'fyma':
    #     return dcc.Graph(id='fyma') 

@app.callback(
    Output('climate-day-table', 'children'),
    [Input('temp-data', 'children'),
    Input('date', 'value')])
def display_climate_day_table(temp_data, value):


    columns=[
        {"name": i, "id": i, "deletable": True, "selectable": True} for i in df_all_temps.columns
    ],
    data=df_all_temps.to_dict('records')

    return data



@app.callback(Output('graph1', 'figure'),
             [Input('temp-data', 'children'),
             Input('rec-highs', 'children'),
             Input('rec-lows', 'children'),
             Input('norms', 'children'),
             Input('year', 'value'),
             Input('period', 'value')])
def update_figure(temp_data, rec_highs, rec_lows, norms, selected_year, period):
    previous_year = int(selected_year) - 1
    selected_year = selected_year
    temps = df_all_temps

    temps[6] = temps.index.day_name()
    temps[5] = temps[3] - temps[4]
   
    temps_cy = temps[temps.index.year.isin([selected_year])]
    temps_py = temps[temps.index.year.isin([previous_year])]
    df_record_highs_ly = pd.read_json(rec_highs)
    df_record_highs_ly = df_record_highs_ly.set_index(1)
    df_record_lows_ly = pd.read_json(rec_lows)
    df_record_lows_ly = df_record_lows_ly.set_index(1)
    df_rl_cy = df_record_lows_ly[:len(temps_cy.index)]
    df_rh_cy = df_record_highs_ly[:len(temps_cy.index)]
    
    df_norms = pd.read_json(norms)
    df_norms_cy = df_norms[:len(temps_cy.index)]
  
    temps_cy.loc[:,'rl'] = df_rl_cy[0].values
    temps_cy.loc[:,'rh'] = df_rh_cy[0].values
    temps_cy.loc[:,'nh'] = df_norms_cy[3].values
    temps_cy.loc[:,'nl'] = df_norms_cy[4].values
   
    if period == 'spring':
        temps = temps_cy[temps_cy.index.month.isin([3,4,5])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index
      
    elif period == 'summer':
        temps = temps_cy[temps_cy.index.month.isin([6,7,8])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    elif period == 'fall':
        temps = temps_cy[temps_cy.index.month.isin([9,10,11])]
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    elif period == 'winter':
        date_range = []
        date_time = []
        sdate = date(int(previous_year), 12, 1)
        edate = date(int(selected_year), 12, 31)

        delta = edate - sdate

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            date_range.append(day)
        for j in date_range:
            day = j.strftime("%Y-%m-%d")
            date_time.append(day)

        temps_py = temps_py[temps_py.index.month.isin([12])]
        temps_cy = temps_cy[temps_cy.index.month.isin([1,2])]
        temp_frames = [temps_py, temps_cy]
        temps = pd.concat(temp_frames)
        date_time = date_time[:91]  
        
        df_record_highs_jan_feb = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(01-)|(02-)')]
        df_record_highs_dec = df_record_highs_ly[df_record_highs_ly.index.str.match(pat = '(12-)')]
        high_frames = [df_record_highs_dec, df_record_highs_jan_feb]
        df_record_highs = pd.concat(high_frames)

        df_record_lows_jan_feb = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(01-)|(02-)')]
        df_record_lows_dec = df_record_lows_ly[df_record_lows_ly.index.str.match(pat = '(12-)')]
        low_frames = [df_record_lows_dec, df_record_lows_jan_feb]
        df_record_lows = pd.concat(low_frames)

        df_high_norms_jan_feb = df_norms[3][0:60]
        df_high_norms_dec = df_norms[3][335:]
        high_norm_frames = [df_high_norms_dec, df_high_norms_jan_feb]
        df_high_norms = pd.concat(high_norm_frames)

        df_low_norms_jan_feb = df_norms[4][0:60]
        df_low_norms_dec = df_norms[4][335:]
        low_norm_frames = [df_low_norms_dec, df_low_norms_jan_feb]
        df_low_norms = pd.concat(low_norm_frames)

        bar_x = date_time
        nh_value = df_high_norms
        nl_value = df_low_norms
        rh_value = df_record_highs[0]
        rl_value = df_record_lows[0]

    else:
        temps = temps_cy
        nh_value = temps['nh']
        nl_value = temps['nl']
        rh_value = temps['rh']
        rl_value = temps['rl']
        bar_x = temps.index

    mkr_color = {'color':'black'}
      
    trace = [
            go.Bar(
                y = temps[5],
                x = bar_x,
                base = temps[4],
                name='Temp Range',
                marker = mkr_color,
                hovertemplate = 'Temp Range: %{y} - %{base}<extra></extra><br>'
                                # 'Record High: %{temps[6]}'                  
            ),
            go.Scatter(
                y = nh_value,
                x = bar_x,
                # hoverinfo='none',
                name='Normal High',
                marker = {'color':'indianred'}
            ),
            go.Scatter(
                y = nl_value,
                x = bar_x,
                # hoverinfo='none',
                name='Normal Low',
                marker = {'color':'slateblue'}
            ),
            go.Scatter(
                y = rh_value,
                x = bar_x,
                # hoverinfo='none',
                name='Record High',
                marker = {'color':'red'}
            ),
            go.Scatter(
                y = rl_value,
                x = bar_x,
                # hoverinfo='none',
                name='Record Low',
                marker = {'color':'blue'}
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


if __name__ == "__main__":
    app.run_server(port=8050, debug=False)