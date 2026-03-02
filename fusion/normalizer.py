def normalize_transit(minutes_delay: float) -> float:
    # 0 mins = 0.0, >= 60 mins = 1.0
    return min(max(minutes_delay / 60.0, 0.0), 1.0)

def normalize_noise(db: float) -> float:
    # < 50 dB = 0.0, >= 110 dB = 1.0
    return min(max((db - 50.0) / 60.0, 0.0), 1.0)

def normalize_crowd(density: float) -> float:
    # 0 = 0.0, >= 4.0 = 1.0
    return min(max(density / 4.0, 0.0), 1.0)

def normalize_heat(temp_above_avg: float) -> float:
    # 0 = 0.0, >= 10 = 1.0
    return min(max(temp_above_avg / 10.0, 0.0), 1.0)

def normalize_accessibility(outages: int) -> float:
    # 0 = 0.0, >= 5 = 1.0
    return min(max(outages / 5.0, 0.0), 1.0)

def normalize_signal(signal_type: str, value: float) -> float:
    """Delegates to specific signal normalizers ensuring outputs are [0.0 - 1.0]."""
    match signal_type:
        case "transit": return normalize_transit(value)
        case "noise": return normalize_noise(value)
        case "crowd": return normalize_crowd(value)
        case "heat": return normalize_heat(value)
        case "accessibility": return normalize_accessibility(value)
        case _: return 0.0
