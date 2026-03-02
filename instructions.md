# urban-signal-fusion — IDE AI Instructions
> Multi-Modal City Stress Score Engine | v2.0 (upgraded from urban-pulse)

---

## Project Identity

**Name:** `urban-signal-fusion`
**Output:** Per-hexagon City Stress Index (CSI) map + REST API + real-time anomaly alerts
**Users:** City planners, urban researchers, municipal emergency services
**Philosophy:** Every block has a rhythm. Stress is when it breaks.

---

## Architecture Overview
```
Raw Signal Sources
    |
    v
[Kafka Topics]──────────────────────────────────────┐
  transit.delays                                     │
  noise.sensors                                      │
  crowd.density                                      ▼
  heat.island                            [Anomaly Detector]
  accessibility.events                    Baseline Comparator
    |                                     Z-score / IQR engine
    v                                     Alert publisher → Kafka
[Signal Fusion Engine]
  GeoPandas + H3 Indexing
  Per-hexagon normalization
  Weighted composite scorer
    |
    v
[Redis Cache]
  CSI keyed by H3 hex_id
  TTL: 60s (live) | 30d (snapshots)
    |
    |───────────────────────────┐
    v                           v
[FastAPI Backend]        [Streamlit Dashboard]
  REST + WebSocket          Live hexagon stress map
  City planner routes       Anomaly alert feed
  Historical queries        Time-slider replay
```

---

## Monorepo Structure
```
urban-signal-fusion/
├── .ai/
│   └── instructions.md
├── ingestion/
│   ├── producers/
│   │   ├── transit_producer.py   ← GTFS-RT → Kafka
│   │   ├── noise_producer.py     ← IoT sensors → Kafka
│   │   ├── crowd_producer.py     ← Pedestrian density → Kafka
│   │   ├── heat_producer.py      ← Weather/satellite → Kafka
│   │   └── access_producer.py   ← Elevator/ramp outages → Kafka
│   ├── consumers/
│   │   └── signal_consumer.py   ← Fused multi-topic consumer
│   └── schemas/
│       └── signal_schema.py     ← Pydantic models for all signals
├── fusion/
│   ├── h3_mapper.py             ← Lat/lon → H3 resolution 9
│   ├── normalizer.py            ← 0.0–1.0 per-signal normalization
│   ├── weights.py               ← Weight registry (loads from YAML)
│   ├── scorer.py                ← Composite CSI calculator
│   └── geo_aggregator.py       ← GeoPandas spatial joins & rollups
├── anomaly/
│   ├── baseline_builder.py      ← Rolling 30-day baseline per hex
│   ├── detector.py              ← Z-score + IQR deviation detector
│   ├── alert_publisher.py       ← Kafka alert publisher
│   └── models.py                ← AnomalyEvent Pydantic models
├── cache/
│   ├── redis_client.py
│   ├── score_store.py           ← Read/write CSI by H3 ID
│   └── snapshot_store.py       ← Hourly snapshot storage
├── api/
│   ├── main.py
│   └── routers/
│       ├── scores.py
│       ├── anomalies.py         ← REST + WebSocket /ws/alerts
│       ├── history.py
│       └── export.py            ← GeoJSON / CSV export
├── dashboard/
│   ├── app.py
│   └── components/
│       ├── hex_map.py           ← Pydeck H3HexagonLayer
│       ├── alert_feed.py
│       ├── signal_breakdown.py  ← Radar chart
│       └── time_slider.py
├── data/
│   ├── city_boundaries/         ← GeoJSON city boundaries
│   ├── hex_baseline/            ← Pre-computed baseline CSI
│   └── sample_feeds/            ← Mock signals for dev/testing
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── infra/
│   ├── docker-compose.yml       ← Kafka (KRaft) + Redis + services
│   ├── kafka/topics.sh
│   └── prometheus/
├── config/
│   ├── settings.py              ← Pydantic BaseSettings
│   └── signal_weights.yaml      ← Runtime-editable weights
└── pyproject.toml
```

---

## City Stress Index (CSI) Formula

### Signal Weights

| Signal | Kafka Topic | Weight | Unit |
|---|---|---|---|
| Transit Delays | `transit.delays` | 0.25 | minutes_delay |
| Noise Level | `noise.sensors` | 0.20 | dB |
| Crowd Density | `crowd.density` | 0.20 | persons/m² |
| Heat Island | `heat.island` | 0.20 | °C above avg |
| Accessibility Events | `accessibility.events` | 0.15 | active outages |

### Composite Score
```python
# All signals normalized to 0.0–1.0 before weighting
CSI(hex) = sum(weight_i * normalized_signal_i)

# Stress bands
0.00–0.25  →  LOW
0.25–0.50  →  MODERATE
0.50–0.75  →  HIGH
0.75–1.00  →  CRITICAL
```

Weights load from `config/signal_weights.yaml` at runtime.
**NEVER hardcode weights inside scorer logic.**

---

## Anomaly Detection Logic
```python
deviation = (CSI_current - baseline_mean) / baseline_std

# Alert thresholds
if abs(deviation) > 2.5:  → ANOMALY_HIGH
if abs(deviation) > 1.8:  → ANOMALY_WARN

# Baseline: rolling 30-day window, same hour + same weekday
# Minimum 14 days of history required before detection activates
```

Every `AnomalyEvent` must include:
`hex_id`, `timestamp`, `csi_current`, `csi_baseline`, `deviation_score`, `triggered_signals[]`

---

## H3 Indexing Rules

- **Default resolution:** `9` (~174m edge — street-block level)
- **Rollup resolution:** `7` (~1.2km edge — district level)
- **Library:** `h3-py` v4+
- `hex_id` is the **canonical primary key** everywhere — lat/lon is transient
```python
import h3
hex_id = h3.latlng_to_cell(lat, lng, resolution=9)
boundary = h3.cell_to_boundary(hex_id)  # for GeoJSON export
```

