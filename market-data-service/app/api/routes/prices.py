from fastapi import APIRouter, Depends, HTTPException
from app.schemas.price import (
    PriceResponse,
    PollRequest,
    PollAcceptedResponse,
    StopRequest,
)
from app.services.poll_scheduler import schedule_polling_job, stop_polling_job
from app.services.get_latest import get_latest_price
from app.models.poll_job import PollJob
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter(prefix="/prices", tags=["Market Prices"])


@router.get("/latest", response_model=PriceResponse)
async def get_latest(
    symbol: str, provider: str | None, db: AsyncSession = Depends(get_db)
):
    try:
        data = await get_latest_price(symbol=symbol, provider=provider, db=db)
        # {"symbol": "AAPL","price": 150.25,"timestamp": "2024-03-20T10:30:00Z","provider": "alpha_vantage"}
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/poll", response_model=PollAcceptedResponse, status_code=202)
async def poll_market_data(request: PollRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Check if a job is already running
        result = await db.execute(select(PollJob).where(PollJob.status == "accepted"))
        existing_job = result.scalar_one_or_none()
        if existing_job:
            raise HTTPException(
                status_code=400, detail="A polling job is already running."
            )

        # Create new job in DB
        job = PollJob(
            symbols=",".join(request.symbols),
            interval=request.interval,
            provider=request.provider,
            status="accepted",
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        # Schedule polling job (direct async call, no thread/background task)
        await schedule_polling_job(
            symbols=request.symbols,
            interval=request.interval,
            provider=request.provider,
            job_id=str(job.id),
        )

        return PollAcceptedResponse(
            job_id=str(job.id),
            status="accepted",
            config={
                "symbols": request.symbols,
                "interval": request.interval,
            },
        )

    except HTTPException:
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_poll(request: StopRequest, db: AsyncSession = Depends(get_db)):
    try:
        await stop_polling_job(request.job_id, db)
        return {"status": "stopped", "job_id": request.job_id}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/poll", response_model=PollAcceptedResponse, status_code=202)
# async def poll_market_data(
#     request: PollRequest,
#     background_tasks: BackgroundTasks,
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         # Check if a job is already running
#         result = await db.execute(select(PollJob).where(PollJob.status == "accepted"))
#         existing_job = result.scalar_one_or_none()
#         if existing_job:
#             raise HTTPException(status_code=400, detail="A polling job is already running.") # Currently limiting it to one job

#         # Create new job
#         job = PollJob(
#             symbols=','.join(request.symbols),
#             interval=request.interval,
#             provider=request.provider,
#             status="accepted"
#         )
#         db.add(job)
#         await db.commit()
#         await db.refresh(job)

#         background_tasks.add_task(
#             schedule_polling_job,
#             request.symbols,
#             request.interval,
#             request.provider,
#             str(job.id),
#            # db
#         )

#         return PollAcceptedResponse(
#             job_id=str(job.id),
#             status="accepted",
#             config={
#                 "symbols": request.symbols,
#                 "interval": request.interval,
#             }
#         )
#     except HTTPException:
#         raise
#     except SQLAlchemyError as e:
#         await db.rollback()
#         raise HTTPException(status_code=500, detail="Database error")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/stop")
# async def stop_poll(request: StopRequest, db: AsyncSession = Depends(get_db)):
#     try:
#         await stop_polling_job(request.job_id, db)
#         return {"status": "stopped", "job_id": request.job_id}

#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
