from asyncio import Event
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

app = Dash(__name__)

start_time = datetime.time(9, 15)
end_time = datetime.time(18, 30)
now = datetime.datetime.now().time()

if datetime.datetime.today().weekday() < 5 and start_time <= now <= end_time:
    interval_time = 10000  
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
                value='', placeholder=' Enter Stock Name', type='text', id='text-input', style={'marginRight': '10px','marginLeft':'10px','borderRadius': '10px'}
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
    ],
    style={'textAlign': 'center', 'color': 'white', 'margin-top': '20px','paddingBottom': '20px'}
),
     dcc.Interval(
        id="interval-component",
        interval=interval_time,
        n_intervals=0
    ),
    html.Label(id="Live_Price"),

    html.Div(id='output-container-button'),
    
],
    style={'backgroundColor': '#000000'}  
)




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
                html.Tr([html.Td(html.Strong("Website:  "), style={'color': 'white', 'textAlign': 'start'}), html.Td(html.A(company_website, href=company_website, target='_blank', style={'color': 'Blue'}), style={'color': 'white', 'textAlign': 'start'})]),
                html.Tr([html.Td(html.Strong(f"{period} Return: "), style={'color': 'White', 'textAlign': 'start'}), html.Td(f"{return_percentage:.2f}%", style={'color': return_color, 'textAlign': 'start'})]),

            ],
            style={'border-collapse': 'collapse', 'margin': 'auto','margin':'10px'}
        )
    ],
    style={'margin':'10px','marginRight': '900px'}
    )

    return stock_info


def Candle_chart(data, stock_name, rangebreaks, short_ma, medium_ma, long_ma):
    title_html = stock_name
    company_logo_url = f"https://logo.clearbit.com/{stock_name}.com"

    data = Talib.calculate_moving_averages(data, short_ma, medium_ma, long_ma)

    data = Talib.handle_candle_pattern(data)

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
                    size=20,
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
        height=800,
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
            html.H3("RSI", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )

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
            html.H3("MACD", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )


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
            html.H3("DMI and ADX", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )

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
            html.H3("ATR", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )
    

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
            html.H3("ROC", style={'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(id='data-chart', figure=fig)
        ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center','border': '1px solid white'})
    )
    
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
     State('long-ma-input', 'value')
    ],
)
def stock(n_clicks, value, radio_value, period, interval_time, short_ma, medium_ma, long_ma):
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
                
           

            data = yf_data.fetch_stock_data(period=period, interval=interval_time)
            rangebreaks = get_range_breaks(data)
            candle_chart = Candle_chart(data, stock_name, rangebreaks, short_ma, medium_ma, long_ma)
            stock_info = display_stock_info(info, yf_data, period, full_stock_name)  
            Sub_plot = sub_plot(data, stock_name, rangebreaks)
            rsi = Rsi(stock_name, rangebreaks, yf_data, period, interval_time)
            Mcd = macd(stock_name, rangebreaks, period, interval_time, yf_data)
            Rock = Roc(stock_name, rangebreaks, period, interval_time, yf_data)
            earnings = yf_data.stock_earning_date() 
            earnings_table = create_earnings_table(earnings)
            Dmi_Adx = dmi_adx(stock_name, rangebreaks, period, interval_time, yf_data)  
            atr = Atr(stock_name, rangebreaks, period, interval_time, yf_data)  
            news = yf_data.stock_news()
            news_table = create_news_table(news)

           

            return html.Div([
                stock_info,
                candle_chart,
                Sub_plot,
                rsi,
                Mcd,
                Dmi_Adx,
                atr,
                Rock,
                news_table,
               
            ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'})
    except Exception as e:
        error_message = str(e)
        return html.Div(f"An error occurred: {error_message}")


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

@app.callback(
    Output('Live_Price', 'children'),
    [Input('submit-val', 'n_clicks')],
    [Input('interval-component', 'n_intervals')],
    [State('text-input', 'value'),
     State('radio-items', 'value')]
)
def update_stock_price(n_clicks, n_intervals, value, radio_value):
    try:
        full_stock_name = value + radio_value
        historical_data = yf.download(full_stock_name, period='2d')  
        if len(historical_data) >= 2:
            yesterday_close = historical_data['Close'].iloc[-2]  
            today_close = historical_data['Close'].iloc[-1] 

            if today_close > yesterday_close:
                color = 'green'
            elif today_close < yesterday_close:
                color = 'red'
            else:
                color = 'white' 

            percentage_change = ((today_close - yesterday_close) / yesterday_close) * 100

            if percentage_change > 0:
                change_text = f"+{percentage_change:.2f}%"
            elif percentage_change < 0:
                change_text = f"{percentage_change:.2f}%"
            else:
                change_text = "(0%)"

            live_price_text = html.Div(f'Price: {today_close} ({change_text})', style={'color': color, 'text-align': 'center', 'font-size': '24px'})
            return live_price_text
        else:
            return html.Div(f'Price: N/A', style={'color': 'white', 'text-align': 'center', 'font-size': '24px'})
    except Exception as e:
        error_message = str(e)
        return html.Div(f"An error occurred: {error_message}")


if __name__ == '__main__':
    app.run_server(debug=True)
