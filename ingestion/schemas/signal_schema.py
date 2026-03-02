from datetime import datetime
from typing import Literal
from pydantic import BaseModel

class SignalEvent(BaseModel):
    signal_type: Literal["transit", "noise", "crowd", "heat", "accessibility"]
    hex_id: str
    value: float
    unit: str
    source_id: str
    timestamp: datetime
