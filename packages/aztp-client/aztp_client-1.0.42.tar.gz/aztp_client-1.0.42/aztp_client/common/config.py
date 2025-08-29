import os
from typing import Optional, Dict
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Default configuration values
DEFAULT_CONFIG = {
    'api_access_key': 'e93b74d812dbf44e1568fcb462747e281c583a85e1065160501a361f25930b21',  # Will be set from ClientConfig
    'base_url': 'https://api.astha.ai:5001/astha/v1',
    'environment': 'production',
    'timeout': 30
}

# List of trusted domains that can be used with the AZTP client
whiteListTrustDomains: Dict[str, str] = {
    "gptarticles.xyz": "gptarticles.xyz",
    "gptapps.ai": "gptapps.ai",
    "vcagents.ai": "vcagents.ai"
}

class ClientConfig(BaseModel):
    api_key: str
    base_url: str = Field(default="https://api.astha.ai:5001/astha/v1")
    environment: str = Field(default="production")
    timeout: int = Field(default=30)

    @classmethod
    def from_env(cls) -> "ClientConfig":
        """Create configuration from environment variables."""
        base_url = os.getenv("AZTP_BASE_URL", "https://api.astha.ai:5001/astha/v1")
        return cls(
            api_key=os.getenv("AZTP_API_KEY", ""),
            base_url=base_url,
            environment=os.getenv("AZTP_ENVIRONMENT", "production"),
            timeout=int(os.getenv("AZTP_TIMEOUT", "30")),
        )

    @classmethod
    def create(
        cls,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        environment: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> "ClientConfig":
        """Create configuration with optional overrides."""
        config = cls.from_env()
        
        if api_key:
            config.api_key = api_key
        if base_url:
            config.base_url = base_url.rstrip("/")  # Just remove trailing slash
        if environment:
            config.environment = environment
        if timeout:
            config.timeout = timeout
            
        return config

    def get_url(self, path: str) -> str:
        """Get full URL for a given path."""
        # Remove any leading/trailing slashes from path
        clean_path = path.strip("/")
        return f"{self.base_url}/aztp/{clean_path}" 