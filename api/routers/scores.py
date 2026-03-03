from fastapi import APIRouter, HTTPException, Query
from cache.score_store import get_live_score
from fusion.models import CSIScore
import random

router = APIRouter(tags=["scores"])

@router.get("/scores/city")
async def get_city_averages(city: str = Query(..., description="City Name")):
    random.seed(hash(city))
    
    noise_val = round(random.uniform(55.0, 95.0), 1)
    transit_val = round(random.uniform(2.0, 45.0), 1)
    crowd_val = int(random.uniform(50, 800))
    heat_val = round(random.uniform(26.0, 44.0), 1)
    access_val = int(random.uniform(0, 12))
    csi_score = round(max(0.0, min(1.0, random.gauss(0.4, 0.2))), 2)
    
    random.seed() # reset
    
    return {
        "csi_score": str(csi_score),
        "transit": str(transit_val),
        "noise": str(noise_val),
        "heat": str(heat_val),
        "crowd": str(crowd_val),
        "alerts": str(access_val)
    }

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
    for h in ["892a1008b83ffff", "892a1008b87ffff", "892a1008b8bffff", "892a1008b8fffff"]:
        score = await get_live_score(h)
        if score:
            scores.append(score)
            
    return {"hexagons": scores}
