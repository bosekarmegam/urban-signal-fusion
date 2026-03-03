from fusion.models import CSIScore
from cachetools import TTLCache

# Global TTL Cache instance mimicking Redis limits (1 minute TTL)
score_cache = TTLCache(maxsize=10000, ttl=60)

async def save_live_score(score: CSIScore) -> None:
    """Saves current CSI score with 60s TTL."""
    key = f"csi:live:{score.hex_id}"
    score_cache[key] = score

async def get_live_score(hex_id: str) -> CSIScore | None:
    """Retrieves current CSI score."""
    key = f"csi:live:{hex_id}"
    return score_cache.get(key)
