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
        
    ]
)


if __name__ == "__main__":
    app.run_server(port=8050, debug=False)