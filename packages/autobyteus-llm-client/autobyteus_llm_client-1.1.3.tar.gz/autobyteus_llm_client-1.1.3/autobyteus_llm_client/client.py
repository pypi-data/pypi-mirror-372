import os
import httpx
import logging
import json
from typing import Dict, Optional, AsyncGenerator, Any, Union, List
from urllib.parse import urljoin
from pathlib import Path

logger = logging.getLogger(__name__)

# Define CertificateError directly in this file
class CertificateError(Exception):
    """Custom exception for certificate-related errors"""
    pass

class AutobyteusClient:
    DEFAULT_SERVER_URL = "https://api.autobyteus.com"
    API_KEY_HEADER = "AUTOBYTEUS_API_KEY"
    API_KEY_ENV_VAR = "AUTOBYTEUS_API_KEY"
    SSL_CERT_FILE_ENV_VAR = "AUTOBYTEUS_SSL_CERT_FILE"
    
    def __init__(self, server_url: Optional[str] = None):
        """
        Initialize the client.

        Args:
            server_url (Optional[str]): The server URL to connect to. If provided,
                                        it overrides the AUTOBYTEUS_LLM_SERVER_URL
                                        environment variable.
        """
        # server_url parameter takes precedence, then env var, then default.
        self.server_url = server_url or os.getenv('AUTOBYTEUS_LLM_SERVER_URL', self.DEFAULT_SERVER_URL)
        self.api_key = os.getenv(self.API_KEY_ENV_VAR)
        
        if not self.api_key:
            raise ValueError(
                f"{self.API_KEY_ENV_VAR} environment variable is required. "
                "Please set it before initializing the client."
            )
        
        # Determine SSL verification method
        custom_cert_path_str = os.getenv(self.SSL_CERT_FILE_ENV_VAR)
        verify_param: Union[str, bool, Path] # Declare type

        if custom_cert_path_str:
            custom_cert_path = Path(custom_cert_path_str)
            if not custom_cert_path.exists():
                raise CertificateError(
                    f"Custom SSL certificate file specified via {self.SSL_CERT_FILE_ENV_VAR} "
                    f"not found at: {custom_cert_path}"
                )
            if not custom_cert_path.is_file():
                 raise CertificateError(
                    f"Custom SSL certificate path specified via {self.SSL_CERT_FILE_ENV_VAR} "
                    f"is not a file: {custom_cert_path}"
                )
            verify_param = str(custom_cert_path)
            logger.info(
                f"Using custom SSL certificate file for TLS verification: {verify_param}. "
                "This is the recommended secure method for servers with self-signed or private CA certificates."
            )
        else:
            verify_param = False # Skip certificate verification
            logger.warning(
                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
                "SECURITY WARNING: SSL certificate verification is DISABLED because the \n"
                f"'{self.SSL_CERT_FILE_ENV_VAR}' environment variable is not set.\n"
                "This configuration is INSECURE and makes the client vulnerable to \n"
                "Man-in-the-Middle (MitM) attacks. It should ONLY be used for development \n"
                "or testing in trusted environments with self-signed certificates if \n"
                "providing the certificate path is not possible.\n"
                "FOR PRODUCTION or secure environments with self-signed certificates, \n"
                f"it is STRONGLY RECOMMENDED to set the '{self.SSL_CERT_FILE_ENV_VAR}' \n"
                "environment variable to the path of the server's certificate (.pem file) \n"
                "to enable proper TLS verification.\n"
                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            )

        # Configure timeout
        timeout_config = httpx.Timeout(
            connect=10.0,
            read=None,
            write=None,
            pool=None
        )
        
        # Initialize clients
        try:
            self.async_client = httpx.AsyncClient(
                verify=verify_param,
                headers={self.API_KEY_HEADER: self.api_key},
                timeout=timeout_config
            )
            
            self.sync_client = httpx.Client(
                verify=verify_param,
                headers={self.API_KEY_HEADER: self.api_key},
                timeout=timeout_config
            )
        except Exception as e: 
            logger.error(f"Failed to initialize httpx client with SSL configuration (verify='{verify_param}'): {e}")
            raise RuntimeError(f"HTTP client initialization failed: {e}") from e
            
        logger.info(f"Initialized Autobyteus client with server URL: {self.server_url}")

    async def get_available_llm_models(self) -> Dict[str, Any]:
        """Async discovery of available LLM models."""
        try:
            response = await self.async_client.get(urljoin(self.server_url, "/models/llm"))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Async LLM model fetch error: {str(e)}")
            raise RuntimeError(str(e)) from e

    def get_available_llm_models_sync(self) -> Dict[str, Any]:
        """Synchronous discovery of available LLM models."""
        try:
            response = self.sync_client.get(urljoin(self.server_url, "/models/llm"))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Sync LLM model fetch error: {str(e)}")
            raise RuntimeError(str(e)) from e

    async def get_available_image_models(self) -> Dict[str, Any]:
        """Async discovery of available image models."""
        try:
            response = await self.async_client.get(urljoin(self.server_url, "/models/image"))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Async image model fetch error: {str(e)}")
            raise RuntimeError(str(e)) from e

    def get_available_image_models_sync(self) -> Dict[str, Any]:
        """Synchronous discovery of available image models."""
        try:
            response = self.sync_client.get(urljoin(self.server_url, "/models/image"))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Sync image model fetch error: {str(e)}")
            raise RuntimeError(str(e)) from e

    async def get_available_audio_models(self) -> Dict[str, Any]:
        """Async discovery of available audio models."""
        try:
            response = await self.async_client.get(urljoin(self.server_url, "/models/audio"))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Async audio model fetch error: {str(e)}")
            raise RuntimeError(str(e)) from e

    def get_available_audio_models_sync(self) -> Dict[str, Any]:
        """Synchronous discovery of available audio models."""
        try:
            response = self.sync_client.get(urljoin(self.server_url, "/models/audio"))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Sync audio model fetch error: {str(e)}")
            raise RuntimeError(str(e)) from e

    async def send_message(
        self,
        conversation_id: str,
        model_name: str,
        user_message: str,
        image_urls: Optional[List[str]] = None,
        audio_urls: Optional[List[str]] = None,
        video_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send a message and get a response."""
        try:
            data = {
                "conversation_id": conversation_id,
                "model_name": model_name,
                "user_message": user_message,
                "image_urls": image_urls or [],
                "audio_urls": audio_urls or [],
                "video_urls": video_urls or []
            }
            response = await self.async_client.post(
                urljoin(self.server_url, "/send-message"),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error sending message: {str(e)}")
            raise RuntimeError(str(e)) from e

    async def stream_message(
        self,
        conversation_id: str,
        model_name: str,
        user_message: str,
        image_urls: Optional[List[str]] = None,
        audio_urls: Optional[List[str]] = None,
        video_urls: Optional[List[str]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream a message and get responses."""
        try:
            data = {
                "conversation_id": conversation_id,
                "model_name": model_name,
                "user_message": user_message,
                "image_urls": image_urls or [],
                "audio_urls": audio_urls or [],
                "video_urls": video_urls or []
            }
            
            async with self.async_client.stream(
                "POST",
                urljoin(self.server_url, "/stream-message"),
                json=data
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            chunk = json.loads(line[6:])
                            if 'error' in chunk:
                                raise RuntimeError(chunk['error'])
                            yield chunk
                        except json.JSONDecodeError:
                            logger.error("Failed to parse stream chunk")
                            raise RuntimeError("Invalid stream response format")

        except httpx.HTTPError as e:
            logger.error(f"Stream error: {str(e)}")
            raise RuntimeError(str(e)) from e

    async def generate_image(
        self,
        model_name: str,
        prompt: str,
        input_image_urls: Optional[List[str]] = None,
        mask_url: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generates or edits an image and gets a response."""
        try:
            data = {
                "model_name": model_name,
                "prompt": prompt,
                "input_image_urls": input_image_urls or [],
                "mask_url": mask_url,
                "generation_config": generation_config or {}
            }
            response = await self.async_client.post(
                urljoin(self.server_url, "/generate-image"),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error generating image: {str(e)}")
            raise RuntimeError(str(e)) from e

    async def generate_speech(
        self,
        model_name: str,
        prompt: str,
        generation_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generates speech from text and gets a response."""
        try:
            data = {
                "model_name": model_name,
                "prompt": prompt,
                "generation_config": generation_config or {}
            }
            response = await self.async_client.post(
                urljoin(self.server_url, "/generate-speech"),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error generating speech: {str(e)}")
            raise RuntimeError(str(e)) from e
        
    async def cleanup(self, conversation_id: str) -> Dict[str, Any]:
        """Clean up a conversation."""
        try:
            response = await self.async_client.post(
                urljoin(self.server_url, "/cleanup"),
                json={"conversation_id": conversation_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Cleanup error: {str(e)}")
            raise RuntimeError(str(e)) from e

    async def close(self):
        """Close both clients"""
        await self.async_client.aclose()
        self.sync_client.close()
