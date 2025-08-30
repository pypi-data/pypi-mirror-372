# Copyright (c) 2025 Marco Pancotti
# This file is part of ThothAI and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""Utility functions for ThothAI Qdrant."""

import logging
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def resolve_api_key(provider_type: str) -> Optional[str]:
    """
    Resolve API key for a given provider from environment variables.
    
    Args:
        provider_type: The embedding provider type (openai, cohere, mistral, huggingface)
    
    Returns:
        The API key if found, None otherwise
        
    Example:
        >>> api_key = resolve_api_key('openai')
        >>> if api_key:
        ...     print("API key found")
    """
    # Define provider-specific environment variable mappings
    env_key_mappings = {
        'openai': ['OPENAI_API_KEY', 'OPENAI_KEY'],
        'cohere': ['COHERE_API_KEY', 'COHERE_KEY'],
        'mistral': ['MISTRAL_API_KEY', 'MISTRAL_KEY'],
        'huggingface': ['HUGGINGFACE_API_KEY', 'HF_API_KEY', 'HUGGINGFACE_TOKEN'],
    }
    
    # Check provider-specific keys first
    provider_keys = env_key_mappings.get(provider_type, [])
    for env_key in provider_keys:
        api_key = os.environ.get(env_key)
        if api_key:
            logger.info("API key found in environment variable")
            return api_key
    
    # Fall back to generic API key
    api_key = os.environ.get('EMBEDDING_API_KEY')
    if api_key:
        logger.info("API key found in environment variable")
        return api_key
    
    return None


def get_embedding_config(provider_type: Optional[str] = None, 
                        model: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Get complete embedding configuration from environment.
    
    Args:
        provider_type: Override provider type (defaults to EMBEDDING_PROVIDER env var)
        model: Override model name (defaults to EMBEDDING_MODEL env var)
    
    Returns:
        Tuple of (provider, api_key, model)
    
    Raises:
        ValueError: If configuration is incomplete or invalid
        
    Example:
        >>> provider, api_key, model = get_embedding_config()
        >>> print(f"Using {provider} with {model}")
    """
    # Get provider
    if not provider_type:
        provider_type = os.environ.get('EMBEDDING_PROVIDER')
    
    if not provider_type:
        raise ValueError(
            "Embedding provider not specified. "
            "Set EMBEDDING_PROVIDER environment variable or pass provider_type parameter."
        )
    
    # Get API key
    api_key = resolve_api_key(provider_type)
    if not api_key:
        raise ValueError(
            f"API key not found for provider {provider_type}. "
            f"Please set the appropriate environment variable."
        )
    
    # Get model with provider-specific defaults
    if not model:
        model = os.environ.get('EMBEDDING_MODEL')
    
    if not model:
        # Provider-specific defaults
        defaults = {
            'openai': 'text-embedding-3-small',
            'cohere': 'embed-english-v3.0',
            'mistral': 'mistral-embed',
            'huggingface': 'sentence-transformers/all-MiniLM-L6-v2',
        }
        model = defaults.get(provider_type, 'text-embedding-3-small')
        logger.info(f"Using default model for {provider_type}: {model}")
    
    return provider_type, api_key, model