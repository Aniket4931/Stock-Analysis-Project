
import yfinance as yf

class Yfinance:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
    
    def stock_info(self):
        info = self.stock.info
        return info
    
    def fetch_stock_data(self, period, interval):
        data = self.stock.history(period=period, interval=interval,rounding=2)
        return data

    
    def stock_earning_date(self):
        earnings = self.stock.calendar
        return earnings
    
    def stock_news(self):
        news = self.stock.news
        return news

    

    

