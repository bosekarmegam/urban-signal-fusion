import asyncio
from confluent_kafka import Producer, Consumer
from config.settings import settings

def get_producer() -> Producer:
    conf = {
        'bootstrap.servers': settings.kafka_bootstrap_servers,
        'client.id': settings.project_name
    }
    return Producer(conf)

def get_consumer(group_id: str, topics: list[str]) -> Consumer:
    conf = {
        'bootstrap.servers': settings.kafka_bootstrap_servers,
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False  # mandatory per instructions
    }
    consumer = Consumer(conf)
    consumer.subscribe(topics)
    return consumer
