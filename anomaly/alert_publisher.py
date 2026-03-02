import structlog
from anomaly.models import AnomalyEvent
from ingestion.kafka_utils import get_producer

logger = structlog.get_logger()

class AlertPublisher:
    def __init__(self):
        self.producer = get_producer()
        self.topic = "anomaly.events"
        
    def _delivery_report(self, err, msg):
        if err is not None:
            logger.error("Failed to publish alert", error=str(err))

    async def publish(self, event: AnomalyEvent) -> None:
        """Asynchronously fires the anomaly to the Kafka bus."""
        try:
            self.producer.produce(
                self.topic,
                key=event.hex_id.encode("utf-8"),
                value=event.model_dump_json().encode("utf-8"),
                callback=self._delivery_report
            )
            # Trigger delivery callbacks non-blockingly
            self.producer.poll(0)
            logger.info("Published anomaly alert", hex_id=event.hex_id)
        except Exception as e:
            logger.error("Error publishing alert", error=str(e))

alert_publisher = AlertPublisher()
