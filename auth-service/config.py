# settings.py
from pydantic_settings import BaseSettings
from pydantic import Field, computed_field

class AppConfig(BaseSettings):
    app_name: str = Field(default="auth-service")
    debug: bool = False
    port: int = 8081
    @computed_field
    @property  
    def version(self) -> str:
        return open(".ver", "r").read()
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

settings = AppConfig()
