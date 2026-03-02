from datetime import datetime
from typing import Literal
from pydantic import BaseModel

class CSIScore(BaseModel):
    hex_id: str
    csi: float                        # 0.0–1.0
    band: Literal["low", "moderate", "high", "critical"]
    signals: dict[str, float]         # normalized per-signal contribution
    confidence: float                 # 1.0 = all 5 signals present
    computed_at: datetime
