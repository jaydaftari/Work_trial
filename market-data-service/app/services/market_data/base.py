from abc import ABC, abstractmethod


class MarketDataFetcher(ABC):
    @abstractmethod
    async def fetch(self, symbol: str) -> dict:
        pass
