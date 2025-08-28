"""MCP tools for embedding services."""

import logging
from copy import deepcopy
from typing import Any, Dict, List

from mcp.types import Tool

from .embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)


class EmbeddingTools:
    """MCP tools for 360 Research embedding services."""
    
    def __init__(self):
        """Initialize the embedding tools."""
        self.client = EmbeddingClient()
        self.result = {"success":False, "embedding":None, "error_msg":""}
    
    def get_tools(self) -> List[Tool]:
        """Get the list of available tools."""
        return [
            Tool(
                name="text_embedding",
                description="Generate embeddings for text using 360 Research API",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "texts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of text strings to embed"
                        },
                        "model": {
                            "type": "string",
                            "default": "fg-clip",
                            "description": "Model to use for embedding"
                        },
                        "embedding_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["float"],
                            "description": "Types of embeddings to return"
                        },
                        "truncate": {
                            "type": "string",
                            "enum": ["start", "end", "none"],
                            "default": "start",
                            "description": "Truncation strategy for long texts"
                        }
                    },
                    "required": ["texts"]
                }
            ),
            Tool(
                name="image_embedding",
                description="Generate embeddings for images using 360 Research API",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "images": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of image URLs or base64 encoded images"
                        },
                        "model": {
                            "type": "string",
                            "default": "fg-clip",
                            "description": "Model to use for embedding"
                        },
                        "embedding_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["float"],
                            "description": "Types of embeddings to return"
                        }
                    },
                    "required": ["images"]
                }
            ),
            Tool(
                name="embedding",
                description="Generate embeddings for text or images using 360 Research API",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "inputs": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of text strings or image URLs/base64"
                        },
                        "input_type": {
                            "type": "string",
                            "enum": ["text", "image"],
                            "description": "Type of input to embed"
                        },
                        "model": {
                            "type": "string",
                            "default": "fg-clip",
                            "description": "Model to use for embedding"
                        },
                        "embedding_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["float"],
                            "description": "Types of embeddings to return"
                        },
                        "truncate": {
                            "type": "string",
                            "enum": ["start", "end", "none"],
                            "default": "start",
                            "description": "Truncation strategy (only for text)"
                        }
                    },
                    "required": ["inputs", "input_type"]
                }
            )
        ]
    
    async def call_text_embedding(self, arguments: Dict[str, Any]) -> dict:
        """Call the text embedding tool."""
        cur_result = deepcopy(self.result)
        try:
            texts = arguments.get("texts", [])
            model = arguments.get("model", "fg-clip")
            embedding_types = arguments.get("embedding_types", ["float"])
            truncate = arguments.get("truncate", "start")
            
            if not texts:
                cur_result['error_msg'] = "Error: No texts provided"
                return cur_result
            
            result = await self.client.get_text_embeddings(
                texts=texts,
                model=model,
                embedding_types=embedding_types,
                truncate=truncate
            )
            cur_result["embedding"] = result['data']["embeddings"][embedding_types[0]][0]
            cur_result["success"] = True
            return cur_result
        except Exception as e:
            logger.error(f"Error in text_embedding tool: {e}")
            cur_result["error_msg"] = str(e)
            return cur_result
    
    async def call_image_embedding(self, arguments: Dict[str, Any]) -> dict:
        """Call the image embedding tool."""
        cur_result = deepcopy(self.result)
        try:
            images = arguments.get("images", [])
            model = arguments.get("model", "fg-clip")
            embedding_types = arguments.get("embedding_types", ["float"])
            
            if not images:
                cur_result['error_msg'] = "Error: No images provided"
            
            result = await self.client.get_image_embeddings(
                images=images,
                model=model,
                embedding_types=embedding_types
            )
            cur_result["embedding"] = result['data']["embeddings"][embedding_types[0]][0]
            cur_result["success"] = True
            return cur_result
            
        except Exception as e:
            logger.error(f"Error in image_embedding tool: {e}")
            cur_result["error_msg"] = str(e)
            return cur_result
    
    async def call_embedding(self, arguments: Dict[str, Any]) -> dict:
        """Call the general embedding tool."""
        cur_result = deepcopy(self.result)        
        try:
            inputs = arguments.get("inputs", [])
            input_type = arguments.get("input_type")
            model = arguments.get("model", "fg-clip")
            embedding_types = arguments.get("embedding_types", ["float"])
            truncate = arguments.get("truncate", "start")
            
            if not inputs:
                return "Error: No inputs provided"
            
            if not input_type:
                return "Error: input_type is required"
            
            result = await self.client.get_embeddings(
                inputs=inputs,
                input_type=input_type,
                model=model,
                embedding_types=embedding_types,
                truncate=truncate
            )
            cur_result["embedding"] = result['data']["embeddings"][embedding_types[0]][0]
            cur_result["success"] = True
            return cur_result
            
        except Exception as e:
            logger.error(f"Error in embedding tool: {e}")
            cur_result["error_msg"] = str(e)
            return cur_result
