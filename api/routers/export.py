from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

router = APIRouter(tags=["export"])

@router.post("/export")
async def export_data(
    hex_ids: list[str] = Body(..., embed=True),
    format: str = Body("geojson", embed=True),
    include_signals: bool = Body(False, embed=True)
):
    if format == "geojson":
        return JSONResponse(content={"type": "FeatureCollection", "features": []})
    return {"message": "Export formats other than geojson are mock unimplemented."}
