from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class AzureSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AZURE_",
        extra="ignore"
    )
    # Storage Account
    storage_account_url: str
    storage_pet_container_name: str

    # Key Vault
    key_vault_url: str

    # PostgreSQL Flexible Server
    postgresql_user: str
    postgresql_host: str
    postgresql_db_name: str

    # Retrieving token
    db_token_endpoint: str


class Settings(AzureSettings):
    api_version: str = "v1"
    clerk_jwks_url: str
    pass

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
