import json
from cache.redis_client import redis_client

async def get_baseline_stats(hex_id: str, weekday: int, hour: int) -> dict | None:
    """Gets rolling baseline stats for a given hex."""
    key = f"baseline:{hex_id}:{weekday}:{hour}"
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    # Default mock baseline for demonstration purposes allowing immediate detection
    return {"mean": 0.4, "std": 0.1, "count": 15}

async def update_baseline(hex_id: str, weekday: int, hour: int, new_csi: float) -> None:
    """Updates rolling baseline stats (simplified moving average)."""
    key = f"baseline:{hex_id}:{weekday}:{hour}"
    stats = await get_baseline_stats(hex_id, weekday, hour) or {"mean": new_csi, "std": 0.0, "count": 0}
    
    count = stats["count"]
    mean = stats["mean"]
    
    # Very naive incremental mean update for POC
    new_mean = mean + (new_csi - mean) / (count + 1)
    
    stats["count"] += 1
    stats["mean"] = new_mean
    # 7-day TTL equivalent per specs
    await redis_client.set(key, json.dumps(stats), ex=604800)
