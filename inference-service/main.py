from rabbitmq_message_adapter import RabbitMQPublisher
import json
import time
from config import settings

from opentelemetry import trace
from opentelemetry.propagate import extract
from opentelemetry.trace import SpanKind

from telemetry import configure_opentelemetry, trace_function, trace_span

configure_opentelemetry(settings)

print(settings.rabbitmq_host, settings.rabbitmq_port, settings.rabbitmq_topic)


@trace_function("Inference consume Function")
def consume(channel, method, properties, body):
    payload = json.loads(body.decode())
    headers = properties.headers or {}
    parent_context = extract(headers)
    print(f"Processing order {payload['id']} for user {payload['user_id']} | headers = {headers}")
    # print(method,properties, channel )
    with trace_span("process_order", {
        "payload": payload 
    }, SpanKind.CONSUMER, parent_context):
        time.sleep(20)   
        print(f"Processing prodcut id= {payload['product_id']}")
        time.sleep(10)  
        print(f"Done ... id= {payload['id']}")
        channel.basic_ack(delivery_tag=method.delivery_tag)
consumer = RabbitMQPublisher(topic=settings.rabbitmq_topic, 
                             host=settings.rabbitmq_host, 
                             port=settings.rabbitmq_port)
consumer.consume(consume)

