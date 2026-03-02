from cache.redis_client import redis_client
from fusion.models import CSIScore

async def save_live_score(score: CSIScore) -> None:
    """Saves current CSI score with 60s TTL."""
    key = f"csi:live:{score.hex_id}"
    await redis_client.set(key, score.model_dump_json(), ex=60)

async def get_live_score(hex_id: str) -> CSIScore | None:
    """Retrieves current CSI score."""
    key = f"csi:live:{hex_id}"
    data = await redis_client.get(key)
    if data:
        return CSIScore.model_validate_json(data)
    return None
