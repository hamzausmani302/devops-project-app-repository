import pika
from abc import ABC, abstractmethod
from messaging_service import MessageQueue
import json

class RabbitMQPublisher(MessageQueue):
    def __init__(self, topic: str, host: str = "localhost", port: int = 5672):
        self.topic = topic
        self.exchange = ''
        self.host = host
        self.port = port
        self.channel = self.connect()
        
    def connect(self) -> pika.channel.Channel:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, port=self.port)
        )
        channel = connection.channel()
        channel.queue_declare(queue=self.topic)
        channel.basic_qos(prefetch_count=1)
        self.channel = channel
        return self.channel
    
    def publish(self, message):
        self.channel.basic_publish(exchange=self.exchange, routing_key=self.topic,
                              body=json.dumps(message).encode())
    def consume(self, callback):
        self.channel.basic_consume(queue=self.topic, on_message_callback=callback)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
