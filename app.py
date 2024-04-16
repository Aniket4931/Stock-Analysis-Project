import datetime
from dash import Dash, html, dcc, Input, Output, State
from yfinance_data import Yfinance
import pandas as pd
import plotly.graph_objs as go
from talib import RSI
from ta_lib_utility import Talib
import plotly.subplots as sp
import yfinance as yf
from plotly.subplots import make_subplots
from candles import candle_patterns
import requests
from bs4 import BeautifulSoup
import time
from stocks_names import stocks_names

app = Dash(__name__)

start_time = datetime.time(9, 15)
end_time = datetime.time(15, 30)
now = datetime.datetime.now().time()

if datetime.datetime.today().weekday() < 5 and start_time <= now <= end_time:
    interval_time = 2000  
else:
    interval_time = 24 * 60 * 60 * 1000 
    
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
                value='1mo',
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
                id='text-input',
                list='stock-names', 
                value='', 
                placeholder='Enter Stock Name', 
                type='text', 
                style={'marginRight': '10px','marginLeft':'10px','borderRadius': '10px'}
            ),
            html.Datalist(
                id='stock-names',
                children=[],
            ),
             
    html.Button('Submit', id='submit-val', style={'border-radius': '10px', 'padding': '10px 20px'})
            ], 
        style={'display': 'flex', 'justifyContent': 'center', 'paddingTop': '20px','paddingBottom': '20px'}
    ),
   html.Div(
    children=[
        html.Label("Short MA (days):", style={'color': 'white'}),
        dcc.Input(
            id='short-ma-input',
            type='number',
            value=50,  
            style={'margin-right': '10px', 'width': '80px'}
        ),
        html.Label("Medium MA (days):", style={'color': 'white'}),
        dcc.Input(
            id='medium-ma-input',
            type='number',
            value=100,  
            style={'margin-right': '10px', 'width': '80px'}
        ),
        html.Label("Long MA (days):", style={'color': 'white'}),
        dcc.Input(
            id='long-ma-input',
            type='number',
            value=200,  
            style={'margin-right': '10px', 'width': '80px'}
        ),
        html.Label("Future LR(days):", style={'color': 'white'}),
        dcc.Input(
            id='Linear-input',
            type='number',
            value=2,  
            style={'margin-right': '10px', 'width': '80px'}
        ),
    ],
    style={'textAlign': 'center', 'color': 'white', 'margin-top': '20px','paddingBottom': '20px'}
),

    dcc.Interval(
        id="interval-component",
        interval=interval_time,
        n_intervals=0
    ),
    html.Label("Price",id="live-price-output"),
    html.Div(id='output-container-button'),

], style={'backgroundColor': '#000000'})

@app.callback(
    Output('stock-names', 'children'),
    [Input('text-input', 'value')]
)
def update_stock_name_suggestions(value):
    suggestions = [stock for stock in stocks_names if value.lower() in stock.lower()]
    return [html.Option(value=suggestion) for suggestion in suggestions]