---

## Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| Stream broker | Apache Kafka (KRaft) | No Zookeeper |
| Kafka client | `confluent-kafka` | Preferred |
| Spatial | `geopandas`, `shapely`, `h3-py` | v4+ H3 API |
| Cache | Redis 7+ async | `redis-py` |
| API | FastAPI 0.110+ | Fully async |
| Validation | Pydantic v2 | No v1 syntax |
| Dashboard | Streamlit 1.33+ | Pydeck map |
| Logging | `structlog` JSON | No print() |
| Config | `pydantic-settings` | No bare os.getenv() |
| Testing | `pytest` + `pytest-asyncio` | asyncio_mode=auto |

---

## API Contract
```
GET  /api/v1/scores/{hex_id}
     → { hex_id, csi, band, signals, confidence, updated_at }

GET  /api/v1/scores/region?bbox=minLng,minLat,maxLng,maxLat&resolution=9
     → { hexagons: [{ hex_id, csi, band, centroid }] }

GET  /api/v1/anomalies?city={city}&since={iso8601}&severity=HIGH
     → { anomalies: [AnomalyEvent] }

GET  /api/v1/history/{hex_id}?from={iso}&to={iso}&interval=1h
     → { hex_id, timeseries: [{ timestamp, csi, signals }] }

POST /api/v1/export
     body: { hex_ids: [], format: "geojson"|"csv", include_signals: bool }
     → File download

WS   /ws/alerts  →  Stream of AnomalyEvent JSON
```

Standards: **ISO 8601 UTC** · **WGS84** · **RFC 7807 errors**

---

## Core Data Models
```python
class SignalEvent(BaseModel):
    signal_type: Literal["transit","noise","crowd","heat","accessibility"]
    hex_id: str
    value: float
    unit: str
    source_id: str
    timestamp: datetime

class CSIScore(BaseModel):
    hex_id: str
    csi: float                        # 0.0–1.0
    band: Literal["low","moderate","high","critical"]
    signals: dict[str, float]         # normalized per-signal contribution
    confidence: float                 # 1.0 = all 5 signals present
    computed_at: datetime

class AnomalyEvent(BaseModel):
    hex_id: str
    severity: Literal["WARN","HIGH"]
    csi_current: float
    csi_baseline: float
    deviation_score: float
    triggered_signals: list[str]
    timestamp: datetime
    city: str
```

---

## Redis Key Schema
```
csi:live:{hex_id}                    TTL 60s   current CSI score
csi:snapshot:{hex_id}:{hour_epoch}   TTL 30d   hourly snapshots
anomaly:active:{hex_id}              TTL 1h    active anomaly flag
baseline:{hex_id}:{weekday}:{hour}   TTL 7d    rolling baseline stats
```

**TTL is mandatory on every Redis write. No exceptions.**

---

## Coding Conventions

- Python 3.11+ — use `match` statements where appropriate
- Type hints on every function — no bare `dict` or `list`
- All I/O must be async: Kafka loops, Redis reads, FastAPI handlers
- Log with `structlog` JSON — never `print()`
- Config via `pydantic-settings` — never `os.getenv()` directly
- Kafka: manual offset commit only (never auto-commit)
- FastAPI: `lifespan` context manager (not deprecated `@app.on_event`)
- Streamlit: always `Pydeck H3HexagonLayer` for maps — never Folium
- Color scale: CSI float → `[R,G,B]` via `matplotlib.cm.RdYlGn_r`
- Cache API calls: `@st.cache_data(ttl=30)`

---

## Testing Requirements

- Unit test every normalizer, scorer, and detector function
- Integration tests spin up Kafka + Redis via Docker — no live APIs in tests
- Fixtures from `data/sample_feeds/` only
- Coverage target: **80%** on `fusion/` and `anomaly/`
```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

---

## Open Data Sources (Free / No Auth)

| Signal | Source |
|---|---|
| Transit delays | GTFS-RT via OpenMobilityData |
| Heat / Air quality | OpenAQ, Copernicus ERA5 |
| Noise (EU cities) | EEA Noise Directive |
| Crowd proxy | OpenStreetMap Overpass API |
| Accessibility | NYC Open Data, Transport for London |

All producers must implement **exponential backoff** for rate limits.
Missing signals reduce CSI **confidence** — the system must not fail.

---

## Backlog

| Feature | Priority |
|---|---|
| ML-based CSI prediction (next 2h) | High |
| Multi-city registry support | High |
| Prometheus + Grafana metrics | Medium |
| Kafka time-travel replay | Medium |
| LLM-generated stress narrative per hex | Low |
| QGIS plugin for city planners | Future |

---

## AI Assistant Rules (Always Enforce)

1. **Check `config/signal_weights.yaml`** before touching any weight value
2. **Use H3 resolution 9** unless explicitly stated otherwise
3. **Never bypass the normalizer** — raw values must never enter the scorer
4. **`hex_id` is the primary key** everywhere — lat/lon is transient input only
5. **Anomaly alerts are fire-and-forget** — never block the scoring pipeline
6. **Kafka consumers must be idempotent** — duplicates must not corrupt scores
7. **Signal failure ≠ system failure** — degrade confidence, keep running
8. **Every Redis write must have an explicit TTL**
9. **Never expose raw third-party values in API responses** — normalize first
10. **When adding a new signal**, update in this exact order:
    `signal_schema.py` → `weights.py` → `normalizer.py` → `scorer.py` → `signal_weights.yaml` → tests

---
*Last updated: 2026-03-02*