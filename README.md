# FinSight AI

> A team of AI analysts that debate, fact-check, and cite their way to an investment thesis on Indian stocks, with a public, honest track record.

> [!WARNING]
> **Not investment advice.** FinSight AI produces research theses for learning and discussion. It does not give buy/sell recommendations and is not registered with SEBI. Do your own research before making any investment decision.

**Status:** 🚧 In active development (Week 1 of 12, started 28 Sep 2026, target 20 Dec 2026)

---

## What it does

You ask about a stock, for example *"What's the case for Infosys right now?"*, and FinSight runs a small team of AI agents over real data:

1. **Market, News, and Fundamentals agents** gather prices, recent news, and financial statements.
2. **Bull and Bear researchers** each argue their side using that evidence.
3. **A Judge** weighs the debate and writes a thesis: bull case, bear case, risks, confidence, and what would change the view.
4. **A Fact-checker** re-verifies every number in the thesis against the database before you see it.

Every claim comes with a citation, and every number comes from code or the database, never from the LLM's memory.

## Standout features (planned)

| # | Feature | What it does |
|---|---------|--------------|
| 1 | **Red-flag detector** | Flags promoter pledging, auditor changes, related-party transactions, cash-flow vs profit gaps, and equity dilution. Computes Piotroski F-score and Beneish M-score. |
| 2 | **Management promise tracker** | Pulls guidance from earnings calls ("we expect 15% growth"), checks it against actual results, and gives management a credibility score. |
| 3 | **Thesis tracker** | Save a thesis, and FinSight turns it into checkable conditions (e.g. "operating margin > 20%") and alerts you when one breaks. |
| 4 | **Time machine replay** | "What would FinSight have said on date X?" shown next to what actually happened afterward. |
| 5 | **Agent scorecard** | Tracks each agent's accuracy over time; the orchestrator trusts better-performing agents more. |

Results are backed by a **leakage-aware backtest** against the Nifty 50 and a **live paper-trading log**, including the weak results.

## Scope

- **Universe:** 20 Nifty 50 stocks. Depth over breadth.
- **Data:** daily prices (yfinance `.NS`), fundamentals, shareholding and pledge data, news RSS, concall transcripts, and annual reports (PDF).
- **Point-in-time:** every data point is stored with an `as_of` date, so backtests and the Time Machine only see what was known at the time.

## Tech stack

| Layer | Tools |
|-------|-------|
| Language | Python |
| Data | pandas, yfinance, PostgreSQL, SQLAlchemy |
| Knowledge | pgvector, hybrid search (BM25 + vector), reranking |
| Agents | LangGraph |
| Backend | FastAPI, Pydantic |
| UI | Streamlit |
| Infra | Docker Compose, Redpanda (Kafka), Kubernetes (k3d/minikube), GitHub Actions |
| Observability | Langfuse, Prometheus, Grafana |

## Architecture

```
  Data sources                 Storage                 Agents (LangGraph)                 UI
 ┌─────────────┐          ┌──────────────┐     ┌────────────────────────────┐     ┌───────────┐
 │ Prices      │          │ PostgreSQL   │     │ Market · News · Fundamentals│     │ Streamlit │
 │ Fundamentals│──ingest─▶│  + as_of     │◀───▶│ Red Flag                    │────▶│ thesis +  │
 │ Shareholding│          │  + pgvector  │     │   ↓                         │     │ reasoning │
 │ News RSS    │          └──────────────┘     │ Bull ⇄ Bear → Judge         │     │ trace     │
 │ Filings/PDFs│                ▲              │   ↓                         │     └───────────┘
 └─────────────┘                │              │ Fact-checker → Orchestrator │
                             FastAPI ◀─────────└────────────────────────────┘
```

## Roadmap

| Week | Dates | Focus | Status |
|------|-------|-------|--------|
| 1 | 28 Sep – 4 Oct | Python setup, price downloader for 20 stocks | 🚧 In progress |
| 2 | 5 – 11 Oct | Postgres schema with point-in-time data | ⬜ |
| 3 | 12 – 18 Oct | FastAPI endpoints + Docker Compose | ⬜ |
| 4 | 19 – 25 Oct | Single Analyst LLM with tool calling | ⬜ |
| 5 | 26 Oct – 1 Nov | RAG over news and filings | ⬜ |
| 6 | 2 – 8 Nov | Multi-agent debate system (**MVP**) | ⬜ |
| 7 | 9 – 15 Nov | Red-flag detector | ⬜ |
| 8 | 16 – 22 Nov | Management promise tracker | ⬜ |
| 9 | 23 – 29 Nov | Time machine + honest backtesting | ⬜ |
| 10 | 30 Nov – 6 Dec | Agent scorecard + thesis tracker | ⬜ |
| 11 | 7 – 13 Dec | Kafka streaming, Kubernetes, CI/CD | ⬜ |
| 12 | 14 – 20 Dec | Polish, demo video, write-up | ⬜ |

## Getting started

Setup instructions will be added as the code lands. The first milestone (Week 1) is a single command that downloads 5 years of daily prices for the 20 stocks to CSV and plots a basic price chart.

Planned local setup:

```bash
git clone https://github.com/<your-username>/finsight-ai.git
cd finsight-ai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

API keys go in a local `.env` file, which is never committed.

## Design principles

1. **Numbers come from code or the database, never from the LLM's memory.**
2. **Everything is point-in-time.** Data is stored with `as_of` dates, and history is never overwritten.
3. **Honest results.** Backtests account for look-ahead bias, survivorship bias, and LLM training-data leakage, and weak results are published too.
4. **Research, not advice.** Output is framed as a thesis with a disclaimer, in line with SEBI rules.

## Author

**Mudit Golchha**,**Niharika Gupta ** NIT Jalandhar
