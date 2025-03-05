from fastapi import APIRouter, HTTPException, Request, Depends, status
from app.exceptions import UserNotAuthorizedException
from app.utils.security import verify_api_key
from app.utils.rate_limiter import rate_limit
from app.utils.helpers import is_authorized
from app.config import settings
import asyncio
import psutil
import time
import os

router = APIRouter()

@router.get(
    "/stats",
    summary="Retrieve system metrics and global statistics",
    tags=["Status"]
)
@rate_limit
async def get_status(request: Request, user: dict = Depends(verify_api_key)):
    if not is_authorized(user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(UserNotAuthorizedException("User is not authorized to get statistics."))
        )

    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_frequency = {
            "current": cpu_freq.current if cpu_freq else None,
            "min": cpu_freq.min if cpu_freq else None,
            "max": cpu_freq.max if cpu_freq else None
        }

        try:
            load_average = list(os.getloadavg())
        except (AttributeError, OSError):
            load_average = []

        memory = psutil.virtual_memory()
        total_memory = round(memory.total / (1024 * 1024), 2)
        used_memory = round(memory.used / (1024 * 1024), 2)
        memory_percent = memory.percent

        disk = psutil.disk_usage("/")
        disk_total = round(disk.total / (1024 ** 3), 2)
        disk_used = round(disk.used / (1024 ** 3), 2)
        disk_free = round(disk.free / (1024 ** 3), 2)
        disk_percent = disk.percent

        process_count = len(psutil.pids())
        net_io = psutil.net_io_counters()
        net_io_data = {"bytes_sent": net_io.bytes_sent, "bytes_recv": net_io.bytes_recv}

        uptime_seconds = time.time() - psutil.Process().create_time()

        db = request.app.state.db
        total_users_future = db[settings.API_KEYS_COLLECTION].count_documents({})
        total_images_future = db[settings.IMAGES_COLLECTION].count_documents({})
        total_users, total_images = await asyncio.gather(total_users_future, total_images_future)

        stats_doc = await db["stats"].find_one({"_id": "global"})
        total_requests = stats_doc.get("totalRequests", 0) if stats_doc else 0

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving system metrics: {e}"
        )

    return {
        "cpu_usage": cpu_usage,
        "cpu_count": cpu_count,
        "cpu_frequency": cpu_frequency,
        "load_average": load_average,
        "total_memory": total_memory,
        "used_memory": used_memory,
        "memory_percent": memory_percent,
        "disk_total": disk_total,
        "disk_used": disk_used,
        "disk_free": disk_free,
        "disk_percent": disk_percent,
        "process_count": process_count,
        "net_io": net_io_data,
        "globalStats": {
            "totalRequests": total_requests,
            "totalUsers": total_users,
            "totalImages": total_images
        },
        "timestamp": time.time(),
        "uptime": uptime_seconds
    }