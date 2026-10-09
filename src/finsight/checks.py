import pandas as pd
from pathlib import Path
from finsight.universe import STOCKS, BENCHMARK
import matplotlib.pyplot as plt


def load_prices(path: Path = Path("data/prices.csv")) -> pd.DataFrame:
    return pd.read_csv(path)

def run_checks(data: pd.DataFrame) -> None:
    unique = data["ticker"].unique()
    tickers = STOCKS + [BENCHMARK]

    for ticker in tickers:
        if ticker not in unique:
            raise ValueError(f"Missing ticker: {ticker}")


    if (data["close"] <= 0).any():
        raise ValueError("Invalid close price")


    if ((data["close"] > data["high"]).any()or (data["close"] < data["low"]).any()):
        raise ValueError("Close price outside low-high range")
    
    if data.duplicated(subset=["date", "ticker"]).any():
        raise ValueError("Duplicate date-ticker rows found")

    counts = data["ticker"].value_counts()
    median_rows = counts.median()

    if (counts < median_rows / 2).any():
        raise ValueError("Some tickers have too few rows")
    
    print("All checks passed.")

def plot_growth_of_100(data: pd.DataFrame) -> None:
    wide = data.pivot(
    index="date",
    columns="ticker",
    values="adj_close"
    )
    growth = wide.div(wide.iloc[0]).mul(100)
    ax = growth.plot(figsize=(14, 7), alpha=0.6)
    ax.plot(
    growth.index,
    growth["^NSEI"],
    color="black",
    linewidth=3,
    label="Nifty 50"
    )
    ax.set_title("Growth of ₹100: Stocks vs Nifty 50")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value of ₹100")
    ax.legend(loc="best")
    plt.tight_layout()
    plt.show()

    out = Path("data/growth_of_100.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    data = load_prices()
    run_checks(data)
    plot_growth_of_100(data)
