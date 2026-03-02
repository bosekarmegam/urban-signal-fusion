from fusion.scorer import calculate_csi, get_band
from fusion.weights import weight_registry

def test_get_band():
    assert get_band(0.1) == "low"
    assert get_band(0.3) == "moderate"
    assert get_band(0.6) == "high"
    assert get_band(0.9) == "critical"

def test_calculate_csi():
    # Mock weights
    weight_registry._weights = {
        "transit": 0.25,
        "noise": 0.20,
        "crowd": 0.20,
        "heat": 0.20,
        "accessibility": 0.15
    }
    
    normalized = {
        "transit": 1.0,
        "noise": 0.5,
        "crowd": 0.0
    }
    
    score = calculate_csi("892a1008983ffff", normalized)
    
    # csi = 1.0*0.25 + 0.5*0.20 + 0.0 = 0.35
    assert score.csi == 0.35
    assert score.band == "moderate"
    assert score.confidence == 0.6  # 3/5 signals present
