from rabbitmq_message_adapter import RabbitMQPublisher
import json
import time
from config import settings

print(settings.rabbitmq_host, settings.rabbitmq_port, settings.rabbitmq_topic)

def consume(channel, method, properties, body):
    payload = json.loads(body.decode())
    print(f"Processing order {payload['id']} for user {payload['user_id']}")
    # print(method,properties, channel )
    time.sleep(20)   
    print(f"Processing prodcut id= {payload['product_id']}")
    time.sleep(10)   
    print(f"Done ... id= {payload['id']}")
    channel.basic_ack(delivery_tag=method.delivery_tag)
consumer = RabbitMQPublisher(topic=settings.rabbitmq_topic, 
                             host=settings.rabbitmq_host, 
                             port=settings.rabbitmq_port)
consumer.consume(consume)

