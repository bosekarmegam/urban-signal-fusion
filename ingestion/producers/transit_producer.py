import random
import h3
from datetime import datetime, timezone
from ingestion.producers.base_producer import BaseProducer
from ingestion.schemas.signal_schema import SignalEvent

# Default backend emission focus (Chennai, India)
LAT, LNG = 13.0827, 80.2707
BASE_HEX = h3.latlng_to_cell(LAT, LNG, 9)
ACTIVE_HEXES = list(h3.grid_disk(BASE_HEX, 6))

class TransitProducer(BaseProducer):
    def __init__(self):
        super().__init__("transit.delays")

    async def fetch_data(self) -> list[dict]:
        events = []
        for _ in range(random.randint(5, 15)):
            event = SignalEvent(
                signal_type="transit",
                hex_id=random.choice(ACTIVE_HEXES),
                value=round(random.uniform(0, 60), 1),
                unit="minutes_delay",
                source_id=f"bus_{random.randint(100,999)}",
                timestamp=datetime.now(timezone.utc)
            )
            events.append(event.model_dump(mode="json"))
        return events

if __name__ == "__main__":
    import asyncio
    producer = TransitProducer()
    asyncio.run(producer.run(interval_seconds=5))
