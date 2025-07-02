import asyncio
from app.services.market_data import get_market_data
from app.services.kafka.producer import (
    send_price_data,
)  # Assuming this wraps aiokafka producer
import logging

logging.basicConfig(level=logging.INFO)

TICKERS = ["AAPL", "GOOG", "MSFT"]  # Current List


async def job(ticker: str):
    try:
        logging.info(f"Fetching market data for {ticker}...")
        data = await get_market_data(ticker)
        if data:
            await send_price_data("market-data", data)
            logging.info(f"Sent data for {ticker} to Kafka.")
        else:
            logging.warning(f"No data fetched for {ticker}.")
    except Exception as e:
        logging.error(f"Error fetching/sending data for {ticker}: {e}")


async def main_loop():
    while True:
        for ticker in TICKERS:
            await job(ticker)
            await asyncio.sleep(
                12
            )  # Wait 12 seconds to respect Alpha Vantage free tier
        logging.info("Cycle complete. Restarting...")


if __name__ == "__main__":
    asyncio.run(main_loop())
