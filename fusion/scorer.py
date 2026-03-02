from datetime import datetime, timezone
from typing import Literal
from fusion.models import CSIScore
from fusion.weights import weight_registry

def get_band(csi: float) -> Literal["low", "moderate", "high", "critical"]:
    """Returns stress band based on CSI thresholds."""
    if csi <= 0.25: return "low"
    if csi <= 0.50: return "moderate"
    if csi <= 0.75: return "high"
    return "critical"

def calculate_csi(hex_id: str, normalized_signals: dict[str, float]) -> CSIScore:
    """Calculates the composite City Stress Index from normalized signals."""
    csi_value = 0.0
    contributions = {}
    
    total_expected_signals = 5.0
    presence_count = 0
    
    for sig_type, norm_value in normalized_signals.items():
        w = weight_registry.get_weight(sig_type)
        if w > 0:
            contribution = norm_value * w
            csi_value += contribution
            contributions[sig_type] = contribution
            presence_count += 1
            
    confidence = presence_count / total_expected_signals
    
    return CSIScore(
        hex_id=hex_id,
        csi=round(csi_value, 4),
        band=get_band(csi_value),
        signals=contributions,
        confidence=round(confidence, 2),
        computed_at=datetime.now(timezone.utc)
    )
