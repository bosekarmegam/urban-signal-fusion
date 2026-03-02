from fastapi import APIRouter
from cache.snapshot_store import get_hourly_snapshot

router = APIRouter(tags=["history"])

@router.get("/history/{hex_id}")
async def get_history(hex_id: str, from_date: str, to_date: str, interval: str = "1h"):
    # Pseudo-history implementation fetching via hourly mock snapshot
    snapshot = await get_hourly_snapshot(hex_id, 0)
    timeseries = []
    if snapshot:
        timeseries.append(snapshot)
        
    return {
        "hex_id": hex_id,
        "timeseries": timeseries
    }
