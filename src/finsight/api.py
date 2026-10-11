from fastapi import FastAPI
from finsight.universe import STOCKS, BENCHMARK
from pathlib import Path
import pandas as pd
from fastapi import HTTPException

DATA_FILE = Path("data/prices.csv")

app = FastAPI(
    title="FinSight AI API",
    description="API for Indian stock market research and analysis",
    version="0.1.0",
)

@app.get("/")
def home():
    return {
        "message": "Welcome to FinSight AI API",
        "status" : "Running",
    }

@app.get("/health")
def health():
    return {
        "status" : "OK"
    }

@app.get("/stocks")
def get_stocks():
    return{
        "count": len(STOCKS),
        "benchmark": BENCHMARK,
        "stocks": STOCKS
    }

@app.get("/prices/{ticker}")
def get_stock_prices(ticker:str):
    if ticker not in STOCKS and ticker != BENCHMARK:
        raise HTTPException(
            status_code=404,
            detail=f"Ticker not found. Valid tickers are {STOCKS} and {BENCHMARK}."
        )

    if not DATA_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail= "Data file is missing. Please run the 'scrape' command first."
        )

    data = pd.read_csv(DATA_FILE)
    stock_data = data[data["ticker"] == ticker]

    if stock_data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No price records found for {ticker}",
        )

    stock_data = stock_data.where(pd.notna(stock_data), None)

    return {
        "ticker": ticker,
        "count": len(stock_data),
        "prices": stock_data.to_dict(orient="records"),
    }
