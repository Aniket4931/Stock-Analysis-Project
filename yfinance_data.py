'''1. Init method --> take ticker as input and set yfinance ticker obj in class variable
2. get_stock_info: Return info for stock
3. fetch_stock_data(period, interval) --> return data for stock for specific period and interval
4. get_stock_earning_date --> return earning date for stock
5. get_stock_news --> return news related to company'''
import yfinance as yf

class Yfinance:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
    
    def stock_info(self):
        info = self.stock.info
        return info
    
    def fetch_stock_data(self, period, interval):
        data = self.stock.history(period=period, interval=interval)
        return data
    
    def stock_earning_date(self):
        earnings = self.stock.calendar
        return earnings
    

    

