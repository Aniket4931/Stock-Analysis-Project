import pandas as pd
import numpy as np
import yfinance as yf
from candles import candle_patterns

class Talib:
    @staticmethod
    def calculate_rsi(data, column_name='Close', periods=14):
        close_prices = data[column_name]
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
        fast_ema = data['Close'].ewm(span=fast_period, adjust=False).mean()
        slow_ema = data['Close'].ewm(span=slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        data['MACD'] = macd
        data['Signal'] = signal
        return data

    @staticmethod
    def calculate_roc(data, column_name='Close', period=12):
        roc = (data[column_name].diff(period) / data[column_name].shift(period)) * 100
        data['ROC'] = roc
        return data

    @staticmethod
    def calculate_bollinger_bands_width(data, period=20, nbdevup=2, nbdevdn=2):
        rolling_mean = data['Close'].rolling(window=period).mean()
        rolling_std = data['Close'].rolling(window=period).std()
        upper_band = rolling_mean + (rolling_std * nbdevup)
        lower_band = rolling_mean - (rolling_std * nbdevdn)
        bb_width = (upper_band - lower_band) / rolling_mean
        data['BB_Width'] = bb_width
        return data

    @staticmethod
    def calculate_dmi_and_adx(data, high_col='High', low_col='Low', close_col='Close', period=14):
        high = data[high_col]
        low = data[low_col]
        close = data[close_col]

        plus_dm = high.diff()
        minus_dm = low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0

        tr1 = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
        atr = tr1.rolling(window=period).mean()

        plus_di = 100 * (plus_dm.ewm(alpha=1/period).mean() / atr)
        minus_di = abs(100 * (minus_dm.ewm(alpha=1/period).mean() / atr))

        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.ewm(alpha=1/period).mean()

        data['Plus DI'] = plus_di
        data['Minus DI'] = minus_di
        data['ADX'] = adx

        return data

    @staticmethod
    def calculate_moving_averages(data, short_window=50, medium_window=100, long_window=200):
        data['Short MA'] = data['Close'].rolling(window=short_window).mean()
        data['Medium MA'] = data['Close'].rolling(window=medium_window).mean()
        data['Long MA'] = data['Close'].rolling(window=long_window).mean()
        return data

    @staticmethod
    def calculate_atr(data, high_col='High', low_col='Low', close_col='Close', period=14):
        high = data[high_col]
        low = data[low_col]
        close = data[close_col]

        tr1 = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
        atr = tr1.rolling(window=period).mean()

        data['ATR'] = atr
        return data

    @staticmethod
    def handle_candle_pattern(data):
        for pattern_name, pattern_data in candle_patterns.items():
            pattern_function = getattr(Talib, pattern_name.lower(), None)
            if pattern_function:
                result = pattern_function(data)
                result_filtered = np.where(result != 0, result, np.nan)
                data[pattern_name + '_result'] = result_filtered
                data[pattern_name + '_description'] = pattern_data['description']
        data.dropna(how='all', inplace=True)
        return data

    @staticmethod
    def cdldoji(data):
        open_close_diff = abs(data['Open'] - data['Close'])
        high_low_diff = data['High'] - data['Low']
        doji = open_close_diff <= 0.1 * high_low_diff
        return doji.astype(int)

    @staticmethod
    def cdlengulfing(data):
        prev_open = data['Open'].shift(1)
        prev_close = data['Close'].shift(1)
        engulfing = ((data['Close'] > data['Open']) & (data['Open'] < prev_close) & (data['Close'] > prev_open)) | \
                    ((data['Close'] < data['Open']) & (data['Open'] > prev_close) & (data['Close'] < prev_open))
        return engulfing.astype(int)

    @staticmethod
    def cdlhammer(data):
        lower_shadow = data['Low'] - data[['Open', 'Close']].min(axis=1)
        body = abs(data['Close'] - data['Open'])
        upper_shadow = data[['Open', 'Close']].max(axis=1) - data['High']
        hammer = (lower_shadow > 2 * body) & (upper_shadow < body)
        return hammer.astype(int)

    @staticmethod
    def cdlhangingman(data):
        lower_shadow = data['Low'] - data[['Open', 'Close']].min(axis=1)
        body = abs(data['Close'] - data['Open'])
        upper_shadow = data[['Open', 'Close']].max(axis=1) - data['High']
        hanging_man = (lower_shadow > 2 * body) & (upper_shadow < body) & (data['Close'] < data['Open'])
        return hanging_man.astype(int)

    @staticmethod
    def cdlharami(data):
        prev_open = data['Open'].shift(1)
        prev_close = data['Close'].shift(1)
        body = abs(data['Close'] - data['Open'])
        prev_body = abs(prev_close - prev_open)
        harami = (body < prev_body) & (data['Open'] > prev_close) & (data['Close'] < prev_open)
        return harami.astype(int)

    @staticmethod
    def cdlinvertedhammer(data):
        upper_shadow = data['High'] - data[['Open', 'Close']].max(axis=1)
        body = abs(data['Close'] - data['Open'])
        lower_shadow = data[['Open', 'Close']].min(axis=1) - data['Low']
        inverted_hammer = (upper_shadow > 2 * body) & (lower_shadow < body)
        return inverted_hammer.astype(int)

    @staticmethod
    def cdlshootingstar(data):
        upper_shadow = data['High'] - data[['Open', 'Close']].max(axis=1)
        body = abs(data['Close'] - data['Open'])
        lower_shadow = data[['Open', 'Close']].min(axis=1) - data['Low']
        shooting_star = (upper_shadow > 2 * body) & (lower_shadow < body) & (data['Close'] < data['Open'])
        return shooting_star.astype(int)



