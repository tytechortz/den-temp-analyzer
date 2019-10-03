import dash
import dash_core_components as dcc
import dash_html_components as html


app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

app.layout = html.Div(
    [
        html.Div([
            html.H1(
                'DENVER TEMPERATURE RECORD',
                className='eight columns',
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
                className='two columns',
            ),
        ])
    ]
)


if __name__ == "__main__":
    app.run_server(port=8050, debug=False)