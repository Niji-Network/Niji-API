from app.exceptions import RateLimitExceededException
from fastapi import HTTPException, Request, status
from typing import Any, Callable
from app.config import settings
import redis.asyncio as redis
import functools
import time

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

MINUTE_SECONDS = 60
DAY_SECONDS = 86400

def rate_limit(endpoint_func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(endpoint_func)
    async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
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

        now = time.time()
        minute_window = int(now // MINUTE_SECONDS)
        day_window = int(now // DAY_SECONDS)

        minute_key = f"rate_limit:{api_key}:minute:{minute_window}"
        day_key = f"rate_limit:{api_key}:day:{day_window}"

        minute_count = await redis_client.incr(minute_key)
        if minute_count == 1:
            await redis_client.expire(minute_key, MINUTE_SECONDS + 1)
        if minute_count > settings.RATE_LIMIT_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(RateLimitExceededException("Per-minute rate limit exceeded."))
            )

        day_count = await redis_client.incr(day_key)
        if day_count == 1:
            await redis_client.expire(day_key, DAY_SECONDS + 1)
        if day_count > settings.RATE_LIMIT_DAY:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(RateLimitExceededException("Daily rate limit exceeded."))
            )

        return await endpoint_func(request, *args, **kwargs)

    return wrapper