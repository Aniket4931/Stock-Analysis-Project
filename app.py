from dash import Dash, html, dcc, Input, Output, State
from yfinance_data import Yfinance
import pandas as pd
import plotly.graph_objs as go
from talib import RSI
from ta_lib_utility import Talib
import plotly.subplots as sp
import yfinance as yf

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
            html.Label("Time range:", style={'margin-right': '10px','color': 'white', 'margin-left': '10px', 'font-size': '20px'}),
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
            html.Label("Interval time:", style={'color': 'white','margin-left': '10px', 'font-size': '20px'}),

            dcc.Dropdown(
                id='interval_time',
                options=[
                    {'label':'Hourly','value':'1h'},
                    {'label':'Daily','value':'1d'},
                    {'label':'Weekly','value':'1wk'},
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

def display_stock_info(info, yf_data):
    company_name = info.get('shortName', '')
    market_cap = info.get('marketCap', '')
    market_cap_suffixes = {
        6: 'million',
        9: 'billion',
        12: 'trillion'
    }
    magnitude = len(str(market_cap))
    suffix = market_cap_suffixes.get((magnitude - 1) // 3 * 3, '')
    formatted_market_cap = f"{market_cap / 10 ** ((magnitude - 1) // 3 * 3):,.2f} {suffix}" if suffix else f"{market_cap:,.0f}"

    stock_currency = info.get('financialCurrency')  
    sector = info.get('sector', '')

    earning_date_info = yf_data.stock_earning_date()
    next_earning_dates = earning_date_info.get('Earnings Date', [])
    next_earning_date_str = ', '.join([str(date) for date in next_earning_dates]) if next_earning_dates else 'Not available'

    stock_info = html.Div([
        html.Table(
            [
                html.Tr([html.Td(html.Strong("Company Name: "), style={'color': 'white', 'textAlign': 'start'}), html.Td(company_name, style={'color': 'white', 'textAlign': 'start'})]),
                html.Tr([html.Td(html.Strong("Market Cap: "), style={'color': 'white', 'textAlign': 'start'}), html.Td(f"{formatted_market_cap} {stock_currency}", style={'color': 'white', 'textAlign': 'start'})]),
                html.Tr([html.Td(html.Strong("Sector: "), style={'color': 'white', 'textAlign': 'start'}), html.Td(sector, style={'color': 'white', 'textAlign': 'start'})]),
                html.Tr([html.Td(html.Strong("Next Earning Date:  "), style={'color': 'white', 'textAlign': 'start'}), html.Td(next_earning_date_str, style={'color': 'white', 'textAlign': 'start'})]),
            ],
            style={'border-collapse': 'collapse', 'margin': 'auto','margin':'10px'}
        )
    ],
    style={'margin':'10px','marginRight': '1000px'}
    )

    return stock_info


def Candle_chart(data, stock_name, rangebreaks):
    title_html = stock_name
    company_logo_url = f"https://logo.clearbit.com/{stock_name}.com"


    rsi = RSI(data['Close'], timeperiod=14)  
    
    candle_trace = go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlestick'
    )


    fig = go.Figure(data=[candle_trace])

    fig.update_layout(
        xaxis={
            'title': 'Date',
            'rangebreaks': rangebreaks,
            'rangeslider': {'visible': False},
            'domain': [0, 1]  
        },
        yaxis={
            'title': 'Price',
            'domain': [0.2, 1]  
        },
        plot_bgcolor='black',
        paper_bgcolor='black',
        font={'color': '#FFFFFF'},
        margin={'t': 50, 'b': 50, 'l': 50, 'r': 50},
        height=550,
        width=1300,
        legend={'orientation': 'h', 'y': 1.1},
        hovermode='x unified',
        hoverlabel={'bgcolor': '#FFFFFF', 'font': {'color': '#333333'}},
        template='plotly_dark'
    )

    candle_chart = dcc.Graph(id='data-chart', figure=fig)
    company_logo = html.Img(
        src=company_logo_url, 
        style={
            'height': '70px', 
            'width': 'auto', 
            'margin-bottom': '10px',
            'border-radius': '10px'  
        }
    )

    return html.Div([
        company_logo,
        html.A(title_html, href=f"https://www.tradingview.com/symbols/{stock_name}", target="_blank", style={'color': 'white', 'text-align': 'center'}),
        candle_chart
    ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'})

def sub_plot(data, stock_name, rangebreaks):
    volume_trace = go.Bar(
        
        x=data.index,
        y=data['Volume'],
        name='Volume',
        marker=dict(color='cyan')     
    )

    layout = {
        'xaxis': {'title': 'Date', 'rangebreaks': rangebreaks, 'rangeslider': {'visible': False}},
        'yaxis': {'title': 'Price'},
        'yaxis2': {'title': 'Volume', 'overlaying': 'y', 'side': 'right'},  
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black',
        'font': {'color': '#FFFFFF'},
        'margin': {'t': 50, 'b': 50, 'l': 50, 'r': 50},
        'height': 200,
        'width': 1300,
        'legend': {'orientation': 'h', 'y': 1.1},
        'hovermode': 'x unified',
        'hoverlabel': {'bgcolor': '#FFFFFF', 'font': {'color': '#333333'}},
        'template': 'plotly_dark'   
    }

    fig = go.Figure(data=[volume_trace], layout=layout)
    
    return html.Div(
    html.Div([
        html.H3("Volume", style={'textAlign': 'center', 'color': 'white'}),
        dcc.Graph(id='data-chart', figure=fig)
    ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
)


def Rsi(data, stock_name, rangebreaks):
    rsi = Talib.calculate_rsi(data)
    
    rsi_trace = go.Scatter(
        x=data.index,
        y=rsi,
        mode='lines',
        name='RSI',
        line=dict(color='orange'),
        yaxis='y2'
    )
    
    fig = go.Figure(data=[rsi_trace])

    fig.update_layout(
        xaxis={
            'title': 'Date',
            'rangebreaks': rangebreaks,
            'rangeslider': {'visible': False},
            'domain': [0, 1]
        },
        yaxis2={
            'title': 'RSI',
            'domain': [0, 1],
            'overlaying': 'y',
            'side': 'right',
            'showgrid': False
        },
        plot_bgcolor='black',
        paper_bgcolor='black',
        font={'color': '#FFFFFF'},
        margin={'t': 50, 'b': 50, 'l': 50, 'r': 50},
        height=200,
        width=1300,
        legend={'orientation': 'h', 'y': 1.1},
        hovermode='x unified',
        hoverlabel={'bgcolor': '#FFFFFF', 'font': {'color': '#333333'}},
        template='plotly_dark'
    )

    return html.Div(
        html.Div([
            html.H3("RSI", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'})
    )
def macd(data, stock_name, rangebreaks):
    data = Talib.calculate_macd(data)

    macd_trace = go.Scatter(
        x=data.index,
        y=data['MACD'],
        mode='lines',
        name='MACD',
        line=dict(color='blue'),
        yaxis='y2'
    )

    signal_trace = go.Scatter(
        x=data.index,
        y=data['Signal'],
        mode='lines',
        name='Signal',
        line=dict(color='red'),
        yaxis='y2'
    )

    fig = go.Figure(data=[macd_trace, signal_trace])

    fig.update_layout(
        xaxis={
            'title': 'Date',
            'rangebreaks': rangebreaks,
            'rangeslider': {'visible': False},
            'domain': [0, 1]
        },
        yaxis={
            'title': 'MACD',
            'domain': [0.2, 1]
        },
        yaxis2={
            'title': 'Signal Line',
            'domain': [0, 1],
            'overlaying': 'y',
            'side': 'right',
            'showgrid': False
        },
        plot_bgcolor='black',
        paper_bgcolor='black',
        font={'color': '#FFFFFF'},
        margin={'t': 50, 'b': 50, 'l': 50, 'r': 50},
        height=200,
        width=1300,
        legend={'orientation': 'h', 'y': 1.1},
        hovermode='x unified',
        hoverlabel={'bgcolor': '#FFFFFF', 'font': {'color': '#333333'}},
        template='plotly_dark'
    )

    return html.Div(
        html.Div([
            html.H3("MACD", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )


def dmi_adx(data, stock_name, rangebreaks):
    Talib.calculate_dmi_and_adx(data)

    plus_di_trace = go.Scatter(
        x=data.index,
        y=data['Plus DI'],
        mode='lines',
        name='Plus DI',
        line=dict(color='green'),
        yaxis='y2'
    )

    minus_di_trace = go.Scatter(
        x=data.index,
        y=data['Minus DI'],
        mode='lines',
        name='Minus DI',
        line=dict(color='red'),
        yaxis='y2'
    )

    adx_trace = go.Scatter(
        x=data.index,
        y=data['ADX'],
        mode='lines',
        name='ADX',
        line=dict(color='blue'),
        yaxis='y2'
    )

    fig = go.Figure(data=[plus_di_trace, minus_di_trace, adx_trace])

    fig.update_layout(
        xaxis={
            'title': 'Date',
            'rangebreaks': rangebreaks,
            'rangeslider': {'visible': False},
            'domain': [0, 1]
        },
        yaxis={
            'title': 'DI/ADX',
            'domain': [0.2, 1]
        },
        plot_bgcolor='black',
        paper_bgcolor='black',
        font={'color': '#FFFFFF'},
        margin={'t': 50, 'b': 50, 'l': 50, 'r': 50},
        height=200,
        width=1300,
        legend={'orientation': 'h', 'y': 1.1},
        hovermode='x unified',
        hoverlabel={'bgcolor': '#FFFFFF', 'font': {'color': '#333333'}},
        template='plotly_dark'
    )

    return html.Div(
        html.Div([
            html.H3("DMI and ADX", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )

def Atr(data, stock_name, rangebreaks):
    data = Talib.calculate_atr(data)
    
    atr_trace = go.Scatter(
        x=data.index,
        y=data['ATR'],
        mode='lines',
        name='ATR',
        line=dict(color='orange'),
        yaxis='y2'
    )

    fig = go.Figure(data=[atr_trace])

    fig.update_layout(
        xaxis={
            'title': 'Date',
            'rangebreaks': rangebreaks,
            'rangeslider': {'visible': False},
            'domain': [0, 1]
        },
        yaxis={
            'title': 'ATR',
            'domain': [0.2, 1]
        },
        plot_bgcolor='black',
        paper_bgcolor='black',
        font={'color': '#FFFFFF'},
        margin={'t': 50, 'b': 50, 'l': 50, 'r': 50},
        height=200,
        width=1300,
        legend={'orientation': 'h', 'y': 1.1},
        hovermode='x unified',
        hoverlabel={'bgcolor': '#FFFFFF', 'font': {'color': '#333333'}},
        template='plotly_dark'
    )

    return html.Div(
        html.Div([
            html.H3("ATR", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )
    

def Roc(data, stock_name, rangebreaks):
    data = Talib.calculate_roc(data)
    
    roc_trace = go.Scatter(
        x=data.index,
        y=data['ROC'],
        mode='lines',
        name='ROC',
        line=dict(color='purple'),
        yaxis='y2'
    )

    fig = go.Figure(data=[roc_trace])

    fig.update_layout(
        xaxis={
            'title': 'Date',
            'rangebreaks': rangebreaks,
            'rangeslider': {'visible': False},
            'domain': [0, 1]
        },
        yaxis={
            'title': 'ROC',
            'domain': [0.2, 1]
        },
        plot_bgcolor='black',
        paper_bgcolor='black',
        font={'color': '#FFFFFF'},
        margin={'t': 50, 'b': 50, 'l': 50, 'r': 50},
        height=200,
        width=1300,
        legend={'orientation': 'h', 'y': 1.1},
        hovermode='x unified',
        hoverlabel={'bgcolor': '#FFFFFF', 'font': {'color': '#333333'}},
        template='plotly_dark'
    )

    return html.Div(
        html.Div([
            html.H3("ROC", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )
    



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
        
        historical_data = yf.download(full_stock_name, period='1d')
        live_price = historical_data['Close'].iloc[-1]

        data = yf_data.fetch_stock_data(period=period, interval=interval_time)
        rangebreaks = get_range_breaks(data)

        candle_chart = Candle_chart(data, stock_name, rangebreaks)
        stock_info = display_stock_info(info, yf_data)  

        Sub_plot = sub_plot(data, stock_name, rangebreaks)
        rsi = Rsi(data, stock_name, rangebreaks)
        Mcd = macd(data, stock_name, rangebreaks)
        Rock = Roc(data, stock_name, rangebreaks)
        earnings = yf_data.stock_earning_date() 
        earnings_table = create_earnings_table(earnings)

        Dmi_Adx = dmi_adx(data, stock_name, rangebreaks)  
        atr = Atr(data, stock_name, rangebreaks)  
        news = yf_data.stock_news()
        news_table = create_news_table(news)

        return html.Div(f'Price: {live_price}', style={'color': 'white', 'text-align': 'center', 'font-size': '24px'}),stock_info,  candle_chart, Sub_plot, rsi, Mcd, Dmi_Adx, atr, Rock, earnings_table, news_table

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