@app.callback(
    Output('live-price-output', 'children'),
    [Input('submit-val', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State('text-input', 'value'),
    State('radio-items', 'value'),
]
)

# Stock Live Price
def update_stock_price(n_clicks, n_intervals, value,radio_value):
    if ".NS"==radio_value:
        radio="NSE"
    elif ".Bo"==radio_value:
        radio="BOM"
    else :
        radio="NASDAQ"
    try:
        if n_clicks or n_intervals:
            url = f'https://www.google.com/finance/quote/{value}:{radio}'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            class1 = "YMlKec fxKbKc"
            live_price = soup.find(class_=class1).text
            sf="Price "+live_price
            return html.Div([
                html.Div(sf, style={'color': 'Green','textAlign': 'center','font-size': '25px' })
            ])
    except Exception as e:
        return f"Error fetching live price: {str(e)}"

        

# Stock Information
def display_stock_info(info, yf_data, period, full_stock_name):
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

    historical_data = yf.download(full_stock_name, period=period)
    if not historical_data.empty:
        first_close = historical_data['Close'].iloc[0]
        last_close = historical_data['Close'].iloc[-1]
        return_percentage = ((last_close - first_close) / first_close) * 100
    else:
        return_percentage = 0

    if return_percentage < 0:
        return_color = 'red'
    else:
        return_color = 'green'

    company_website = info.get('website', 'Not available')

    stock_info = html.Div([
        html.Table(
            [
                html.Tr([html.Td(html.Strong("Company Name: "), style={'color': 'white', 'textAlign': 'start'}), html.Td(company_name, style={'color': 'white', 'textAlign': 'start'})]),
                html.Tr([html.Td(html.Strong("Market Cap: "), style={'color': 'white', 'textAlign': 'start'}), html.Td(f"{formatted_market_cap} {stock_currency}", style={'color': 'white', 'textAlign': 'start'})]),
                html.Tr([html.Td(html.Strong("Sector: "), style={'color': 'white', 'textAlign': 'start'}), html.Td(sector, style={'color': 'white', 'textAlign': 'start'})]),
                html.Tr([html.Td(html.Strong("Next Earning Date:  "), style={'color': 'white', 'textAlign': 'start'}), html.Td(next_earning_date_str, style={'color': 'white', 'textAlign': 'start'})]),
                html.Tr([html.Td(html.Strong("Website:  "), style={'color': 'white', 'textAlign': 'start'}), html.Td(html.A(company_website, href=company_website, target='_blank', style={'color': 'White'}), style={'color': 'white', 'textAlign': 'start'})]),
                html.Tr([html.Td(html.Strong(f"{period} Return: "), style={'color': 'White', 'textAlign': 'start'}), html.Td(f"{return_percentage:.2f}%", style={'color': return_color, 'textAlign': 'start'})]),

            ],
            style={'border-collapse': 'collapse', 'margin': 'auto','margin':'10px'}
        )
    ],
    style={'margin':'10px','marginRight': '900px'}
    )

    return stock_info

import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

# Candle Chart , Candle Patterns, Moving averages, Linear Regeression
def Candle_chart(data, stock_name, rangebreaks, short_ma, medium_ma, long_ma, future_days):
    title_html = stock_name
    company_logo_url = f"https://logo.clearbit.com/{stock_name}.com"

    data = Talib.calculate_moving_averages(data, short_ma, medium_ma, long_ma)
    data = Talib.handle_candle_pattern(data)

    X = np.arange(len(data)).reshape(-1, 1)
    y = data['Close'].values.reshape(-1, 1)
    reg = LinearRegression().fit(X, y)
    linear_regression_line = reg.predict(X)

    future_X = np.arange(len(data), len(data) + future_days).reshape(-1, 1)
    future_linear_regression_line = reg.predict(future_X)

    std_dev = data['Close'].rolling(window=20).std()
    upper_band = linear_regression_line.flatten() + 2 * std_dev
    lower_band = linear_regression_line.flatten() - 2 * std_dev

    candle_trace = go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlestick'
    )

    short_ma_trace = go.Scatter(
        x=data.index,
        y=data['Short MA'],
        mode='lines',
        name=f'Short MA({short_ma})',
        line=dict(color='blue')
    )

    medium_ma_trace = go.Scatter(
        x=data.index,
        y=data['Medium MA'],
        mode='lines',
        name=f'Medium MA({medium_ma})',
        line=dict(color='green')
    )

    long_ma_trace = go.Scatter(
        x=data.index,
        y=data['Long MA'],
        mode='lines',
        name=f'Long MA({long_ma})',
        line=dict(color='red')
    )
    
    linear_regression_trace = go.Scatter(
        x=data.index,
        y=linear_regression_line.flatten(),
        mode='lines',
        name='Linear Regression',
        line=dict(color='orange', dash='dash')
    )

    future_linear_regression_trace = go.Scatter(
        x=[data.index[-1] + timedelta(days=i) for i in range(1, future_days + 1)],
        y=future_linear_regression_line.flatten(),
        mode='lines',
        name=f'Future Linear Regression ({future_days} days)',
        line=dict(color='Cyan', dash='dash')
    )

    upper_band_trace = go.Scatter(
        x=data.index,
        y=upper_band,
        mode='lines',
        name='Upper Band',
        line=dict(color='green', dash='dash')
    )

    lower_band_trace = go.Scatter(
        x=data.index,
        y=lower_band,
        mode='lines',
        name='Lower Band',
        line=dict(color='red', dash='dash')
    )

    pattern_colors = ['Orange', 'Cyan', 'Fuchsia', 'red', 'SpringGreen', 'yellow', 'Chartreuse', 'magenta']  
    start_index = 3
    
    pattern_traces = []
    color_index = 0
    
    for pattern in data.columns:
        if pattern.endswith('_result'):
            pattern_name = pattern[start_index:].replace('_result', '').replace('_', ' ').title()
            color = pattern_colors[color_index % len(pattern_colors)]
            pattern_key = pattern[:-len('_result')]  
            pattern_description = candle_patterns[pattern_key]['description']  
    
            pattern_trace = go.Scatter(
                x=data.index,
                y=data[pattern],
                mode='markers',
                name=pattern_name,
                marker=dict(
                    color=color,
                    size=15,
                ),
                opacity=0.8,
                text=pattern_description, 
            )
    
            pattern_traces.append(pattern_trace)
            color_index += 1


    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)

    fig.add_trace(candle_trace, row=1, col=1)
    fig.add_trace(short_ma_trace, row=1, col=1)
    fig.add_trace(medium_ma_trace, row=1, col=1)
    fig.add_trace(long_ma_trace, row=1, col=1)
    fig.add_trace(linear_regression_trace, row=1, col=1)
    fig.add_trace(future_linear_regression_trace, row=1, col=1)
    fig.add_trace(upper_band_trace, row=1, col=1)
    fig.add_trace(lower_band_trace, row=1, col=1)

    for pattern_trace in pattern_traces:
        fig.add_trace(pattern_trace, row=2, col=1)

    fig.update_layout(
        xaxis=dict(
            title=f'<span style="color:{pattern_colors[0]}; font-size: 18px;">&#x2022; Doji </span> <span style="color:{pattern_colors[1]}; font-size: 18px;">&#x2022; Engulfing </span><span style="color:{pattern_colors[2]}; font-size: 18px;">&#x2022; Hammer </span><span style="color:{pattern_colors[3]}; font-size: 18px;">&#x2022; Hanging Man </span><span style="color:{pattern_colors[4]}; font-size: 18px;">&#x2022; Harami </span><span style="color:{pattern_colors[5]}; font-size: 18px;">&#x2022; Inverted Hammer </span><span style="color:{pattern_colors[6]}; font-size: 18px;">&#x2022; Shooting Star</span> ',

            rangebreaks=rangebreaks,
            rangeslider={'visible': False}
        ),
        yaxis=dict(
            title='Price'
        ),
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='#FFFFFF'),
        height=900,
        width=1300,
        legend=dict(orientation='h', y=1.1),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#FFFFFF', font=dict(color='#333333')),
        template='plotly_dark',
   
    )

    company_logo = html.Img(
        src=company_logo_url, 
        style={
            'height': '70px', 
            'width': 'auto', 
            'margin-bottom': '10px',
            'border-radius': '10px'  
        }
    )

    div = html.Div([
        company_logo,
        html.A(title_html, href=f"https://www.tradingview.com/symbols/{stock_name}", target="_blank", style={'color': 'white', 'text-align': 'center'}),
        dcc.Graph(id='data-chart', figure=fig),
    ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'})
    return div

#Volume chart
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

# Rsi( Relative Strength Index) Chart 
def Rsi( stock_name, rangebreaks,yf_data,period,interval_time):
    if period=="1D":
        period="1y"
    elif period=='5D':
        period="1y"
    elif period=="1mo":
        period="1y"
    elif period=="3mo":
        period="1y"
    elif period=="6mo":
        period="1y"
    
    data = yf_data.fetch_stock_data(period=period, interval=interval_time)
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
            html.H3("RSI (Relative Strength Index)", style={'textAlign': 'center', 'color': 'white'}),
            
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )


# Macd(Moving Average Convergence Divergence) Chart
def macd( stock_name, rangebreaks,period,interval_time,yf_data):
    if period=="1D":
        period="1y"
    elif period=='5D':
        period="1y"
    elif period=="1mo":
        period="1y"
    elif period=="3mo":
        period="1y"
    elif period=="6mo":
        period="1y"
    data = yf_data.fetch_stock_data(period=period, interval=interval_time)

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
            html.H3("MACD (Moving Average Convergence Divergence)", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )


# DMI (Directional Movement Index) and ADX (Average Directional Index)
def dmi_adx( stock_name, rangebreaks,period,interval_time,yf_data):
    if period=="1D":
        period="6mo"
    elif period=='5D':
        period="6mo"
    elif period=="1mo":
        period="14mo"
    elif period=="3mo":
        period="1y"
    elif period=="6mo":
        period="1y"



    data = yf_data.fetch_stock_data(period=period, interval=interval_time)
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
            html.H3("DMI (Directional Movement Index) and ADX (Average Directional Index)", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )

# Atr(Average True Range) chart
def Atr(stock_name, rangebreaks,period,interval_time,yf_data):
    if period=="1D":
        period="6mo"
    elif period=='5D':
        period="6mo"
    elif period=="1mo":
        period="1y"
    elif period=="3mo":
        period="1y"
    elif period=="6mo":
        period="1y"
    data = yf_data.fetch_stock_data(period=period, interval=interval_time)
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
            html.H3("ATR (Average True Range)", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )
    
# Roc(Rate of Change) Chart
def Roc(stock_name, rangebreaks,period,interval_time,yf_data):
    if period=="1D":
        period="6mo"
    elif period=='5D':
        period="6mo"
    elif period=="1mo":
        period="1y"
    elif period=="3mo":
        period="1y"
    elif period=="6mo":
        period="1y"
    data = yf_data.fetch_stock_data(period=period, interval=interval_time)
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
            html.H3("ROC (Rate of Change)", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )
    

# bolling bbdas    
def bollinger_bbdas(data, rangebreaks, period, interval_time, yf_data):
    if period == "1D":
        period = "6mo"
    elif period == '5D':
        period = "6mo"
    elif period == "1mo":
        period = "1y"
    elif period == "3mo":
        period = "1y"
    elif period == "6mo":
        period = "1y"

    data = yf_data.fetch_stock_data(period=period, interval=interval_time)
    data = Talib.calculate_bollinger_bands_width(data)

    bb_width_trace = go.Scatter(
        x=data.index,
        y=data['BB_Width'],  
        mode='lines',
        name='Bollinger Bands Width',
        line=dict(color='purple'),
        yaxis='y2'
    )

    fig = go.Figure(data=[bb_width_trace])

    fig.update_layout(
        xaxis={
            'title': 'Date',
            'rangebreaks': rangebreaks,
            'rangeslider': {'visible': False},
            'domain': [0, 1]
        },
        yaxis={
            'title': 'Bollinger Bands Width',
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
            html.H3("Bollinger Bands Width", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'border': '1px solid white'})
    )


    

def create_news_table(news_data):
    news_table = html.Div([
        html.H3("News", style={'textAlign': 'center', 'color': 'white'}),
        html.Ul(
            [html.Li(news_item['title'], style={'color': 'white'}) for news_item in news_data]
        )
    ])
    return html.Div(
        html.Div([news_table
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'})
    )


   

@app.callback(
    Output('output-container-button', 'children'),
    [Input('submit-val', 'n_clicks')],
    [State('text-input', 'value'),
     State('radio-items', 'value'),
     State('period', 'value'),
     State('interval_time', 'value'),
     State('short-ma-input', 'value'),  
     State('medium-ma-input', 'value'),
     State('long-ma-input', 'value'),
     State('Linear-input', 'value')

    ],
)


        

# Main Function
def stock(n_clicks, value, radio_value, period, interval_time, short_ma, medium_ma, long_ma,Linear_input):
    try:
        if n_clicks:
            full_stock_name = value + radio_value
            yf_data = Yfinance(full_stock_name)  
            info = yf_data.stock_info()

            if full_stock_name[-3:]==".BO":
                stock_name=full_stock_name[:-3]
            elif full_stock_name[-3:]==".NS":
                stock_name=full_stock_name[:-3]
            else:
                stock_name=full_stock_name

            future_days = Linear_input  

            data = yf_data.fetch_stock_data(period=period, interval=interval_time)
            rangebreaks = get_range_breaks(data)
            candle_chart = Candle_chart(data, stock_name, rangebreaks, short_ma, medium_ma, long_ma,future_days)
            stock_info = display_stock_info(info, yf_data, period, full_stock_name)  
            Sub_plot = sub_plot(data, stock_name, rangebreaks)
            rsi = Rsi(stock_name, rangebreaks, yf_data, period, interval_time)
            Mcd = macd(stock_name, rangebreaks, period, interval_time, yf_data)
            Rock = Roc(stock_name, rangebreaks, period, interval_time, yf_data)
            earnings = yf_data.stock_earning_date() 
            Dmi_Adx = dmi_adx(stock_name, rangebreaks, period, interval_time, yf_data)  
            atr = Atr(stock_name, rangebreaks, period, interval_time, yf_data)  
            news = yf_data.stock_news()
            news_table = create_news_table(news)
            boling= bollinger_bbdas(data, rangebreaks, period, interval_time, yf_data)

           

            return html.Div([
                stock_info,
                candle_chart,
                Sub_plot,
                rsi,
                Mcd,
                Dmi_Adx,
                boling,
                atr,
                Rock,
                news_table,

            ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'})
    except Exception as e:
        error_message = str(e)
        return html.Div(f"An error occurred: {error_message}")

#rang breaker
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