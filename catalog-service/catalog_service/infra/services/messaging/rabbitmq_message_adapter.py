import pika
from abc import ABC, abstractmethod
from catalog_service.core.services.messaging_service import MessageQueue
import json
from config import settings

class RabbitMQPublisher(MessageQueue):
    def __init__(self, topic: str):
        self.topic = topic
        self.exchange = ''
        channel = self.connect()
        channel.queue_declare(queue=self.topic)

    def connect(self) -> pika.channel.Channel:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.rabbitmq_host, port=settings.rabbitmq_port)
        )
        channel = connection.channel()
        self.channel = channel
        return channel
    
    def publish(self, message, headers = {}):
        self.channel.basic_publish(exchange=self.exchange, routing_key=self.topic,
                              body=json.dumps(message).encode(),
                              properties=pika.BasicProperties(
                                headers=headers
                            ))
    def consume(self, callback):
        self.channel.basic_consume(queue=self.topic, on_message_callback=callback, auto_ack=True)

