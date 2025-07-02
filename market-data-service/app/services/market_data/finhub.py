import httpx
import os
from app.services.market_data.base import MarketDataFetcher
from datetime import datetime, timezone
from dotenv import load_dotenv
from app.services.kafka.producer import send_price_data


class FinnhubFetcher(MarketDataFetcher):
    async def fetch(self, symbol: str) -> dict:
        load_dotenv()
        API_KEY = os.getenv("FINNHUB_API_KEY")
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            price = float(data.get("c", 0.0))  # c = current price
            send_price_data("price-events", data, symbol, "finnhub", price)

            print("raw data", data)
            return {
                "symbol": symbol,
                "timestamp": datetime.now(timezone.utc),
                "price": price,
            }
