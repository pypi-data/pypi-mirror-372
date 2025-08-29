from typing import Optional, Dict, Any
import requests
from urllib3.exceptions import InsecureRequestWarning
import warnings
import aiohttp

from ..common.config import ClientConfig, DEFAULT_CONFIG
from ..common.errors import ValidationError, ApiError, AztpError
from .types import (
    OIDCLoginOptions,
    OIDCLoginResponse,
    ValidateTokenRequest,
    ValidateTokenResponse
)

# Suppress only the single warning from urllib3 needed.
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

class OIDCClient:
    def __init__(self, config: ClientConfig):
        self._validate_config(config)
        self.config = DEFAULT_CONFIG.copy()
        self.config.update({
            'api_access_key': config.api_key,
            'base_url': config.base_url,
            'environment': config.environment,
            'timeout': config.timeout
        })
        
        # Headers for aiohttp session
        self.headers = {
            'api_access_key': self.config['api_access_key'],
            'Content-Type': 'application/json'
        }
        self.base_url = self.config['base_url']

    async def login(
        self,
        provider: str,
        aztp_id: str,
        options: Optional[OIDCLoginOptions] = None
    ) -> OIDCLoginResponse:
        """
        Initiates OIDC login with specified provider
        
        Args:
            provider: The OIDC provider (e.g., "google")
            aztp_id: The AZTP ID for the agent
            options: Optional configuration for the login process
            
        Returns:
            OIDCLoginResponse containing login response with redirect URL
            
        Raises:
            ValidationError: If required parameters are invalid
            ApiError: If an unexpected error occurs
        """
        if not provider:
            raise ValidationError("Provider is required")
            
        if not aztp_id or not aztp_id.startswith("aztp://"):
            raise ValidationError("Invalid AZTP ID format - must start with 'aztp://'")

        options = options or {}
        
        try:
            payload = {
                'provider': provider,
                'agent': aztp_id,
                'stateless': options.get('stateless', True),
            }
            
            if options.get('return_url'):
                payload['returnUrl'] = options['return_url']

            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(
                    f"{self.base_url}/oidc/provider",
                    json=payload,
                    timeout=self.config['timeout'],
                    ssl=False  # Allow self-signed certificates
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            
        except aiohttp.ClientError as e:
            raise self._handle_error(e)

    async def validate_token(self, token: str) -> ValidateTokenResponse:
        """
        Validates a JWT token and returns user information
        
        Args:
            token: The JWT token to validate
            
        Returns:
            ValidateTokenResponse containing validation response with user information
            
        Raises:
            ValidationError: If token is not provided
            ApiError: If an unexpected error occurs
        """
        if not token:
            raise ValidationError("Token is required")
            
        try:
            request: ValidateTokenRequest = {'token': token}
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(
                    f"{self.base_url}/oidc/validate-jwt-token",
                    json=request,
                    timeout=self.config['timeout'],
                    ssl=False  # Allow self-signed certificates
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            
        except aiohttp.ClientError as e:
            raise self._handle_error(e)

    def _validate_config(self, config: ClientConfig) -> None:
        if not config.base_url:
            raise ValidationError("Base URL is required")
        if not config.api_key:
            raise ValidationError("API access key is required")

    def _handle_error(self, error: Exception) -> Exception:
        if isinstance(error, AztpError):
            return error
        return ApiError("An unexpected error occurred", 500) 