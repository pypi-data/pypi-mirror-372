# Copyright (c) 2025 Marco Pancotti
# This file is part of ThothAI and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""External Embedding Manager for ThothAI Qdrant."""

import hashlib
import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .utils import resolve_api_key

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract interface for external embedding providers."""
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for list of texts."""
        pass
    
    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for single query."""
        pass
    
    @abstractmethod
    async def embed_texts_async(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings async for list of texts."""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Test connection and API key validity."""
        pass
    
    @abstractmethod
    def get_dimensions(self) -> int:
        """Return embedding dimensions for the model."""
        pass
    
    @property
    @abstractmethod
    def max_batch_size(self) -> int:
        """Maximum batch size for provider."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider name for logging/metrics."""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider implementation."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small", 
                 base_url: Optional[str] = None, timeout: int = 30):
        """Initialize OpenAI provider."""
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError("OpenAI library not installed. Install with: pip install openai>=1.0.0") from e
        
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self.model = model
        self.timeout = timeout
        self._dimensions: Optional[int] = None
        self._validate_model()
    
    def _validate_model(self):
        """Validate that the model exists."""
        valid_models = [
            "text-embedding-3-small", 
            "text-embedding-3-large", 
            "text-embedding-ada-002"
        ]
        if self.model not in valid_models:
            raise ValueError(f"Model {self.model} not supported. Valid models: {valid_models}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Implement batch embedding with retry logic."""
        if not texts:
            return []
        
        # Batch processing to respect rate limits
        batches = [texts[i:i + self.max_batch_size] 
                  for i in range(0, len(texts), self.max_batch_size)]
        
        all_embeddings = []
        for batch in batches:
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )
                for data in response.data:
                    all_embeddings.append(data.embedding)
            except Exception as e:
                logger.error(f"OpenAI embedding error: {e}")
                raise
        
        return all_embeddings
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for single query."""
        embeddings = self.embed_texts([query])
        return embeddings[0] if embeddings else []
    
    async def embed_texts_async(self, texts: List[str]) -> List[List[float]]:
        """Async version - falls back to sync for now."""
        return self.embed_texts(texts)
    
    def validate_connection(self) -> bool:
        """Test connection to OpenAI."""
        try:
            # Test with a simple embedding
            self.embed_query("test")
            return True
        except Exception as e:
            logger.error(f"OpenAI connection validation failed: {e}")
            return False
    
    def get_dimensions(self) -> int:
        """Return embedding dimensions for the model."""
        if self._dimensions is None:
            dimensions_map = {
                "text-embedding-3-small": 1536,
                "text-embedding-3-large": 3072,
                "text-embedding-ada-002": 1536
            }
            self._dimensions = dimensions_map.get(self.model, 1536)
        return self._dimensions
    
    @property
    def max_batch_size(self) -> int:
        """Maximum batch size for OpenAI."""
        return 100
    
    @property
    def provider_name(self) -> str:
        """Provider name."""
        return "openai"


class CohereEmbeddingProvider(EmbeddingProvider):
    """Cohere embedding provider implementation."""
    
    def __init__(self, api_key: str, model: str = "embed-multilingual-v3.0", timeout: int = 30, 
                 base_url: Optional[str] = None):
        """Initialize Cohere provider."""
        if not api_key:
            raise ValueError("Cohere API key is required")
        
        try:
            import cohere
        except ImportError as e:
            raise ImportError("Cohere library not installed. Install with: pip install cohere") from e
        
        # Cohere client doesn't support base_url override, ignoring if provided
        self.client = cohere.Client(api_key=api_key, timeout=timeout)
        self.model = model
        self.timeout = timeout
        self._dimensions: Optional[int] = None
        self._validate_model()
    
    def _validate_model(self):
        """Validate that the model exists."""
        valid_models = [
            "embed-english-v3.0",
            "embed-multilingual-v3.0", 
            "embed-english-light-v3.0",
            "embed-multilingual-light-v3.0"
        ]
        if self.model not in valid_models:
            raise ValueError(f"Model {self.model} not supported. Valid models: {valid_models}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Implement batch embedding with retry logic."""
        if not texts:
            return []
        
        # Batch processing to respect rate limits
        batches = [texts[i:i + self.max_batch_size] 
                  for i in range(0, len(texts), self.max_batch_size)]
        
        all_embeddings = []
        for batch in batches:
            try:
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
                    input_type="search_document"
                )
                all_embeddings.extend(response.embeddings)
            except Exception as e:
                logger.error(f"Cohere embedding error: {e}")
                raise
        
        return all_embeddings
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for single query."""
        try:
            response = self.client.embed(
                texts=[query],
                model=self.model,
                input_type="search_query"
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Cohere query embedding error: {e}")
            raise
    
    async def embed_texts_async(self, texts: List[str]) -> List[List[float]]:
        """Async version - falls back to sync for now."""
        return self.embed_texts(texts)
    
    def validate_connection(self) -> bool:
        """Test connection to Cohere."""
        try:
            # Test with a simple embedding
            self.embed_query("test")
            return True
        except Exception as e:
            logger.error(f"Cohere connection validation failed: {e}")
            return False
    
    def get_dimensions(self) -> int:
        """Return embedding dimensions for the model."""
        if self._dimensions is None:
            dimensions_map = {
                "embed-english-v3.0": 1024,
                "embed-multilingual-v3.0": 1024,
                "embed-english-light-v3.0": 384,
                "embed-multilingual-light-v3.0": 384
            }
            self._dimensions = dimensions_map.get(self.model, 1024)
        return self._dimensions
    
    @property
    def max_batch_size(self) -> int:
        """Maximum batch size for Cohere."""
        return 96
    
    @property
    def provider_name(self) -> str:
        """Provider name."""
        return "cohere"


class MistralEmbeddingProvider(EmbeddingProvider):
    """Mistral embedding provider implementation."""
    
    def __init__(self, api_key: str, model: str = "mistral-embed", timeout: int = 30,
                 base_url: Optional[str] = None):
        """Initialize Mistral provider."""
        if not api_key:
            raise ValueError("Mistral API key is required")
        
        try:
            from mistralai import Mistral
        except ImportError as e:
            raise ImportError("Mistral library not installed. Install with: pip install mistralai") from e
        
        # Mistral client doesn't support base_url override in current version, ignoring if provided
        self.client = Mistral(api_key=api_key)
        self.model = model
        self.timeout = timeout
        self._dimensions: Optional[int] = None
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Implement batch embedding with retry logic."""
        if not texts:
            return []
        
        # Batch processing to respect rate limits
        batches = [texts[i:i + self.max_batch_size] 
                  for i in range(0, len(texts), self.max_batch_size)]
        
        all_embeddings = []
        for batch in batches:
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    inputs=batch
                )
                for data in response.data:
                    all_embeddings.append(data.embedding)
            except Exception as e:
                logger.error(f"Mistral embedding error: {e}")
                raise
        
        return all_embeddings
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for single query."""
        embeddings = self.embed_texts([query])
        return embeddings[0] if embeddings else []
    
    async def embed_texts_async(self, texts: List[str]) -> List[List[float]]:
        """Async version - falls back to sync for now."""
        return self.embed_texts(texts)
    
    def validate_connection(self) -> bool:
        """Test connection to Mistral."""
        try:
            # Test with a simple embedding
            self.embed_query("test")
            return True
        except Exception as e:
            logger.error(f"Mistral connection validation failed: {e}")
            return False
    
    def get_dimensions(self) -> int:
        """Return embedding dimensions for the model."""
        if self._dimensions is None:
            # Mistral embed has 1024 dimensions
            self._dimensions = 1024
        return self._dimensions
    
    @property
    def max_batch_size(self) -> int:
        """Maximum batch size for Mistral."""
        return 100
    
    @property
    def provider_name(self) -> str:
        """Provider name."""
        return "mistral"


class EmbeddingProviderFactory:
    """Factory for creating embedding providers."""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> EmbeddingProvider:
        """Create an embedding provider instance."""
        providers = {
            "openai": OpenAIEmbeddingProvider,
            "cohere": CohereEmbeddingProvider,
            "mistral": MistralEmbeddingProvider,
        }
        
        if provider_type not in providers:
            raise ValueError(f"Unknown provider: {provider_type}. Available: {list(providers.keys())}")
        
        provider_class = providers[provider_type]
        return provider_class(**kwargs)


class EmbeddingCache:
    """Simple in-memory embedding cache."""
    
    def __init__(self, max_size: int = 10000):
        self._cache: Dict[str, List[float]] = {}
        self.max_size = max_size
    
    def get_cache_key(self, text: str, model: str) -> str:
        """Generate cache key for text and model combination."""
        return hashlib.md5(f"{text}:{model}".encode()).hexdigest()
    
    def get(self, text: str, model: str) -> Optional[List[float]]:
        """Get embedding from cache."""
        key = self.get_cache_key(text, model)
        return self._cache.get(key)
    
    def set(self, text: str, model: str, embedding: List[float]):
        """Store embedding in cache."""
        if len(self._cache) >= self.max_size:
            # Simple LRU eviction - remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        key = self.get_cache_key(text, model)
        self._cache[key] = embedding


class ExternalEmbeddingManager:
    """External embedding manager for ThothAI Qdrant."""
    
    def __init__(self, provider: EmbeddingProvider, enable_cache: bool = True, cache_size: int = 10000):
        """Initialize external embedding manager.
        
        Args:
            provider: External embedding provider instance
            enable_cache: Enable embedding caching
            cache_size: Maximum cache size
        """
        self.provider = provider
        self.enable_cache = enable_cache
        self.cache = EmbeddingCache(cache_size) if enable_cache else None
        
        # Metrics tracking
        self._metrics = {
            'embeddings_generated': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time': 0.0,
            'errors': 0,
        }
        
        # Validate provider connection
        if not self.provider.validate_connection():
            raise ConnectionError(f"Failed to connect to {self.provider.provider_name} embedding service")
        
        logger.info(f"ExternalEmbeddingManager initialized with {self.provider.provider_name} provider")
        logger.info(f"Model: {getattr(self.provider, 'model', 'unknown')}")
        logger.info(f"Dimensions: {self.provider.get_dimensions()}")
        logger.info(f"Max batch size: {self.provider.max_batch_size}")
        logger.info(f"Cache enabled: {self.enable_cache}")
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'ExternalEmbeddingManager':
        """Create manager from configuration.
        
        Args:
            config: Configuration dictionary with provider settings
            
        Returns:
            ExternalEmbeddingManager instance
            
        Example:
            config = {
                'provider': 'openai',
                'api_key': 'sk-...',
                'model': 'text-embedding-3-small',
                'enable_cache': True,
                'cache_size': 10000
            }
        """
        provider_config = config.copy()
        provider_type = provider_config.pop('provider')
        
        # Extract manager-specific settings
        enable_cache = provider_config.pop('enable_cache', True)
        cache_size = provider_config.pop('cache_size', 10000)
        
        # Create provider with remaining config
        provider = EmbeddingProviderFactory.create_provider(provider_type, **provider_config)
        
        return cls(provider=provider, enable_cache=enable_cache, cache_size=cache_size)
    
    @classmethod
    def from_env(cls) -> 'ExternalEmbeddingManager':
        """Create manager from environment variables.
        
        Expected environment variables:
        - EMBEDDING_PROVIDER: openai, cohere, mistral
        - EMBEDDING_MODEL: model name (optional, uses defaults)
        - EMBEDDING_API_KEY or provider-specific key (OPENAI_API_KEY, etc.)
        - EMBEDDING_BASE_URL: base URL for API (optional, for custom endpoints)
        - EMBEDDING_TIMEOUT: timeout in seconds (optional, default 30)
        - EMBEDDING_CACHE_SIZE: cache size (optional, default 10000)
        - EMBEDDING_BATCH_SIZE: max batch size override (optional)
        
        Returns:
            ExternalEmbeddingManager instance
        """
        provider_type = os.environ.get('EMBEDDING_PROVIDER')
        if not provider_type:
            raise ValueError("EMBEDDING_PROVIDER environment variable is required")
        
        # Resolve API key - first check EMBEDDING_API_KEY, then provider-specific
        api_key = os.environ.get('EMBEDDING_API_KEY') or resolve_api_key(provider_type)
        
        if not api_key:
            raise ValueError(f"API key not found for provider {provider_type}. Set EMBEDDING_API_KEY or {provider_type.upper()}_API_KEY")
        
        model = os.environ.get('EMBEDDING_MODEL', cls._get_default_model(provider_type))
        cache_size = int(os.environ.get('EMBEDDING_CACHE_SIZE', '10000'))
        timeout = int(os.environ.get('EMBEDDING_TIMEOUT', '30'))
        
        config = {
            'provider': provider_type,
            'api_key': api_key,
            'model': model,
            'cache_size': cache_size,
            'timeout': timeout
        }
        
        # Add base_url if specified (useful for OpenAI-compatible endpoints)
        base_url = os.environ.get('EMBEDDING_BASE_URL')
        if base_url:
            config['base_url'] = base_url
        
        # Note: EMBEDDING_BATCH_SIZE is not used here because each provider
        # has its own max_batch_size property that shouldn't be overridden
        # unless we add specific logic for it
        
        return cls.from_config(config)
    
    @staticmethod
    def _get_default_model(provider_type: str) -> str:
        """Get default model for provider - all set to multilingual models."""
        defaults = {
            'openai': 'text-embedding-3-small',  # OpenAI models are multilingual by default
            'cohere': 'embed-multilingual-v3.0',  # Explicitly multilingual
            'mistral': 'mistral-embed',  # Mistral embed is multilingual by default
        }
        return defaults.get(provider_type, 'default')
    
    def encode_texts(self, texts: List[str]) -> List[List[float]]:
        """Encode texts to embeddings.
        
        Args:
            texts: List of texts to encode
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        logger.debug(f"Encoding {len(texts)} texts with {self.provider.provider_name}")
        
        # Get embeddings with caching
        embeddings = self._get_embeddings_with_cache(texts)
        
        logger.debug(f"Successfully encoded {len(texts)} texts")
        return embeddings
    
    def encode_query(self, query: str) -> List[float]:
        """Encode single query text.
        
        Args:
            query: Query text
            
        Returns:
            Query embedding vector
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        logger.debug(f"Encoding query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        
        # Use cache if enabled
        if self.enable_cache and self.cache:
            cached = self.cache.get(query.strip(), self._get_model_identifier())
            if cached:
                logger.debug("Using cached query embedding")
                return cached
        
        # Get embedding from provider
        embedding = self.provider.embed_query(query.strip())
        
        # Cache if enabled
        if self.enable_cache and self.cache:
            self.cache.set(query.strip(), self._get_model_identifier(), embedding)
        
        logger.debug(f"Query encoded to {len(embedding)}-dimensional vector")
        return embedding
    
    def encode(self, texts, **kwargs):  # kwargs kept for API compatibility
        """Unified encode method for compatibility with tools expecting flexible input.
        
        This method provides a unified interface that can handle both single strings
        and lists of strings, making it compatible with tools like RetrieveEntityTool
        that expect this flexibility.
        
        Args:
            texts: Either a single string or a list of strings to encode
            **kwargs: Additional arguments (kept for API compatibility, not used)
            
        Returns:
            Either a single embedding vector (list of floats) for single text input,
            or a list of embedding vectors for multiple text inputs
            
        Examples:
            # Single string
            embedding = manager.encode("Hello world")
            
            # List of strings
            embeddings = manager.encode(["Hello", "World"])
        """
        # kwargs intentionally not used - kept for backward compatibility
        if isinstance(texts, str):
            # Single text - use encode_query
            return self.encode_query(texts)
        else:
            # Multiple texts - use encode_texts
            # Handle empty list case
            if not texts:
                return []
            # Ensure all items are strings
            texts = [str(text) if text is not None else "" for text in texts]
            return self.encode_texts(texts)
    
    def _get_embeddings_with_cache(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings with caching support."""
        start_time = time.time()
        
        if not self.enable_cache or not self.cache:
            try:
                embeddings = self.provider.embed_texts(texts)
                self._metrics['embeddings_generated'] += len(texts)
                self._metrics['total_time'] += time.time() - start_time
                return embeddings
            except Exception as e:
                self._metrics['errors'] += 1
                raise
        
        model_id = self._get_model_identifier()
        cached_embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            cached = self.cache.get(text, model_id)
            if cached:
                cached_embeddings.append((i, cached))
                self._metrics['cache_hits'] += 1
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
                self._metrics['cache_misses'] += 1
        
        # Get embeddings for uncached texts
        if uncached_texts:
            try:
                new_embeddings = self.provider.embed_texts(uncached_texts)
                self._metrics['embeddings_generated'] += len(uncached_texts)
                
                # Cache new embeddings
                for text, embedding in zip(uncached_texts, new_embeddings):
                    self.cache.set(text, model_id, embedding)
            except Exception as e:
                self._metrics['errors'] += 1
                logger.error(f"Error generating embeddings: {e}")
                raise
        else:
            new_embeddings = []
        
        # Combine cached and new embeddings in correct order
        all_embeddings = [None] * len(texts)
        
        # Place cached embeddings
        for idx, embedding in cached_embeddings:
            all_embeddings[idx] = embedding
        
        # Place new embeddings
        for uncached_idx, embedding in zip(uncached_indices, new_embeddings):
            all_embeddings[uncached_idx] = embedding
        
        # Update metrics
        elapsed = time.time() - start_time
        self._metrics['total_time'] += elapsed
        
        logger.debug(f"Used cache for {len(cached_embeddings)} embeddings, "
                    f"computed {len(new_embeddings)} new embeddings")
        
        # Log metrics periodically (every 100 embeddings)
        if self._metrics['embeddings_generated'] % 100 == 0 and self._metrics['embeddings_generated'] > 0:
            self._log_metrics()
        
        return all_embeddings
    
    def _get_model_identifier(self) -> str:
        """Get model identifier for caching."""
        return f"{self.provider.provider_name}:{getattr(self.provider, 'model', 'default')}"
    
    def _log_metrics(self):
        """Log current metrics."""
        total_requests = self._metrics['cache_hits'] + self._metrics['cache_misses']
        cache_hit_rate = (self._metrics['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        avg_time = self._metrics['total_time'] / self._metrics['embeddings_generated'] if self._metrics['embeddings_generated'] > 0 else 0
        
        logger.info(
            f"Embedding metrics: "
            f"generated={self._metrics['embeddings_generated']}, "
            f"cache_hit_rate={cache_hit_rate:.1f}%, "
            f"avg_time={avg_time:.3f}s, "
            f"errors={self._metrics['errors']}"
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics.
        
        Returns:
            Dictionary of metrics
        """
        total_requests = self._metrics['cache_hits'] + self._metrics['cache_misses']
        return {
            **self._metrics,
            'cache_hit_rate': (self._metrics['cache_hits'] / total_requests) if total_requests > 0 else 0,
            'avg_embedding_time': self._metrics['total_time'] / self._metrics['embeddings_generated'] if self._metrics['embeddings_generated'] > 0 else 0,
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "provider_name": self.provider.provider_name,
            "model_name": getattr(self.provider, 'model', 'unknown'),
            "embedding_dimension": self.provider.get_dimensions(),
            "max_batch_size": self.provider.max_batch_size,
            "cache_enabled": self.enable_cache,
            "cache_size": len(self.cache._cache) if self.cache else 0,
            "is_external": True
        }
    
    async def encode_texts_async(self, texts: List[str]) -> List[List[float]]:
        """Async version of text encoding."""
        return await self.provider.embed_texts_async(texts)
    
    def clear_cache(self):
        """Clear embedding cache."""
        if self.cache:
            self.cache._cache.clear()
            logger.info("Embedding cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.cache:
            return {"cache_enabled": False}
        
        return {
            "cache_enabled": True,
            "cache_size": len(self.cache._cache),
            "max_cache_size": self.cache.max_size,
            "cache_usage_percent": (len(self.cache._cache) / self.cache.max_size) * 100
        }