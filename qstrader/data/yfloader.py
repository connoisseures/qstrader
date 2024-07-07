import yfinance as yf


class Yfloader:
    def load_as_csv(self, start_date, end_date, ticker):
        data = yf.download(ticker, start_date, end_date)
        # Export data to a CSV file
        data.to_csv(f"{ticker}.csv")
