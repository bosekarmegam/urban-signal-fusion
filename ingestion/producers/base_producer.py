import asyncio
import json
import structlog
from typing import Any
from confluent_kafka import Producer
from ingestion.kafka_utils import get_producer

logger = structlog.get_logger()

class BaseProducer:
    def __init__(self, topic: str):
        self.topic = topic
        self.producer = get_producer()
        
    def delivery_report(self, err, msg) -> None:
        if err is not None:
            logger.error("Message delivery failed", error=str(err), topic=self.topic)
        else:
            logger.debug("Message delivered", topic=msg.topic(), partition=msg.partition())

    async def produce_event(self, event_data: dict[str, Any]) -> None:
        try:
            self.producer.produce(
                self.topic,
                value=json.dumps(event_data).encode("utf-8"),
                callback=self.delivery_report
            )
            # Trigger delivery callbacks
            self.producer.poll(0)
        except BufferError as e:
            logger.error("Local producer queue is full", error=str(e))
            self.producer.poll(0.1)
            
    async def fetch_data(self) -> list[dict[str, Any]]:
        """Override to implement API fetching logic."""
        raise NotImplementedError
        
    async def run(self, interval_seconds: int = 10) -> None:
        """Runs the producer loop with exponential backoff on failures."""
        backoff = 1.0
        max_backoff = 60.0
        
        logger.info("Starting producer", topic=self.topic, interval=interval_seconds)
        while True:
            try:
                events = await self.fetch_data()
                for event in events:
                    await self.produce_event(event)
                
                # Flush to ensure all are sent
                self.producer.flush(0.1)
                
                # Reset backoff on success
                backoff = 1.0
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error("Error in producer, applying backoff", error=str(e), backoff=backoff, topic=self.topic)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, max_backoff)
