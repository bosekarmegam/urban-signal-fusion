from cache.redis_client import redis_client
from fusion.models import CSIScore

async def save_hourly_snapshot(score: CSIScore, hour_epoch: int) -> None:
    """Saves CSI snapshot with 30d TTL."""
    key = f"csi:snapshot:{score.hex_id}:{hour_epoch}"
    # 30 days = 30 * 24 * 60 * 60 = 2592000 seconds
    await redis_client.set(key, score.model_dump_json(), ex=2592000)

async def get_hourly_snapshot(hex_id: str, hour_epoch: int) -> CSIScore | None:
    """Retrieves CSI snapshot for a specific hour."""
    key = f"csi:snapshot:{hex_id}:{hour_epoch}"
    data = await redis_client.get(key)
    if data:
        return CSIScore.model_validate_json(data)
    return None
