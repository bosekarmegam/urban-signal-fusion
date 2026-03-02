<div align="center">
  <h1>🚦 Urban Signal Fusion</h1>
  <p><strong>Multi-Modal City Stress Score Engine</strong></p>
  <p>A high-performance geospatial data pipeline that captures real-time city rhythms, calculates a City Stress Index (CSI), and flags urban anomalies instantly.</p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.33.0-FF4B4B.svg)](https://streamlit.io)

  <h3><a href="https://urban-signal-fusion.streamlit.app/">👉 View Live Dashboard Here 👈</a></h3>
</div>

---

## 📖 Overview
Every city block has a rhythm. Stress happens when it breaks. 
**Urban Signal Fusion** is an open-source ETL pipeline and dashboarding system built to synthesize multi-modal urban inputs (transit delays, crowd density, heat island effects, noise pollution, and infrastructure outages) into a unified **City Stress Index (CSI)** down to the street level using Uber's H3 Hexagonal Grid system.

Built by **Suneel Bose** ([@bosekarmegam](https://github.com/bosekarmegam)).

## ✨ Key Features
- **Real-Time Data Ingestion:** Asynchronous Kafka streaming (KRaft mode) for multi-topic urban signals.
- **Geospatial Mapping:** Maps GPS points to `H3` hexagon grids for resolution-9 micro-block analysis.
- **Dynamic Composite Scoring:** Computes an aggregate CSI (0.0 - 1.0) powered by a dynamically hot-reloadable weights configuration.
- **Intelligent Anomaly Detection:** Utilizes Redis rolling baselines and Z-score mathematics to fire instantaneous anomaly alerts back into the Kafka bus.
- **Interactive Dashboarding:** Streamlit dashboard utilizing PyDeck mapping and Altair charting for live geospatial visualization of major cities globally (Default: **Chennai**).

## 🚀 Quickstart (Local Development)

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.11+

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/bosekarmegam/urban-signal-fusion.git
cd urban-signal-fusion

# Setup virtual environment and install
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .[dev]
```

### 3. Boot Core Infrastructure (Kafka + Redis)
```bash
docker-compose -f infra/docker-compose.yml up -d
```

### 4. Run the Stack
**Terminal 1 (Mock Producers):**
```bash
python -m ingestion.consumers.signal_consumer
```

**Terminal 2 (API Backend):**
```bash
uvicorn api.main:app --reload
```

**Terminal 3 (Live Dashboard):**
```bash
streamlit run dashboard/app.py
```

## 🌐 Deployment (Production)
To deploy this project to the web, you need a hosting provider. Here is a recommended architecture:
- **Compute (FastAPI & Streamlit):** Deploy via [Render](https://render.com), [Railway](https://railway.app), or AWS Elastic Beanstalk. Ensure you set environment variables to point to production datastores.
- **Event Streaming (Kafka):** Use a managed service like [Confluent Cloud](https://www.confluent.io) to avoid managing Kafka broker state manually.
- **Caching (Redis):** Use [Upstash](https://upstash.com) or AWS ElastiCache.

## 🤝 Contributing
Contributions are absolutely welcome! Please feel free to submit a Pull Request.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
