import yfinance as yf
from app.services.market_data.base import MarketDataFetcher
from datetime import datetime, timezone
from app.services.kafka.producer import send_price_data


class YahooFinanceFetcher(MarketDataFetcher):
    async def fetch(self, symbol: str) -> dict:
        ticker = yf.Ticker(symbol)
        price = ticker.info.get("currentPrice") or ticker.info.get(
            "regularMarketPrice", 0.0
        )
        print("raw-data", ticker.info)
        price: float(price)
        send_price_data("price-events", ticker.info, symbol, "yahoo_finance", price)

        return {
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc),
            "price": price,
        }
