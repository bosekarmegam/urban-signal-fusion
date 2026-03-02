from fusion.normalizer import normalize_transit, normalize_noise, normalize_signal

def test_normalize_transit():
    assert normalize_transit(0) == 0.0
    assert normalize_transit(30) == 0.5
    assert normalize_transit(60) == 1.0
    assert normalize_transit(120) == 1.0

def test_normalize_noise():
    assert normalize_noise(50) == 0.0
    assert normalize_noise(80) == 0.5
    assert normalize_noise(110) == 1.0
    assert normalize_noise(30) == 0.0

def test_normalize_signal_delegation():
    assert normalize_signal("transit", 60) == 1.0
    assert normalize_signal("unknown", 100) == 0.0
