from app.exceptions import RateLimitExceededException
from fastapi import HTTPException, Request, status
from app.config import settings
import redis.asyncio as redis
import functools
import time

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def rate_limit(endpoint_func):
    @functools.wraps(endpoint_func)
    async def wrapper(request: Request, *args, **kwargs):
        user = kwargs.get("user")
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated."
            )

        if user.get("role", "user") == "admin":
            return await endpoint_func(request, *args, **kwargs)

        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is required for rate limiting."
            )

        current_time = time.time()
        window_minute = int(current_time // 60)
        window_day = int(current_time // (60 * 60 * 24))

        minute_key = f"rate_limit:{api_key}:minute:{window_minute}"
        day_key = f"rate_limit:{api_key}:day:{window_day}"

        minute_limit = settings.RATE_LIMIT_MINUTE
        day_limit = settings.RATE_LIMIT_DAY

        minute_count = await redis_client.incr(minute_key)
        if minute_count == 1:
            await redis_client.expire(minute_key, 61)
        if minute_count > minute_limit:
            raise HTTPException(
                status_code=429,
                detail=str(RateLimitExceededException("Per-minute rate limit exceeded."))
            )

        day_count = await redis_client.incr(day_key)
        if day_count == 1:
            await redis_client.expire(day_key, 86461)
        if day_count > day_limit:
            raise HTTPException(
                status_code=429,
                detail=str(RateLimitExceededException("Daily rate limit exceeded."))
            )

        return await endpoint_func(request, *args, **kwargs)

    return wrapper