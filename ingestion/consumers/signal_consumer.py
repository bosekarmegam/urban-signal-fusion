import asyncio
import json
import structlog
from confluent_kafka import Message
from ingestion.kafka_utils import get_consumer
from ingestion.schemas.signal_schema import SignalEvent

logger = structlog.get_logger()
TOPICS = [
    "transit.delays", 
    "noise.sensors", 
    "crowd.density", 
    "heat.island", 
    "accessibility.events"
]

async def process_signal(event: SignalEvent):
    """Placeholder for pipeline integration"""
    logger.debug("Processing signal event", hex_id=event.hex_id, signal_type=event.signal_type)

async def run_signal_consumer():
    consumer = get_consumer("signal-fusion-group", TOPICS)
    logger.info("Started signal consumer")
    
    try:
        while True:
            # Non-blocking poll combined with asyncio.sleep for async I/O
            msg: Message = consumer.poll(timeout=0)
            if msg is None:
                await asyncio.sleep(0.1)
                continue
            
            if msg.error():
                logger.error("Consumer error", error=msg.error())
                continue
                
            try:
                data = json.loads(msg.value().decode("utf-8"))
                event = SignalEvent.model_validate(data)
                
                # Hand over to pipeline
                await process_signal(event)
                
                # Manual offset commit
                consumer.commit(msg, asynchronous=True)
            except Exception as e:
                logger.error("Error processing msg", error=str(e))
                
    except asyncio.CancelledError:
        logger.info("Signal consumer cancelled")
    finally:
        consumer.close()

if __name__ == "__main__":
    asyncio.run(run_signal_consumer())
