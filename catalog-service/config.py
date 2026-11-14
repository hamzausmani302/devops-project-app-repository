# settings.py
from pydantic_settings import BaseSettings
from pydantic import Field, computed_field

class AppConfig(BaseSettings):
    app_name: str = Field(default="catalog-service")
    debug: bool = False
    port: int = 8000
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_topic: str = "orders"
    auth_service_url: str = "http://auth-service:8081"
    @computed_field
    @property  
    def version(self) -> str:
        return open(".ver", "r").read()
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
    
)
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter



def configure_opentelemetry(config):

    resource = Resource.create({
        "service.name": config.app_name,
        "service.version": config.version,
    })

    provider = TracerProvider(
        resource=resource
    )

    # exporter = OTLPSpanExporter(
    #     endpoint="localhost:4317",
    #     insecure=True,
    # )
    exporter = ConsoleSpanExporter()
    provider.add_span_processor(
        BatchSpanProcessor(exporter)                                                    
    )

    trace.set_tracer_provider(provider)

    return provider

settings = AppConfig()
