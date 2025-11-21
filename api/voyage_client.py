"""
Voyage AI Embedding Client for DeepWiki
Integrates Voyage AI's embedding service (https://www.voyageai.com)
"""

import os
import logging
from typing import Any, Dict, List, Optional, Union
import requests
from adalflow.core.model_client import ModelClient
from adalflow.core.types import EmbedderOutput, Embedding

logger = logging.getLogger(__name__)


class VoyageClient(ModelClient):
    """Client for Voyage AI embedding service."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.voyageai.com/v1",
        timeout: int = 60,
    ):
        """
        Initialize Voyage AI client.
        
        Args:
            api_key: Voyage AI API key (or set VOYAGE_API_KEY env var)
            base_url: Base URL for the Voyage AI API
            timeout: Request timeout in seconds
        """
        super().__init__()
        self.api_key = api_key or os.environ.get('VOYAGE_API_KEY')
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        if not self.api_key:
            logger.warning("VOYAGE_API_KEY not set. Voyage AI client may not work properly.")
        
        logger.info(f"Voyage AI client initialized with base URL: {self.base_url}")
    
    def init_sync_client(self):
        """Initialize synchronous client (already using requests)."""
        pass
    
    def init_async_client(self):
        """Initialize async client (not implemented yet)."""
        pass
    
    def parse_embed_response(self, response: Dict[str, Any]) -> EmbedderOutput:
        """
        Parse the embedding response from Voyage AI API.
        
        Args:
            response: Raw API response
            
        Returns:
            EmbedderOutput with embeddings
        """
        try:
            # Voyage AI response format: {"object": "list", "data": [...], "model": "...", "usage": {...}}
            if isinstance(response, dict) and 'data' in response:
                data = response['data']
                # Extract embeddings from data array
                embeddings = []
                for item in data:
                    if isinstance(item, dict) and 'embedding' in item:
                        embeddings.append(item['embedding'])
                    else:
                        logger.warning(f"Unexpected data item format: {item}")
                
                if embeddings:
                    # Wrap in Embedding objects
                    embedding_objects = [
                        Embedding(embedding=emb, index=i) 
                        for i, emb in enumerate(embeddings)
                    ]
                    return EmbedderOutput(
                        data=embedding_objects,
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
        Parse Voyage AI embedding response to EmbedderOutput format.
        
        Args:
            response: The response from Voyage AI API (can be EmbedderOutput or raw response)
            
        Returns:
            EmbedderOutput with properly formatted Embedding objects
        """
        try:
            # If response is already an EmbedderOutput, return it
            if isinstance(response, EmbedderOutput):
                return response
            
            # If response is a dict with 'data' key (Voyage AI format)
            if isinstance(response, dict) and 'data' in response:
                return self.parse_embed_response(response)
            
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
        Make synchronous call to Voyage AI embedding API.
        
        Args:
            api_kwargs: Should contain 'input' (text or list of texts) and 'model'
            model_type: Type of model (embedder)
            
        Returns:
            EmbedderOutput with embeddings
        """
        try:
            if not self.api_key:
                raise ValueError("VOYAGE_API_KEY is required but not set")
            
            # Extract parameters
            text_input = api_kwargs.get('input') or api_kwargs.get('prompt')
            model = api_kwargs.get('model', 'voyage-3-large')
            input_type = api_kwargs.get('input_type', 'document')  # 'query' or 'document'
            truncation = api_kwargs.get('truncation', True)
            
            if not text_input:
                raise ValueError("No input text provided")
            
            # Handle both single string and list of strings
            if isinstance(text_input, str):
                texts = [text_input]
            else:
                texts = text_input
            
            # Prepare request payload
            payload = {
                "input": texts,
                "model": model,
                "input_type": input_type,
                "truncation": truncation
            }
            
            # Optional: encoding_format (can be "float" or "base64")
            if 'encoding_format' in api_kwargs:
                payload['encoding_format'] = api_kwargs['encoding_format']
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # Make request
            url = f"{self.base_url}/embeddings"
            logger.debug(f"Calling Voyage AI API: {url} with model: {model}")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Parse response using the helper method
            return self.parse_embed_response(result)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Voyage AI API request failed: {e}")
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = f"{error_msg}: {error_detail}"
                except:
                    pass
            return EmbedderOutput(
                data=None,
                error=error_msg,
                raw_response=None
            )
        except Exception as e:
            logger.error(f"Error in Voyage AI client call: {e}")
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

