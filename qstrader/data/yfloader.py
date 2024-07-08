from typing import List

import yfinance as yf


class Yfloader:
    def load_as_csv(self, start_date, end_date, ticker: List[str]):
        for tk in ticker:
            data = yf.download(tk, start_date, end_date)
            # Export data to a CSV file
            data.to_csv(f"{tk}.csv")
