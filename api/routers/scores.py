from fastapi import APIRouter, HTTPException, Query
from cache.score_store import get_live_score
from fusion.models import CSIScore
from ingestion.producers.mock_data import DEMO_HEX_IDS

router = APIRouter(tags=["scores"])

@router.get("/scores/{hex_id}", response_model=CSIScore)
async def get_score(hex_id: str):
    score = await get_live_score(hex_id)
    if not score:
        raise HTTPException(status_code=404, detail="Score not found or expired")
    return score

@router.get("/scores/region")
async def get_region_scores(
    bbox: str = Query(..., description="minLng,minLat,maxLng,maxLat"),
    resolution: int = Query(9, description="H3 resolution")
):
    scores = []
    # Mocking a region lookup
    for h in DEMO_HEX_IDS[:10]:
        score = await get_live_score(h)
        if score:
            scores.append(score)
            
    return {"hexagons": scores}
