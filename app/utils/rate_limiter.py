from app.exceptions import RateLimitExceededException  # Custom exception for rate limits
from fastapi import HTTPException, Request, status
from app.config import settings
import redis.asyncio as redis
import functools
import time

# Create a global asynchronous Redis client using the URL specified in settings.
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def rate_limit(endpoint_func):
    """
    Decorator to limit the number of requests for an endpoint using Redis.

    For each API key, two counters are maintained:
      - A per-minute counter (stored with key: "rate_limit:{api_key}:minute:{window_minute}")
      - A per-day counter (stored with key: "rate_limit:{api_key}:day:{window_day}")

    Each request increments these counters. The counters automatically expire after the
    duration of their respective windows (61 seconds for per-minute, 86461 seconds for per-day).

    If the counter exceeds the configured limits (RATE_LIMIT_MINUTE or RATE_LIMIT_DAY from settings),
    an HTTPException with status code 429 is raised, indicating that the rate limit has been exceeded.

    Args:
        endpoint_func (Callable): The endpoint function to decorate.

    Returns:
        Callable: The decorated function with rate limiting applied.

    Raises:
        HTTPException: If the request exceeds the per-minute or daily rate limits.
    """

    @functools.wraps(endpoint_func)
    async def wrapper(request: Request, *args, **kwargs):
        # Retrieve API key from request headers.
        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is required for rate limiting."
            )

        # Calculate current time windows.
        current_time = time.time()
        window_minute = int(current_time // 60)
        window_day = int(current_time // (60 * 60 * 24))

        # Construct Redis keys for the per-minute and per-day counters.
        minute_key = f"rate_limit:{api_key}:minute:{window_minute}"
        day_key = f"rate_limit:{api_key}:day:{window_day}"

        # Increment the per-minute counter and set expiration if new.
        minute_count = await redis_client.incr(minute_key)
        if minute_count == 1:
            await redis_client.expire(minute_key, 61)
        if minute_count > settings.RATE_LIMIT_MINUTE:
            raise HTTPException(
                status_code=429,
                detail=str(RateLimitExceededException("Per-minute rate limit exceeded."))
            )

        # Increment the per-day counter and set expiration if new.
        day_count = await redis_client.incr(day_key)
        if day_count == 1:
            await redis_client.expire(day_key, 86461)
        if day_count > settings.RATE_LIMIT_DAY:
            raise HTTPException(
                status_code=429,
                detail=str(RateLimitExceededException("Daily rate limit exceeded."))
            )

        # Proceed to call the endpoint function if rate limits are not exceeded.
        return await endpoint_func(request, *args, **kwargs)

    return wrapper