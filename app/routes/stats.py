from fastapi import APIRouter, Request, HTTPException, status, Depends
from app.utils.security import verify_api_key
from app.config import settings
import psutil
import time
import os

router = APIRouter()

@router.get(
    "/stats",
    summary="Retrieve application consumption and system statistics as JSON",
    tags=["Status"]
)
async def get_status(request: Request, user: dict = Depends(verify_api_key)):
    """
    Retrieves the current resource consumption and system statistics, including:
      - CPU usage (percentage over a 1-second interval)
      - CPU count (number of cores)
      - Load average (1, 5, 15 minutes; if available)
      - Memory usage (total and used in MB, and percentage)
      - Disk usage for the root filesystem (total, used, free in GB, and percentage)
      - Process count (number of active processes)
      - Current timestamp

    This endpoint is restricted to authorized users (those allowed to post images).

    **Returns:**
      A JSON object with keys:
        - cpu_usage
        - cpu_count
        - load_average (list of floats or an empty list if not available)
        - total_memory (in MB)
        - used_memory (in MB)
        - memory_percent
        - disk_total (in GB)
        - disk_used (in GB)
        - disk_free (in GB)
        - disk_percent
        - process_count
        - timestamp

    **Raises:**
      - HTTPException (403) if the user is not authorized.
      - HTTPException (500) if there is an error retrieving system metrics.
    """
    # Ensure the user is authorized to access status.
    if user["username"] not in settings.ALLOWED_POST_USERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to access status."
        )

    try:
        # CPU metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=True)

        # Load average (available on Unix systems)
        try:
            load_avg = os.getloadavg()  # Returns a tuple: (1-min, 5-min, 15-min)
            load_average = list(load_avg)
        except (AttributeError, OSError):
            load_average = []

        # Memory metrics in MB
        memory = psutil.virtual_memory()
        total_memory = round(memory.total / (1024 * 1024), 2)
        used_memory = round(memory.used / (1024 * 1024), 2)
        memory_percent = memory.percent

        # Disk usage metrics for root directory (in GB)
        disk = psutil.disk_usage("/")
        disk_total = round(disk.total / (1024**3), 2)
        disk_used = round(disk.used / (1024**3), 2)
        disk_free = round(disk.free / (1024**3), 2)
        disk_percent = disk.percent

        # Number of processes
        process_count = len(psutil.pids())

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving system metrics: {e}"
        )

    return {
        "cpu_usage": cpu_usage,
        "cpu_count": cpu_count,
        "load_average": load_average,
        "total_memory": total_memory,
        "used_memory": used_memory,
        "memory_percent": memory_percent,
        "disk_total": disk_total,
        "disk_used": disk_used,
        "disk_free": disk_free,
        "disk_percent": disk_percent,
        "process_count": process_count,
        "timestamp": time.time()
    }