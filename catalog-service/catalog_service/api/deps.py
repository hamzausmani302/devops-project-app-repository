# create dependencies here
from catalog_service.core.services.messaging_service import MessageQueue
from catalog_service.infra.services.messaging.rabbitmq_message_adapter import RabbitMQPublisher
from config import settings
def get_messaging_service() -> MessageQueue:
    return RabbitMQPublisher(topic=settings.rabbitmq_topic)