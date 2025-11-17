"""
MapiGuru Self-Hosted Embedding Client for DeepWiki
Integrates yo-digital's internal embedding service
"""

import os
import logging
from typing import Any, Dict, List, Optional, Union
import requests
from adalflow.core.model_client import ModelClient
from adalflow.core.types import EmbedderOutput, Embedding

logger = logging.getLogger(__name__)


class MapiGuruClient(ModelClient):
    """Client for MapiGuru self-hosted embedding service."""
    
    def __init__(
        self,
        base_url: str = None,
        api_key: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        Initialize MapiGuru client.
        
        Args:
            base_url: Base URL for the embedding service
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        super().__init__()
        self.base_url = base_url or os.environ.get(
            'MAPIGURU_BASE_URL', 
            'https://chat.mapiguru.yo-digital.com'
        )
        self.api_key = api_key or os.environ.get('MAPIGURU_API_KEY')
        self.timeout = timeout
        
        # Remove trailing slash from base URL
        self.base_url = self.base_url.rstrip('/')
        
        logger.info(f"MapiGuru client initialized with base URL: {self.base_url}")
    
    def init_sync_client(self):
        """Initialize synchronous client (already using requests)."""
        pass
    
    def init_async_client(self):
        """Initialize async client (not implemented yet)."""
        pass
    
    def parse_embed_response(self, response: Dict[str, Any]) -> EmbedderOutput:
        """
        Parse the embedding response from MapiGuru API.
        
        Args:
            response: Raw API response
            
        Returns:
            EmbedderOutput with embeddings
        """
        try:
            # Assuming the response contains an 'embedding' field
            # Adjust based on actual response structure
            if isinstance(response, dict):
                embedding = response.get('embedding') or response.get('embeddings')
                if embedding:
                    return EmbedderOutput(
                        data=[embedding] if not isinstance(embedding[0], list) else embedding,
                        error=None,
                        raw_response=response
                    )
            
            logger.error(f"Unexpected response format: {response}")
            return EmbedderOutput(
                data=None,
                error=f"Failed to parse embedding response: {response}",
                raw_response=response
            )
        except Exception as e:
            logger.error(f"Error parsing embed response: {e}")
            return EmbedderOutput(
                data=None,
                error=str(e),
                raw_response=response
            )
    
    def parse_embedding_response(self, response: Any) -> EmbedderOutput:
        """
        Parse MapiGuru embedding response to EmbedderOutput format.
        
        Args:
            response: The response from MapiGuru API (can be EmbedderOutput or raw response)
            
        Returns:
            EmbedderOutput with properly formatted Embedding objects
        """
        try:
            # If response is already an EmbedderOutput, return it
            if isinstance(response, EmbedderOutput):
                return response
            
            # If response is a raw list of embeddings
            if isinstance(response, list):
                embedding_objects = [
                    Embedding(embedding=emb if isinstance(emb, list) else emb[0], index=i) 
                    for i, emb in enumerate(response)
                ]
                return EmbedderOutput(
                    data=embedding_objects,
                    error=None,
                    raw_response=response
                )
            
            # Fallback: treat as error
            logger.error(f"Unexpected response type in parse_embedding_response: {type(response)}")
            return EmbedderOutput(
                data=[],
                error=f"Unexpected response type: {type(response)}",
                raw_response=response
            )
        except Exception as e:
            logger.error(f"Error in parse_embedding_response: {e}")
            return EmbedderOutput(
                data=[],
                error=str(e),
                raw_response=response
            )
    
    def call(
        self,
        api_kwargs: Dict[str, Any],
        model_type: str = "embedder"
    ) -> EmbedderOutput:
        """
        Make synchronous call to MapiGuru embedding API.
        
        Args:
            api_kwargs: Should contain 'input' (text or list of texts) and 'model'
            model_type: Type of model (embedder)
            
        Returns:
            EmbedderOutput with embeddings
        """
        try:
            # Extract parameters
            text_input = api_kwargs.get('input') or api_kwargs.get('prompt')
            model = api_kwargs.get('model', 'sentence-transformers/all-MiniLM-L6-v2')
            
            if not text_input:
                raise ValueError("No input text provided")
            
            # Handle both single string and list of strings
            if isinstance(text_input, str):
                texts = [text_input]
                is_single = True
            else:
                texts = text_input
                is_single = False
            
            embeddings = []
            
            # Process each text
            for text in texts:
                payload = {
                    "text": text,
                    "model": model
                }
                
                headers = {
                    'Content-Type': 'application/json'
                }
                
                # Add API key to headers if available
                if self.api_key:
                    headers['Authorization'] = f'Bearer {self.api_key}'
                
                # Make request
                url = f"{self.base_url}/embeddings/extract"
                logger.debug(f"Calling MapiGuru API: {url} with model: {model}")
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract embedding from response
                # MapiGuru returns a direct array: [[0.123, 0.456, ...]]
                if isinstance(result, list):
                    # Direct array format
                    if len(result) > 0:
                        embedding = result[0] if isinstance(result[0], list) else result
                    else:
                        raise ValueError(f"Empty embedding array in response: {result}")
                elif isinstance(result, dict):
                    # Object format (fallback)
                    embedding = result.get('embedding') or result.get('embeddings') or result.get('data')
                else:
                    raise ValueError(f"Unexpected response type: {type(result)}")
                
                if embedding is None:
                    logger.error(f"No embedding found in response: {result}")
                    raise ValueError(f"No embedding in response: {result}")
                
                embeddings.append(embedding)
            
            # Wrap embeddings in Embedding objects (required by Adalflow ToEmbeddings)
            embedding_objects = [
                Embedding(embedding=emb, index=i) 
                for i, emb in enumerate(embeddings)
            ]
            
            # Return embeddings wrapped in Embedding objects
            return EmbedderOutput(
                data=embedding_objects,
                error=None,
                raw_response={"embeddings": embeddings}
            )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"MapiGuru API request failed: {e}")
            return EmbedderOutput(
                data=None,
                error=str(e),
                raw_response=None
            )
        except Exception as e:
            logger.error(f"Error in MapiGuru client call: {e}")
            return EmbedderOutput(
                data=None,
                error=str(e),
                raw_response=None
            )
    
    async def acall(
        self,
        api_kwargs: Dict[str, Any],
        model_type: str = "embedder"
    ) -> EmbedderOutput:
        """
        Async call not implemented yet.
        Falls back to synchronous call.
        """
        return self.call(api_kwargs, model_type)
    
    def convert_inputs_to_api_kwargs(
        self,
        input: Optional[Any] = None,
        model_kwargs: Dict = {},
        model_type: str = "embedder",
    ) -> Dict[str, Any]:
        """
        Convert inputs to API kwargs format.
        
        Args:
            input: Text or list of texts to embed
            model_kwargs: Additional model parameters
            model_type: Type of model
            
        Returns:
            Dictionary with API parameters
        """
        api_kwargs = {
            "input": input,
        }
        
        # Add model and other kwargs
        api_kwargs.update(model_kwargs)
        
        return api_kwargs

