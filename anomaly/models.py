from datetime import datetime
from typing import Literal
from pydantic import BaseModel

class AnomalyEvent(BaseModel):
    hex_id: str
    severity: Literal["WARN", "HIGH"]
    csi_current: float
    csi_baseline: float
    deviation_score: float
    triggered_signals: list[str]
    timestamp: datetime
    city: str
