# settings.py
from pydantic_settings import BaseSettings
from pydantic import Field

class AppConfig(BaseSettings):
    app_name: str = Field(default="inference-service")
    debug: bool = False
    rabbitmq_host: str
    rabbitmq_port: int = 5672
    rabbitmq_topic: str = "orders"
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

settings = AppConfig()
