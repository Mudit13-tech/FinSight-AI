import pandas as pd
import yfinance as yf
from datetime import date
from finsight.universe import STOCKS, BENCHMARK
from pathlib import Path
import argparse

def download_one(
    ticker: str,
    period: str = "5y",
    start: date | None = None,
) -> pd.DataFrame:

    if start is not None:
        data = yf.Ticker(ticker).history(
            start=start,
            auto_adjust=False
        )
    else:
        data = yf.Ticker(ticker).history(
            period=period,
            auto_adjust=False
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


def merge_prices(old: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    old = old.copy()
    new = new.copy()

    old["date"] = pd.to_datetime(old["date"])
    new["date"] = pd.to_datetime(new["date"])

    old["as_of"] = pd.to_datetime(old["as_of"])
    new["as_of"] = pd.to_datetime(new["as_of"])

    combined = pd.concat([old, new], ignore_index=True)

    combined = combined.drop_duplicates(
        subset=["date", "ticker"],
        keep="last",
    )

    combined = combined.sort_values(
        ["ticker", "date"]
    ).reset_index(drop=True)

    return combined

def adjustment_changed(
    old_rows: pd.DataFrame,
    new_rows: pd.DataFrame,
    tolerance: float = 1e-4,
) -> bool:
    old = old_rows.copy()
    new = new_rows.copy()

    old["date"] = pd.to_datetime(old["date"])
    new["date"] = pd.to_datetime(new["date"])

    a = old.set_index("date")["adj_close"]
    b = new.set_index("date")["adj_close"]

    common = a.index.intersection(b.index)

    if len(common) == 0:
        return True

    rel_diff = (a[common] - b[common]).abs() / a[common]

    return bool((rel_diff > tolerance).any())

def update_prices(
    path: Path = Path("data/prices.csv"),
    overlap_days: int = 7,
) -> pd.DataFrame:
    tickers = STOCKS + [BENCHMARK]

    if not path.exists():
        return download_all(tickers)

    old = pd.read_csv(path)
    frames = []
    old_tickers = set(old["ticker"].unique())

    for ticker in tickers:
        old_rows = old[old["ticker"] == ticker]

        # New ticker: download full historical data
        if ticker not in old_tickers:
            try:
                new_rows = download_one(ticker)
                new_rows["as_of"] = date.today()
                frames.append(new_rows)
            except Exception as exc:
                print(f"Download failed for {ticker}: {exc}")
            continue

        # Find latest saved date BEFORE downloading
        latest_date = pd.to_datetime(old_rows["date"]).max().date()
        start_date = latest_date - pd.Timedelta(days=overlap_days)

        # Download recent and overlapping data
        try:
            new_rows = download_one(ticker, start=start_date)
            new_rows["as_of"] = date.today()
        except Exception as exc:
            print(f"Update failed for {ticker}: {exc}")
            frames.append(old_rows)
            continue

        # If adjusted prices changed, download full history
        if adjustment_changed(old_rows, new_rows):
            try:
                full_rows = download_one(ticker)
                full_rows["as_of"] = date.today()
                frames.append(full_rows)
            except Exception as exc:
                print(f"Full download failed for {ticker}: {exc}")
                frames.append(old_rows)
        else:
            frames.append(merge_prices(old_rows, new_rows))

    if not frames:
        raise RuntimeError("No ticker data available")

    # Preserve any older tickers not in the current universe
    extra_tickers = old[~old["ticker"].isin(tickers)]
    if not extra_tickers.empty:
        frames.append(extra_tickers)

    return pd.concat(frames, ignore_index=True)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--full",
        action="store_true",
        help="Download full historical data",
    )

    args = parser.parse_args()

    tickers = STOCKS + [BENCHMARK]

    if args.full:
        data = download_all(tickers)
        old_rows = 0
    else:
        path = Path("data/prices.csv")
        old_rows = len(pd.read_csv(path)) if path.exists() else 0
        data = update_prices(path)

    out = Path("data/prices.csv")
    out.parent.mkdir(parents=True, exist_ok=True)

    data.to_csv(out, index=False)

    print(f"Saved {len(data)} rows to {out}")
    print(f"Tickers: {data['ticker'].nunique()}")
    print(f"Rows added/changed: {len(data) - old_rows}")




if __name__=="__main__":
    main()


    

    
