# Copyright (c) 2025 Marco Pancotti
# This file is part of ThothAI and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""Factory for creating vector store instances."""

import logging
from typing import Any, Dict

from .adapter.qdrant_native import QdrantNativeAdapter
from .core.base import VectorStoreInterface
from .core.config import validate_config, load_config_from_env

logger = logging.getLogger(__name__)


class VectorStoreFactory:
    """Factory for creating vector store instances."""
    
    _adapters: Dict[str, Any] = {}
    _initialized = False
    
    @classmethod
    def _initialize_adapters(cls):
        """Initialize available adapters."""
        if cls._initialized:
            return
        
        # Register Qdrant native adapter
        cls._adapters["qdrant"] = QdrantNativeAdapter
        
        cls._initialized = True
        logger.info(f"Initialized vector store factory with adapters: {list(cls._adapters.keys())}")
    
    @classmethod
    def create(
        cls,
        backend: str,
        collection: str,
        **kwargs
    ) -> VectorStoreInterface:
        """Create a vector store instance.
        
        Args:
            backend: Backend type (currently only 'qdrant')
            collection: Collection name
            **kwargs: Backend-specific parameters
            
        Returns:
            Vector store instance
            
        Raises:
            ValueError: If backend is not supported
        """
        cls._initialize_adapters()
        
        if backend not in cls._adapters:
            available_backends = list(cls._adapters.keys())
            raise ValueError(
                f"Unsupported backend: {backend}. "
                f"Available backends: {available_backends}"
            )
        
        adapter_class = cls._adapters[backend]
        return adapter_class(collection=collection, **kwargs)
    
    @classmethod
    def from_validated_config(cls, config: Dict[str, Any]) -> VectorStoreInterface:
        """Create vector store from validated configuration.
        
        Args:
            config: Configuration dictionary with 'qdrant' and 'embedding' sections
            
        Returns:
            Vector store instance
            
        Example:
            >>> config = {
            ...     'qdrant': {'collection': 'my_collection'},
            ...     'embedding': {'provider': 'openai', 'api_key': 'sk-...'}
            ... }
            >>> store = VectorStoreFactory.from_validated_config(config)
        """
        # Validate configuration
        validated = validate_config(config)
        
        # Extract parameters
        params = {
            'collection': validated.qdrant.collection,
            'host': validated.qdrant.host,
            'port': validated.qdrant.port,
            'embedding_provider': validated.embedding.provider,
            'embedding_model': validated.embedding.model,
        }
        
        if validated.qdrant.api_key:
            params['api_key'] = validated.qdrant.api_key
        if validated.qdrant.url:
            params['url'] = validated.qdrant.url
        if validated.embedding.embedding_dim:
            params['embedding_dim'] = validated.embedding.embedding_dim
            
        return cls.create('qdrant', **params)
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> VectorStoreInterface:
        """Create vector store from configuration.
        
        Args:
            config: Configuration dictionary with 'backend' and 'params'
            
        Returns:
            Vector store instance
            
        Example:
            config = {
                "backend": "qdrant",
                "params": {
                    "collection": "my_collection",
                    "host": "localhost",
                    "port": 6333,
                    "embedding_provider": "openai",
                    "embedding_model": "text-embedding-3-small"
                }
            }
        """
        backend = config.get("backend")
        if not backend:
            raise ValueError("Configuration must include 'backend' key")
        
        params = config.get("params", {})
        return cls.create(backend, **params)
    
    @classmethod
    def from_env(cls) -> VectorStoreInterface:
        """Create vector store from environment variables.
        
        Returns:
            Vector store instance
            
        Raises:
            ValueError: If required environment variables are missing
            
        Example:
            >>> # Set environment variables first
            >>> # EMBEDDING_PROVIDER=openai
            >>> # OPENAI_API_KEY=sk-...
            >>> store = VectorStoreFactory.from_env()
        """
        config = load_config_from_env()
        return cls.from_validated_config(config)
    
    @classmethod
    def list_backends(cls) -> list[str]:
        """List available backends."""
        cls._initialize_adapters()
        return list(cls._adapters.keys())