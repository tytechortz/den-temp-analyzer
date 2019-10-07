import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_table as dt
from dash.dependencies import Input, Output, State


# df = pd.read_csv('https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&dataTypes=TMAX,TMIN&stations=USW00023062&startDate=2019-01-01&endDate=2019-09-30&units=standard').round(1)
df = pd.read_csv('daily_normal_max.csv')
print(df)

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']=True

app.layout = html.Div(
    [
         html.Div([
            html.Div([
                html.Label('Select Product'),
                dcc.RadioItems(
                    id='product',
                    options=[
                        {'label':'Temperature graphs', 'value':'temp-graph'},
                        {'label':'Climatology for a day', 'value':'climate-for-day'},
                    ],
                    value='climate-for-day',
                    labelStyle={'display': 'block'},
                ),
            ],
                className='three columns',
            ),
        ]),
        html.Div([
                html.Div(
                    id='date-picker'
                ),
            ],
                className='two-columns',
            ),  
        html.Div([
            html.Div([
                html.Div(
                    id='climate-day-table'
                ),
            ]),     
        ]),
    ]
)


@app.callback(
    Output('date-picker', 'children'),
    [Input('product', 'value')])
def display_date_selector(product_value):
    if product_value == 'climate-for-day':
        return  dcc.DatePickerSingle(
                    id='date',
                    display_format='MM-DD',
                )

@app.callback(
    Output('climate-day-table', 'children'),
    [Input('product', 'value')])
def display_climate_stuff(value):
    if value == 'climate-for-day':
        return dt.DataTable(id='datatable-interactivity',
        data=[{}], 
        columns=[{}],
        # filter_action="native", 
        # sort_mode="multi",
        # column_selectable="single",
        # row_selectable="multi",
        # row_deletable=True,
        # selected_columns=[],
        # selected_rows=[],
        # page_current= 0,
        # page_size= 10,
        # style_as_list_view=True,
        )

@app.callback([
    Output('datatable-interactivity', 'data'),
    Output('datatable-interactivity', 'columns')],
    [Input('date', 'date')])
def display_climate_day_table(date):
    print(date)
    columns=[
        {"name": i, "id": i,"filterable": True} for i in df.columns
    ]
    
    return df.to_dict('records'), columns

if __name__ == "__main__":
    app.run_server(port=8050, debug=False)