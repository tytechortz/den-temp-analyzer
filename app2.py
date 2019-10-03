import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True


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


if __name__ == "__main__":
    app.run_server(port=8050, debug=False)