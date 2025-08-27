from typing import Union

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Variables attendues

    # -- API --
    aisberg_api_key: Union[str, None] = None
    aisberg_base_url: Union[str, None] = None
    aisberg_timeout: int = 180  # 180 seconds (default 3 minutes)

    # Config Pydantic
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
