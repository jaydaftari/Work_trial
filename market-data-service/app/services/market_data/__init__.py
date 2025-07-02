from .alphavantage import AlphaVantageFetcher
from .yfinance_fetcher import YahooFinanceFetcher
from .finhub import FinnhubFetcher

PROVIDER_MAP = {
    "alpha_vantage": AlphaVantageFetcher(),
    "yahoo_finance": YahooFinanceFetcher(),
    "finnhub": FinnhubFetcher(),
}


async def get_market_data(symbol: str, provider: str = None) -> dict:
    print("inside get market data")
    if provider:
        print("inside provider")
        fetcher = PROVIDER_MAP.get(provider.lower())
        if not fetcher:
            raise ValueError(f"Unsupported provider: {provider}")
        try:
            print("inside try")
            data = await fetcher.fetch(symbol)

            if data and data.get("price", 0) > 0:
                data["provider"] = provider
                print("data::", data)
                return data
            else:
                raise Exception(f"No valid data from provider {provider}")
        except Exception as e:
            raise Exception(f"Fetcher {provider} failed: {e}")
    else:
        # Try all providers until one works
        for name, fetcher in PROVIDER_MAP.items():
            try:
                data = await fetcher.fetch(symbol)
                if data and data.get("price", 0) > 0:
                    data["provider"] = name
                    return data
            except Exception as e:
                print(f"[WARN] Fetcher {name} failed: {e}")
        raise Exception("All market data fetchers failed.")
