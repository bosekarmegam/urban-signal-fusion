from datetime import datetime, timezone
import structlog
from anomaly.models import AnomalyEvent
from fusion.models import CSIScore
from anomaly.baseline_builder import get_baseline_stats
from config.settings import settings

logger = structlog.get_logger()

async def detect_anomaly(score: CSIScore) -> AnomalyEvent | None:
    """Runs Z-score detection against rolling baselines."""
    dt = score.computed_at
    weekday = dt.weekday()
    hour = dt.hour
    
    baseline = await get_baseline_stats(score.hex_id, weekday, hour)
    
    # Minimum 14 days of history required before detection activates
    if not baseline or baseline.get("count", 0) < 14:
        return None
        
    mean = baseline["mean"]
    std = max(baseline["std"], 0.01) # Avoid div by zero
        
    deviation = (score.csi - mean) / std
    
    severity = None
    if abs(deviation) > 2.5:
        severity = "HIGH"
    elif abs(deviation) > 1.8:
        severity = "WARN"
        
    if severity:
        logger.info("Anomaly detected", hex_id=score.hex_id, deviation=deviation, severity=severity)
        return AnomalyEvent(
            hex_id=score.hex_id,
            severity=severity,
            csi_current=round(score.csi, 4),
            csi_baseline=round(mean, 4),
            deviation_score=round(deviation, 2),
            triggered_signals=list(score.signals.keys()),
            timestamp=datetime.now(timezone.utc),
            city=settings.city
        )
        
    return None
