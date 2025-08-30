# Copyright (c) 2025 Marco Pancotti
# This file is part of ThothAI and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""Configuration validation for ThothAI Qdrant."""

import logging
import os
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class QdrantConfig(BaseModel):
    """Configuration for Qdrant connection."""
    
    host: str = Field(default="localhost", description="Qdrant host")
    port: int = Field(default=6333, ge=1, le=65535, description="Qdrant port")
    api_key: Optional[str] = Field(default=None, description="Optional API key")
    collection: str = Field(..., description="Collection name")
    url: Optional[str] = Field(default=None, description="Full URL (overrides host/port)")
    
    @validator('collection')
    def validate_collection_name(cls, v):
        """Validate collection name format."""
        if not v or not v.strip():
            raise ValueError("Collection name cannot be empty")
        if len(v) > 255:
            raise ValueError("Collection name too long (max 255 characters)")
        return v.strip()
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format if provided."""
        if v:
            if not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError("URL must start with http:// or https://")
        return v


class EmbeddingConfig(BaseModel):
    """Configuration for embedding provider."""
    
    provider: str = Field(..., description="Embedding provider (openai, cohere, mistral, huggingface)")
    model: Optional[str] = Field(default=None, description="Model name")
    api_key: str = Field(..., description="API key for the provider")
    embedding_dim: Optional[int] = Field(default=None, ge=1, le=4096, description="Embedding dimensions")
    cache_size: int = Field(default=10000, ge=0, description="Embedding cache size")
    
    @validator('provider')
    def validate_provider(cls, v):
        """Validate provider is supported."""
        supported = ['openai', 'cohere', 'mistral', 'huggingface']
        if v.lower() not in supported:
            raise ValueError(f"Provider must be one of: {', '.join(supported)}")
        return v.lower()
    
    @validator('model')
    def set_default_model(cls, v, values):
        """Set default model based on provider if not specified."""
        if not v and 'provider' in values:
            defaults = {
                'openai': 'text-embedding-3-small',
                'cohere': 'embed-english-v3.0',
                'mistral': 'mistral-embed',
                'huggingface': 'sentence-transformers/all-MiniLM-L6-v2',
            }
            v = defaults.get(values['provider'])
        return v


class ThothConfig(BaseModel):
    """Complete configuration for ThothAI Qdrant."""
    
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = 'forbid'


def validate_config(config: Dict[str, Any]) -> ThothConfig:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Validated ThothConfig instance
        
    Raises:
        ValueError: If configuration is invalid
        
    Example:
        >>> config = {
        ...     'qdrant': {'collection': 'my_collection'},
        ...     'embedding': {'provider': 'openai', 'api_key': 'sk-...'}
        ... }
        >>> validated = validate_config(config)
    """
    try:
        return ThothConfig(**config)
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise ValueError(f"Invalid configuration: {e}") from e


def load_config_from_env() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Configuration dictionary
        
    Example:
        >>> config = load_config_from_env()
        >>> validated = validate_config(config)
    """
    from .utils import resolve_api_key
    
    # Load Qdrant config
    qdrant_config = {
        'host': os.environ.get('QDRANT_HOST', 'localhost'),
        'port': int(os.environ.get('QDRANT_PORT', 6333)),
        'collection': os.environ.get('QDRANT_COLLECTION', 'thoth_vectors'),
    }
    
    if api_key := os.environ.get('QDRANT_API_KEY'):
        qdrant_config['api_key'] = api_key
    
    if url := os.environ.get('QDRANT_URL'):
        qdrant_config['url'] = url
    
    # Load embedding config
    provider = os.environ.get('EMBEDDING_PROVIDER')
    if not provider:
        raise ValueError("EMBEDDING_PROVIDER environment variable is required")
    
    api_key = resolve_api_key(provider)
    if not api_key:
        raise ValueError(f"API key not found for provider {provider}")
    
    embedding_config = {
        'provider': provider,
        'api_key': api_key,
        'model': os.environ.get('EMBEDDING_MODEL'),
        'cache_size': int(os.environ.get('EMBEDDING_CACHE_SIZE', 10000)),
    }
    
    if dim := os.environ.get('EMBEDDING_DIM'):
        embedding_config['embedding_dim'] = int(dim)
    
    return {
        'qdrant': qdrant_config,
        'embedding': embedding_config,
    }


def validate_startup() -> bool:
    """
    Validate configuration at startup.
    
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    try:
        config = load_config_from_env()
        validated = validate_config(config)
        logger.info(f"Configuration validated: Qdrant at {validated.qdrant.host}:{validated.qdrant.port}, "
                   f"using {validated.embedding.provider} embeddings")
        return True
    except Exception as e:
        logger.error(f"Startup validation failed: {e}")
        raise