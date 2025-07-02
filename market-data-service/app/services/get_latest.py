from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone

from app.models.price_point import PricePoint
from app.schemas.price import PriceResponse
from app.services.market_data import get_market_data

LATENCY_LIMIT = timedelta(seconds=1)


async def get_latest_price(
    symbol: str, provider: str = None, db: AsyncSession = None
) -> PriceResponse:

    if not db:
        raise ValueError("DB session is required")

    # Fetch by symbol and optional provider
    query = select(PricePoint).where(PricePoint.symbol == symbol)

    if provider:
        query = query.where(PricePoint.provider == provider)

    result = await db.execute(query)
    price_obj = result.scalars().first()

    now = datetime.now(timezone.utc)
    aware_timezone = (
        price_obj.timestamp.replace(tzinfo=timezone.utc) if price_obj else None
    )
    if price_obj and (now - aware_timezone <= LATENCY_LIMIT):
        return PriceResponse(
            symbol=price_obj.symbol,
            price=price_obj.price,
            timestamp=price_obj.timestamp.isoformat(),
            provider=price_obj.provider,
        )

    # Cache miss — fetch fresh data
    fresh_data = await get_market_data(symbol, provider)
    print("fresh data:", fresh_data)

    if price_obj:
        # Update existing record
        price_obj.price = fresh_data["price"]
        price_obj.timestamp = fresh_data["timestamp"]
    else:
        # Insert new record
        print("inseting..")
        price_obj = PricePoint(
            symbol=fresh_data["symbol"],
            price=fresh_data["price"],
            timestamp=fresh_data["timestamp"],
            provider=fresh_data["provider"],
        )
        db.add(price_obj)

    await db.commit()
    print("inseted..")

    return PriceResponse(
        symbol=price_obj.symbol,
        price=price_obj.price,
        timestamp=price_obj.timestamp.isoformat(),
        provider=price_obj.provider,
    )
