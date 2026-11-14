# settings.py
from pydantic_settings import BaseSettings
from pydantic import Field, computed_field

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
    @computed_field
    @property  
    def version(self) -> str:
        return open(".ver", "r").read()
        

settings = AppConfig()
