from dash import Dash, html, dcc, Input, Output, State
from yfinance_data import Yfinance
import pandas as pd
import plotly.graph_objs as go

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
            style={'justifyContent': 'center','color': 'white','paddingTop': '20px'},
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
                    {'label':'1Y','value':'1y'},
                    {'label':'2Y','value':'2y'},
                    {'label':'5Y','value':'5y'},
                    {'label':'Max','value':'Max'},
                ],
                value='1D',
                style={'width': '80px'} 
            ),
            dcc.Dropdown(
                id='interval_time',
                options=[
                    {'label':'1h','value':'1h'},
                    {'label':'1d','value':'1d'},
                    {'label':'1w','value':'1wk'},
                ],
                value='1d',
                style={'marginRight': '10px','width': '100px','marginLeft':'5px'} 
            ),
            dcc.Input(
                value='', placeholder='Enter Stock Name', type='text', id='text-input', style={'marginRight': '10px','marginLeft':'10px'}
            ),
            html.Button('Submit', id='submit-val')
        ], 
        style={'display': 'flex', 'justifyContent': 'center', 'paddingTop': '20px','paddingBottom': '20px'}
    ),
    
    html.Div(id='output-container-button'),
    
],
    style={'backgroundColor': '#000000'}  
)

def Candle_chart(data, stock_name, rangebreaks):
    title_html = f'<a href="https://www.tradingview.com/symbols/{stock_name}" target="_blank">{stock_name}</a>'
    candle_chart = dcc.Graph(
        id='data-chart',
        figure={
            'data': [
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Candlestick'
                )
            ],
            'layout': {
                'title': title_html,
                'xaxis': {'title': 'Date', 'rangebreaks': rangebreaks, 'rangeslider': {'visible': False}},
                'yaxis': {'title': 'Price'},
                'plot_bgcolor': '#FFFFFF', 
                'paper_bgcolor': '#F0F0F0',  
                'font': {'color': '#333333'},  
                'margin': {'t': 50, 'b': 50, 'l': 50, 'r': 50},  
                'height': 600,  
                'width': 1440, 
                'legend': {'orientation': 'h', 'y': 1.1},  
                'hovermode': 'x unified', 
                'hoverlabel': {'bgcolor': '#FFFFFF', 'font': {'color': '#333333'}},  
                'template': 'plotly_white'  
            }
        }
    )
    return html.Div(candle_chart, style={'display': 'flex', 'justifyContent': 'center'})



def create_earnings_table(earnings_data):
    earnings_df = pd.DataFrame.from_dict(earnings_data)
    earnings_table = html.Div([
        html.H3("Earnings Table", style={'textAlign': 'center', 'color': 'white'}),  
        html.Table([
            html.Thead(
                html.Tr([html.Th(col) for col in earnings_df.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(earnings_df.iloc[i][col], style={'color': 'white'}) for col in earnings_df.columns
                ]) for i in range(len(earnings_df))
            ])
        ])
    ])
    return earnings_table


def create_news_table(news_data):
    news_table = html.Div([
        html.H3("News", style={'textAlign': 'center', 'color': 'white'}),
        html.Ul(
            [html.Li(news_item['title'], style={'color': 'white'}) for news_item in news_data]
        )
    ])
    return news_table


@app.callback(
    Output('output-container-button', 'children'),
    [Input('submit-val', 'n_clicks')],
    [State('text-input', 'value'),
     State('radio-items', 'value'),
     State('period', 'value'),
     State('interval_time', 'value')]  
)
def stock(n_clicks, value, radio_value, period, interval_time):
    if n_clicks:
        full_stock_name = value + radio_value
        yf_data = Yfinance(full_stock_name)  
        info = yf_data.stock_info()
        stock_name = full_stock_name[:-3]

        data = yf_data.fetch_stock_data(period=period, interval=interval_time)
        rangebreaks = get_range_breaks(data)
        candle_chart = Candle_chart(data, stock_name, rangebreaks)

        earnings = yf_data.stock_earning_date()
        earnings_table = create_earnings_table(earnings)

        news = yf_data.stock_news()
        news_table = create_news_table(news)

        return candle_chart, earnings_table, news_table


def get_range_breaks(data):
    date_series = pd.Series(data.index)
    gaps = date_series[date_series.diff() > pd.Timedelta(days=1)]
    
    rangebreaks = []

    for idx in gaps.index:
        rangebreaks.append(
            {
                "bounds": [
                    date_series.iloc[idx - 1] + pd.Timedelta(days=1),
                    date_series.iloc[idx]
                ]
            }
        )
    
    return rangebreaks




if __name__ == '__main__':
    app.run_server(debug=True)
