import httpx
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from app.services.market_data.base import MarketDataFetcher
from app.services.kafka.producer import send_price_data


class AlphaVantageFetcher(MarketDataFetcher):
    async def fetch(self, symbol: str) -> dict:
        load_dotenv()
        API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
        url = "https://www.alphavantage.co/query"
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": API_KEY}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            print("data", data)
            quote = data.get("Global Quote", {})
            price = float(quote.get("05. price", 0.0))
            send_price_data("price-events", data, symbol, "alpha_vantage", price)
            return {
                "symbol": symbol,
                "timestamp": datetime.now(timezone.utc),
                "price": price,
            }
