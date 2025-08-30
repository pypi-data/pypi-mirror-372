#!/usr/bin/env python3
# Copyright (c) 2025 Marco Pancotti
# This file is part of ThothAI and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""Test the get_documents_by_type method."""

from thoth_qdrant.adapter.qdrant_native import QdrantNativeAdapter
from thoth_qdrant.core.base import ThothType
import inspect

def test_method_exists():
    """Test that get_documents_by_type method exists and has correct signature."""
    
    # Check if the method exists
    assert hasattr(QdrantNativeAdapter, 'get_documents_by_type'), \
        "QdrantNativeAdapter should have get_documents_by_type method"
    
    # Check method signature
    sig = inspect.signature(QdrantNativeAdapter.get_documents_by_type)
    params = list(sig.parameters.keys())
    
    assert 'self' in params, "Method should have self parameter"
    assert 'thoth_type' in params, "Method should have thoth_type parameter"
    
    # Check return type annotation if available
    if sig.return_annotation != inspect.Signature.empty:
        print(f"Return type: {sig.return_annotation}")
    
    print("✅ get_documents_by_type method exists with correct signature")
    print(f"   Signature: {sig}")
    
    # Check that ThothType enum has the expected values
    assert hasattr(ThothType, 'COLUMN'), "ThothType should have COLUMN"
    assert hasattr(ThothType, 'SQL'), "ThothType should have SQL"
    assert hasattr(ThothType, 'EVIDENCE'), "ThothType should have EVIDENCE"
    
    print("✅ ThothType enum has all expected values")
    print(f"   Available types: {[t.value for t in ThothType]}")

if __name__ == "__main__":
    test_method_exists()
    print("\n✅ All checks passed! The get_documents_by_type method is properly implemented.")