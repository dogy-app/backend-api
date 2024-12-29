from azure.identity import EnvironmentCredential
from azure.keyvault.secrets import SecretClient

from app.config import get_settings


def get_secret_from_client(secret: str, secret_client: SecretClient) -> str:
    retrieved_secret: str | None = secret_client.get_secret(secret).value
    if retrieved_secret is None:
        raise ValueError(f"Secret {secret} not found")
    return retrieved_secret

def get_secret(secret: str) -> str:
    settings = get_settings()
    credential = EnvironmentCredential()
    secret_client = SecretClient(vault_url=settings.key_vault_url, credential=credential)
    return get_secret_from_client(secret, secret_client)
