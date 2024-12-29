from functools import lru_cache

from dotenv import load_dotenv
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class AzureSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AZURE_")

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
    pass


try:
    settings = Settings()
    print("Environment variables successfully loaded:")
    print(settings.model_dump())
except ValidationError as e:
    print("Environment variable validation failed:")
    print(e)

@lru_cache
def get_settings():
    return settings
