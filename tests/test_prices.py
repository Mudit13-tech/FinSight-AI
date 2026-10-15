
import pandas as pd

from finsight.prices import merge_prices, adjustment_changed
from unittest.mock import patch


def make_rows(dates, adj_closes):
    return pd.DataFrame({
        "date": dates,
        "ticker": ["TCS.NS"] * len(dates),
        "open": [100.0] * len(dates),
        "high": [110.0] * len(dates),
        "low": [90.0] * len(dates),
        "close": [105.0] * len(dates),
        "adj_close": adj_closes,
        "volume": [1000] * len(dates),
        "as_of": ["2026-10-15"] * len(dates),
    })


def test_merge_prices_removes_duplicates_and_keeps_new_row():
    old = make_rows(["2026-10-13"], [100.0])
    new = make_rows(["2026-10-13", "2026-10-14"], [101.0, 102.0])

    result = merge_prices(old, new)

    assert len(result) == 2
    assert result.iloc[0]["adj_close"] == 101.0


def test_adjustment_changed_returns_false_when_prices_match():
    old = make_rows(["2026-10-13"], [100.0])
    new = make_rows(["2026-10-13"], [100.0])

    assert adjustment_changed(old, new) is False


def test_adjustment_changed_returns_true_when_prices_change():
    old = make_rows(["2026-10-13"], [100.0])
    new = make_rows(["2026-10-13"], [102.0])

    assert adjustment_changed(old, new) is True


def test_update_prices_keeps_old_data_when_download_fails(tmp_path):
    from finsight.prices import update_prices

    old = make_rows(["2026-10-14"], [100.0])
    path = tmp_path / "prices.csv"
    old.to_csv(path, index=False)

    with patch("finsight.prices.download_one", side_effect=RuntimeError("Network error")):
        result = update_prices(path)

    assert len(result) == 1
    assert result.iloc[0]["ticker"] == "TCS.NS"


def test_update_prices_adds_new_day(tmp_path):
    from finsight.prices import update_prices, STOCKS, BENCHMARK

    tickers = STOCKS + [BENCHMARK]
    old_frames = []

    for ticker in tickers:
        old = make_rows(["2026-10-14"], [100.0])
        old["ticker"] = ticker
        old_frames.append(old)

    old_data = pd.concat(old_frames, ignore_index=True)
    path = tmp_path / "prices.csv"
    old_data.to_csv(path, index=False)

    def fake_download(ticker, period="5y", start=None):
        if start is not None:
            return make_rows(
                ["2026-10-14", "2026-10-15"],
                [100.0, 101.0],
            ).assign(ticker=ticker)
        return make_rows(
            ["2026-10-14", "2026-10-15"],
            [100.0, 101.0],
        ).assign(ticker=ticker)

    with patch("finsight.prices.download_one", side_effect=fake_download):
        with patch("finsight.prices.adjustment_changed", return_value=False):
            result = update_prices(path)

    assert len(result) == len(tickers) * 2
    assert result.groupby("ticker").size().eq(2).all()


def test_update_prices_redownloads_full_history_when_adjustment_changes(tmp_path):
    from finsight.prices import update_prices, STOCKS, BENCHMARK

    tickers = STOCKS + [BENCHMARK]
    old_frames = []

    for ticker in tickers:
        old = make_rows(["2026-10-14"], [100.0])
        old["ticker"] = ticker
        old_frames.append(old)

    old_data = pd.concat(old_frames, ignore_index=True)
    path = tmp_path / "prices.csv"
    old_data.to_csv(path, index=False)

    calls = []

    def fake_download(ticker, period="5y", start=None):
        calls.append((ticker, start))

        if start is not None:
            return make_rows(["2026-10-14"], [102.0]).assign(ticker=ticker)

        return make_rows(
            ["2026-10-13", "2026-10-14"],
            [99.0, 102.0],
        ).assign(ticker=ticker)

    with patch("finsight.prices.download_one", side_effect=fake_download):
        with patch("finsight.prices.adjustment_changed", return_value=True):
            result = update_prices(path)

    assert len(result) == len(tickers) * 2
    assert any(start is None for _, start in calls)



