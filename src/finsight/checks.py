
"""Sanity-check data/prices.csv and draw the growth chart."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from finsight.universe import STOCKS, BENCHMARK

PRICES_FILE = Path("data/prices.csv")
CHART_FILE = Path("data/growth_of_100.png")


def load_prices(path: Path = PRICES_FILE) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])


def run_checks(data: pd.DataFrame) -> None:
    """Summarize the data and report suspicious records."""

    summary = data.groupby("ticker").agg(
        rows=("date", "count"),
        first_day=("date", "min"),
        last_day=("date", "max"),
        missing_close=("close", lambda s: s.isna().sum()),
    )

    print(summary.to_string(), "\n")

    problems = []

    expected_tickers = set(STOCKS) | {BENCHMARK}
    missing = expected_tickers - set(data["ticker"])

    if missing:
        problems.append(f"Missing tickers: {sorted(missing)}")

    if data["close"].isna().any():
        problems.append("Some closing prices are missing")

    if (data["close"].dropna() <= 0).any():
        problems.append("Some close prices are zero or negative")

    bad_range = (
        (data["close"] > data["high"])
        | (data["close"] < data["low"])
    )

    if bad_range.any():
        problems.append(
            f"{bad_range.sum()} rows have close outside the low-high range"
        )

    if data.duplicated(subset=["date", "ticker"]).any():
        problems.append("Duplicate (date, ticker) rows")

    if not summary.empty:
        short = summary[
            summary["rows"] < 0.9 * summary["rows"].median()
        ]

        if not short.empty:
            problems.append(
                f"Tickers with too little history: {list(short.index)}"
            )

    if problems:
        print("PROBLEMS:")
        for problem in problems:
            print(f"- {problem}")
    else:
        print("All checks passed.")


def plot_growth_of_100(data: pd.DataFrame) -> None:
    """Plot the growth of Rs 100 using adjusted closing prices."""

    wide = data.pivot(
        index="date",
        columns="ticker",
        values="adj_close",
    )

    growth = wide / wide.bfill().iloc[0] * 100

    stocks = growth.drop(columns=[BENCHMARK], errors="ignore")

    fig, ax = plt.subplots(figsize=(12, 7))
    stocks.plot(ax=ax, linewidth=0.8, alpha=0.5, legend=False)

    if BENCHMARK in growth.columns:
        growth[BENCHMARK].plot(
            ax=ax,
            color="black",
            linewidth=2.5,
            label="Nifty 50",
        )
        ax.legend(loc="upper left")

    ax.set_title("Growth of Rs 100 over 5 years (adjusted close)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value (Rs)")

    fig.tight_layout()

    CHART_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(CHART_FILE, dpi=120)
    print(f"Chart saved -> {CHART_FILE}")

    plt.show()
    plt.close(fig)


def main() -> None:
    data = load_prices()
    run_checks(data)
    plot_growth_of_100(data)


if __name__ == "__main__":
    main()