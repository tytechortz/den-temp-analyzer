import dash
from dash.dependencies import Input, Output
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from conect import norm_records, rec_lows, rec_highs, all_temps
from datetime import datetime, date, timedelta
import json, csv, psycopg2, dash_table, time, operator

df = pd.DataFrame(all_temps,columns=['dow','sta','Date','TMAX','TMIN'])
df = df.drop(['dow','sta'], axis=1)

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

current_year = datetime.now().year
today = time.strftime("%Y-%m-%d")
startyr = 1950
year_count = current_year-startyr

df_all_temps = pd.DataFrame(all_temps,columns=['dow','sta','Date','TMAX','TMIN'])
df_all_temps['Date'] = pd.to_datetime(df_all_temps['Date'])

last_day = df_all_temps.iloc[-1, 2] + timedelta(days=1)
ld = last_day.strftime("%Y-%m-%d")
df_all_temps = df_all_temps.drop(['dow','sta'], axis=1)
df_date_index = df_all_temps.set_index(['Date'])
# print(df_date_index.columns)
df_ya_max = df_date_index.resample('Y').mean()
df5 = df_ya_max[:-1]

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
                    id='datatable-interactivity-container'
                ),
            ],
                 className='eight columns'
            ),
            html.Div([
                html.Div(
                    id='climate-day-stuff'
                ),
            ])     
        ],
            className='row'
        ),
        html.Div(id='temp-data', style={'display': 'none'}),
        html.Div(id='rec-highs', style={'display': 'none'}),
        html.Div(id='rec-lows', style={'display': 'none'}),
        html.Div(id='norms', style={'display': 'none'}),
    ],
)

@app.callback(
    Output('date-picker', 'children'),
    [Input('product', 'value')])
    # Input('year', 'value')])
def display_date_selector(product_value):
    if product_value == 'climate-for-day':
        return  dcc.DatePickerSingle(
                    id='date',
                    display_format='MM-DD',
                    date=today
                )

# @app.callback(
#     Output('time-param', 'children'),
#     [Input('product', 'value')])
# def display_time_param(product_value):
#     if product_value == 'daily-data-month':
#         return html.Div('Date:')
#     elif product_value == 'temp-graph':
#         return html.Div([html.H3('Year:')])
@app.callback(
    Output('climate-day-stuff', 'children'),
    [Input('product', 'value')])
def display_climate_stuff(value):
    if value == 'climate-for-day':
        return dt.DataTable(id='datatable-interactivity',
        data=[{}], 
        columns=[{}], 
        fixed_rows={'headers': True, 'data': 0},
        style_cell_conditional=[
            {'if': {'column_id': 'Date'},
            'width':'140px'},
            {'if': {'column_id': 'TMAX'},
            'width':'140px'},
            {'if': {'column_id': 'TMIN'},
            'width':'140px'},
        ],
        # editable=True,
        # filter_action="native",
        # sort_action="native",
        # sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        # row_deletable=True,
        # selected_columns=[],
        selected_rows=[],
        # page_action="native",
        page_current= 0,
        # page_size= 10,
        )

@app.callback(
    Output('datatable-interactivity-container', "children"),
    [Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):
    # derived_virtual_data=df_all_temps.to_rows('dict')
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    print(rows)
    # df_all_temps = pd.DataFrame(all_temps,columns=['dow','sta','Date','TMAX','TMIN'])
    # dff = df if rows is None else pd.DataFrame(rows)
    dff = pd.DataFrame(rows)
    # df_all_temps = df_all_temps.drop(['dow','sta'], axis=1)
    print(dff)
    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]
    
    return [
        dcc.Graph(
            id=column,
            figure={
                'data': [
                    {
                        "x": dff.index,
                        "y": dff[column],
                        "type": "bar",
                        # "marker": {"color": colors},
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": dff[column]}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        for column in ['TMAX','TMIN'] 
    ]

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

@app.callback([
    Output('datatable-interactivity', 'data'),
    Output('datatable-interactivity', 'columns')],
    [Input('temp-data', 'children'),
    Input('date', 'date')])
def display_climate_day_table(temp_data, date):
    dr = df_date_index[(df_date_index.index.month == int(date[5:7])) & (df_date_index.index.day == int(date[8:10]))]
    # dr = df_all_temps
    print(dr.columns[0])
    dr = dr.reset_index()
    
    columns=[
        {"name": i, "id": i} for i in dr.columns
    ]

    # dr_new = dr.reset_index()
    # print(dr_new)
    print(dr.to_dict('records'))
    # dr_new['Date'] = dr['Date'].dt.strftime('%Y-%m-%d')
    print(columns)
    # data = dr.to_dict('records')
    # return dr_new.to_dict('records'), columns
    return dr.to_dict('records'), columns

if __name__ == '__main__':
    app.run_server(debug=False)