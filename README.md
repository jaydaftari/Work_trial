# Work_trial

# 📈 Market Data Service

A production-ready **microservice** built with **FastAPI**, **PostgreSQL**, and **Kafka** that fetches live market data, streams it through a processing pipeline, and exposes REST APIs for clients.

---

## 🚀 Features
- **GET Latest Price** – Fetch current price for a given symbol (with optional provider).
- **POST Polling Job** – Schedule periodic fetching of prices for one or more symbols.
- **Kafka Streaming Pipeline** – Producers publish raw price events, consumers compute 5-point moving averages.
- **Stop Polling Job** – Gracefully stop active polling requests.
- **Persistent Storage** – PostgreSQL stores raw data, polling jobs, price points, and moving averages.

---

## 🏗️ Architecture

     ┌─────────────┐
     │   Client    │
     └──────┬──────┘
            │ REST APIs
            ▼
    ┌─────────────────┐
    │   FastAPI API   │
    └──────┬──────────┘
           │ produces
           ▼
     ┌─────────────┐
     │   Kafka     │
     └──────┬──────┘
            │ consumes
            ▼
    ┌─────────────────┐
    │  MA Consumer    │
    │  (5-point avg)  │
    └──────┬──────────┘
           │ writes
           ▼
     ┌─────────────┐
     │ PostgreSQL  │
     └─────────────┘







API Contracts:
GET:

- **Producers** publish raw market data (`price-events` topic).
- **Consumers** calculate moving averages over the last 5 events per symbol.
- **Database** persists raw data, moving averages, polling jobs, and price points.

---

## ⚡ API Contracts

### 1. Get Latest Price
`GET /prices/latest?symbol=AAPL&provider=alpha_vantage`

**Request:**  
Query params: `symbol` (required), `provider` (optional)

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 201.08,
  "timestamp": "2025-06-30T18:42:40.248708Z",
  "provider": "alpha_vantage"
}


POST:
http://0.0.0.0:8000/prices/poll

Req:{
  "symbols": ["AAPL", "MSFT"],
  "interval": 60,
  "provider": "alpha_vantage"
}

Res:{
    "job_id": "8e858090-5ffe-483b-a49b-2a9bba9a395e",
    "status": "accepted",
    "config": {
        "symbols": [
            "AAPL",
            "MSFT"
        ],
        "interval": 60
    }
}

http://0.0.0.0:8000/prices/stop

Req:{"job_id":"8e858090-5ffe-483b-a49b-2a9bba9a395e"}
Res:{
    "status": "stopped",
    "job_id": "8e858090-5ffe-483b-a49b-2a9bba9a395e"
}


How to run:
docker compose up --build

To check Data in postgres using docker:
docker exec -it marketdata_postgres psql -U postgres -d marketdata
Then, just use then plsql commands



Tables on Postgres:
raw_market_data
poll_jobs
symbol_averages
price_points


Dependency:
Alpha_Vantage
finhub
yfinance
