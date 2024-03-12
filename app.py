from dash import Dash, html, dcc, Input, Output, State
from yfinance_data import Yfinance
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.RadioItems(
            id='radio-items',
            options=[
                {'label': 'International', 'value': ''},
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
                id='period',
                options=[
                    {'label':'1D','value':'1D'},
                    {'label':'5D','value':'5D'},
                    {'label':'1M','value':'1mo'},
                    {'label':'3M','value':'3mo'},
                    {'label':'6M','value':'6mo'},
                    {'label':'1Y','value':'1yr'},
                    {'label':'2Y','value':'2yr'},
                    {'label':'5Y','value':'5yr'},
                    {'label':'Max','value':'Max'},
                ],
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
     State('radio-items', 'value'),
     State('period', 'value')]
)
def stock(n_clicks, value, radio_value, period):
    if n_clicks:
        full_stock_name = value + radio_value
        yf_data = Yfinance(full_stock_name)  
        info = yf_data.stock_info()

        table_rows = [html.Tr([html.Th(key), html.Td(str(value))]) for key, value in info.items()]

        data = yf_data.fetch_stock_data(period=period, interval='1d')
        
        info_table = html.Div([
            html.H3("Info Table", style={'textAlign': 'center'}),  
            html.Table(table_rows)
        ])
        
        data_table = html.Div([
            html.H3("Data Table", style={'textAlign': 'center'}),  
            html.Table([
                html.Thead(
                    [html.Th(col) for col in data.columns]
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(data.iloc[i][col]) 
                        for col in data.columns
                    ]) for i in range(len(data))
                ])
            ])
        ])
        
        earnings = yf_data.stock_earning_date()
        
        earnings_df = pd.DataFrame.from_dict(earnings)
        
        earnings_table = html.Div([
            html.H3("Earnings Table", style={'textAlign': 'center'}),  
            html.Table([
                html.Thead(
                    html.Tr([html.Th(col) for col in earnings_df.columns])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(earnings_df.iloc[i][col]) for col in earnings_df.columns
                    ]) for i in range(len(earnings_df))
                ])
            ])
        ])

        news=yf_data.stock_news()
        news_table = html.Div([
            html.H3("News", style={'textAlign': 'center'}),
            html.Ul(
                [html.Li(news_item['title'])
                  for news_item in news])
        ])
        
        
        return [info_table, data_table, earnings_table,news_table]


if __name__ == '__main__':
    app.run_server(debug=True)
