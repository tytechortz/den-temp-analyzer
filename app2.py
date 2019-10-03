import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from datetime import datetime, date, timedelta
import json, csv, psycopg2, dash_table, time, operator


app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

current_year = datetime.now().year
today = time.strftime("%Y-%m-%d")


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
        html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
        html.Div([
            html.Div([
                html.Label('Select Product'),
                dcc.RadioItems(
                    id='product',
                    options=[
                        {'label':'Daily data for a month', 'value':'daily-data-month'},
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
            ],
                className='two-columns',
            ),  
        ],
            className='row'
        ),
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


if __name__ == "__main__":
    app.run_server(port=8050, debug=False)