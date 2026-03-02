import pytest
from datetime import datetime, timezone
from fusion.models import CSIScore
from anomaly.detector import detect_anomaly
from unittest.mock import patch

@pytest.mark.asyncio
@patch('anomaly.detector.get_baseline_stats')
async def test_detect_anomaly_high(mock_get_baseline):
    mock_get_baseline.return_value = {"mean": 0.2, "std": 0.1, "count": 15}
    
    score = CSIScore(
        hex_id="892a1008983ffff",
        csi=0.8,
        band="critical",
        signals={"transit": 0.2},
        confidence=1.0,
        computed_at=datetime.now(timezone.utc)
    )
    
    anomaly = await detect_anomaly(score)
    assert anomaly is not None
    assert anomaly.severity == "HIGH"
    # deviation = (0.8 - 0.2) / 0.1 = 6.0
    assert anomaly.deviation_score == 6.0

@pytest.mark.asyncio
@patch('anomaly.detector.get_baseline_stats')
async def test_detect_anomaly_insufficient_history(mock_get_baseline):
    mock_get_baseline.return_value = {"mean": 0.2, "std": 0.1, "count": 10}
    score = CSIScore(
        hex_id="892a1008983ffff", csi=0.8, band="critical",
        signals={}, confidence=1.0, computed_at=datetime.now(timezone.utc)
    )
    anomaly = await detect_anomaly(score)
    assert anomaly is None
