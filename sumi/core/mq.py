from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from config import settings


def get_producer():
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_URL)
    return producer


def get_consumer(topic, group_id=None):
    if group_id is None:
        consumer = AIOKafkaConsumer(topic,
                                    bootstrap_servers=settings.KAFKA_URL)
    else:
        consumer = AIOKafkaConsumer(topic,
                                    bootstrap_servers=settings.KAFKA_URL,
                                    group_id=group_id,
                                    auto_offset_reset='latest')
    return consumer