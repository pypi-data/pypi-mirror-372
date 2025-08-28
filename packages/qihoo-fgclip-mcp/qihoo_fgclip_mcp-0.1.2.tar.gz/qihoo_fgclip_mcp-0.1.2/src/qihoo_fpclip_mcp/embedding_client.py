"""360 Research API client for embedding services."""
import os
import logging
from typing import List, Dict, Any
from urllib.parse import urlparse

import httpx


logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Client for 360 Research embedding API."""
    
    def __init__(self):
        self.base_url = os.getenv("MCP_API_BASE_URL", "https://api.research.360.cn/models/interface")
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        self.api_key = os.getenv("MCP_API_KEY",None)
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if a string is a valid URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _is_base64_image(self, data: str) -> bool:
        """Check if a string is a base64 encoded image."""
        return data.startswith("data:image/")
    
    async def get_text_embeddings(
        self, 
        texts: List[str], 
        model: str = "fg-clip",
        embedding_types: List[str] = None,
        truncate: str = "start"
    ) -> Dict[str, Any]:
        """Get text embeddings from 360 Research API.
        
        Args:
            texts: List of text strings to embed
            model: Model name to use for embedding
            embedding_types: Types of embeddings to return
            truncate: Truncation strategy ("start", "end", "none")
            
        Returns:
            API response containing embeddings
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        if embedding_types is None:
            embedding_types = ["float"]
        
        payload = {
            "model": model,
            "input_type": "text",
            "embedding_types": embedding_types,
            "texts": texts,
            "truncate": truncate
        }
        
        logger.info(f"Requesting text embeddings for {len(texts)} texts")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={**self.headers},
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_image_embeddings(
        self, 
        images: List[str], 
        model: str = "fg-clip",
        embedding_types: List[str] = None
    ) -> Dict[str, Any]:
        """Get image embeddings from 360 Research API.
        
        Args:
            images: List of image URLs or base64 encoded images
            model: Model name to use for embedding
            embedding_types: Types of embeddings to return
            
        Returns:
            API response containing embeddings
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        if embedding_types is None:
            embedding_types = ["float"]
        
        payload = {
            "model": model,
            "input_type": "image",
            "embedding_types": embedding_types,
            "images": images
        }
        
        logger.info(f"Requesting image embeddings for {len(images)} images")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={**self.headers},
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_embeddings(
        self, 
        inputs: List[str], 
        input_type: str,
        model: str = "fg-clip",
        embedding_types: List[str] = None,
        truncate: str = "start"
    ) -> Dict[str, Any]:
        """Get embeddings for text or images from 360 Research API.
        
        Args:
            inputs: List of text strings or image URLs/base64
            input_type: Type of input ("text" or "image")
            model: Model name to use for embedding
            embedding_types: Types of embeddings to return
            truncate: Truncation strategy for text (only used for text input)
            
        Returns:
            API response containing embeddings
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        if embedding_types is None:
            embedding_types = ["float"]
        
        payload = {
            "model": model,
            "input_type": input_type,
            "embedding_types": embedding_types
        }
        
        if input_type == "text":
            payload["texts"] = inputs
            payload["truncate"] = truncate
            logger.info(f"Requesting text embeddings for {len(inputs)} texts")
        elif input_type == "image":
            payload["images"] = inputs
            logger.info(f"Requesting image embeddings for {len(inputs)} images")
        else:
            raise ValueError(f"Unsupported input_type: {input_type}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={**self.headers},
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
