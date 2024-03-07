from dash import Dash, html, dcc, Input, Output, State
import yfinance as yf
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.RadioItems(
            id='radio-items',
            options=[
                {'label': 'NSC', 'value': '.NS'},
                {'label': 'BSC', 'value': '.Bo'}
            ],
            style={'justifyContent': 'center'},
            value='.NS',  
            labelStyle={'display': 'inline-block'}
        )
    ], style={'textAlign': 'center'}), 

    html.Div(
        children=[
            dcc.Dropdown(
                options=['1D', '5D', '1M', '3M', '6M', '1Y', '2Y', '5Y', 'Max'],
                value='1D',
                style={'width': '80px'} 
            ),
            dcc.Input(
                value='', placeholder='Enter Stock Name', type='text', id='text-input', style={'marginRight': '10px','marginLeft':'10px'}
            ),
            html.Button('Submit', id='submit-val')
        ], 
        style={'display': 'flex', 'justifyContent': 'center', 'paddingTop': '20px','paddingBottom': '20px'}
    ),
    html.Div(id='output-container-button')
],
    style={'backgroundColor': '#CFD8DC'}  
)


@app.callback(
    Output('output-container-button', 'children'),
    [Input('submit-val', 'n_clicks')],
    [State('text-input', 'value'),
     State('radio-items', 'value')]
)
def stock_info(n_clicks, value, radio_value):
    if n_clicks:
        full_stock_name = value + radio_value
        stock = yf.Ticker(full_stock_name)
        info = stock.info
        one_year = stock.history(period="1yr")
        he = one_year.head()

        return f"Company Name:  {info['longName']},   Sector: {info['sector']},   Exchange: {info['exchange']} "

if __name__ == '__main__':
    app.run_server(debug=True)
