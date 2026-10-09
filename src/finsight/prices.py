import pandas as pd
import yfinance as yf
from datetime import date
from finsight.universe import STOCKS, BENCHMARK
from pathlib import Path

def download_one(ticker:str,period:str = "5y")->pd.DataFrame:

    data = yf.Ticker(ticker).history(
        period = period,
        auto_adjust = False
    )

    if data.empty:
        raise ValueError(f"No data found for{ticker}")

    data = data.reset_index()

    data["Date"] = pd.to_datetime(data["Date"]).dt.date

    data = data.rename(
        columns = {
            'Date': 'date',
            'Open':'open',
            'High':'high',
            'Low':'low',
            'Close':'close',
            'Adj Close':'adj_close',
            'Volume':'volume'
        }
    )

    data["ticker"] = ticker

    return data[['date','ticker','open','high','low','close','adj_close','volume']]


def download_all(tickers:list[str],period:str="5y")-> pd.DataFrame:
    frames = []
    failed = []

    for ticker in tickers:
        try:
            data = download_one(ticker,period)
            frames.append(data)
        except Exception as exc:
            failed.append((ticker,str(exc)))

    if not frames:
        raise RuntimeError("No ticker data downloaded")

    combined = pd.concat(frames,ignore_index=True)
    combined["as_of"] = date.today()

    if failed:
        print("Failed tickers:")
        for ticker , error in failed:
            print(f"{ticker}:{error}")

    return combined


def main():
    tickers = STOCKS + [BENCHMARK]
    data = download_all(tickers)
    
    out = Path("data/prices.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    

    data.to_csv(out,index = False)

    print(f"Saved {len(data)}rows to {out}")
    print(f"Tickers {data['ticker'].nunique()}")

if __name__=="__main__":
    main()


    

    
