from pydantic import BaseSettings


class Settings(BaseSettings):
    database_path: str = "sqlite:///./queue-support.db"

    class Config:
        env_prefix = "queue_support_"

        env_file = ".env", "/etc/queue-support.conf"


settings = Settings()
