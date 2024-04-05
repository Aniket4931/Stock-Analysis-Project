import talib
import pandas as pd
import numpy as np
import yfinance as yf
from candles import candle_patterns

class Talib:
    @staticmethod
    def calculate_rsi(data, column_name='Close', periods=14,start_index=14):
        close_prices = data[column_name]
        rsi = talib.RSI(close_prices, timeperiod=periods)
        return rsi


    @staticmethod
    def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
        macd, signal, _ = talib.MACD(data['Close'], fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)
        data['MACD'] = macd
        data['Signal'] = signal
        return data

    @staticmethod
    def calculate_roc(data, column_name='Close', period=12):
        roc = talib.ROC(data[column_name], timeperiod=period)
        data['ROC'] = roc
        return data
    
    @staticmethod
    def calculate_bollinger_bands_width(data, period=20, nbdevup=2, nbdevdn=2):
        upper, middle, lower = talib.BBANDS(data['Close'], timeperiod=period, nbdevup=nbdevup, nbdevdn=nbdevdn)
        bb_width = (upper - lower) / middle
        data['BB_Width'] = bb_width
        return data
    
    @staticmethod
    def calculate_dmi_and_adx(data, high_col='High', low_col='Low', close_col='Close', period=14):
        high = data[high_col].values
        low = data[low_col].values
        close = data[close_col].values
        plus_di = talib.PLUS_DI(high, low, close, timeperiod=period)
        minus_di = talib.MINUS_DI(high, low, close, timeperiod=period)
        adx = talib.ADX(high, low, close, timeperiod=period)
        data['Plus DI'] = plus_di
        data['Minus DI'] = minus_di
        data['ADX'] = adx
        return data


    def calculate_moving_averages(data, short_window=50, medium_window=100, long_window=200):
        short_ma = data['Close'].rolling(window=short_window, min_periods=1).mean()
        medium_ma = data['Close'].rolling(window=medium_window, min_periods=1).mean()
        long_ma = data['Close'].rolling(window=long_window, min_periods=1).mean()
        data['Short MA'] = short_ma
        data['Medium MA'] = medium_ma
        data['Long MA'] = long_ma
        return data

    @staticmethod
    def calculate_atr(data, high_col='High', low_col='Low', close_col='Close', period=14):
        high = data[high_col].values
        low = data[low_col].values
        close = data[close_col].values

        atr = talib.ATR(high, low, close, timeperiod=period)
        data['ATR'] = atr

        return data
    
    
    
    def handle_candle_pattern(data):
        for pattern_name, pattern_data in candle_patterns.items():
            pattern_function_name = pattern_data['function']
            pattern_description = pattern_data['description']
            pattern_function = getattr(talib, pattern_function_name)
            result = pattern_function(data['Open'], data['High'], data['Low'], data['Close'])
            result_filtered = np.where(result != 0, result, np.nan)
            data[pattern_name + '_result'] = result_filtered
            data[pattern_name + 'description'] = pattern_description  

        data.dropna(how='all', inplace=True)

        return data





