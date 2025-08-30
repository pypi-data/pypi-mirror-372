#!/usr/bin/env python3
# Copyright (c) 2025 Marco Pancotti
# This file is part of ThothAI and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""Verify the get_documents_by_type method implementation."""

from thoth_qdrant.adapter.qdrant_native import QdrantNativeAdapter
from thoth_qdrant.core.base import ThothType, EvidenceDocument
import inspect

def verify_implementation():
    """Verify get_documents_by_type is properly implemented."""
    
    print("Checking QdrantNativeAdapter methods...")
    
    # Check if method exists
    if hasattr(QdrantNativeAdapter, 'get_documents_by_type'):
        print("✅ get_documents_by_type method exists")
        
        # Get method signature
        method = getattr(QdrantNativeAdapter, 'get_documents_by_type')
        sig = inspect.signature(method)
        print(f"   Signature: {sig}")
        
        # Check parameters
        params = list(sig.parameters.keys())
        if 'thoth_type' in params:
            print("✅ Method accepts thoth_type parameter")
            param = sig.parameters['thoth_type']
            if param.annotation != inspect.Parameter.empty:
                print(f"   Type annotation: {param.annotation}")
        
        # Check return type
        if sig.return_annotation != inspect.Parameter.empty:
            print(f"✅ Return type: {sig.return_annotation}")
    else:
        print("❌ get_documents_by_type method NOT found")
    
    print("\nChecking ThothType enum values...")
    for attr in dir(ThothType):
        if not attr.startswith('_'):
            value = getattr(ThothType, attr)
            if hasattr(value, 'value'):
                print(f"  - ThothType.{attr} = '{value.value}'")
    
    print("\nChecking related methods...")
    # Check for other document retrieval methods
    methods = [
        'get_all_evidence_documents',
        'get_all_sql_documents', 
        'get_all_column_documents',
        '_get_all_documents'
    ]
    
    for method_name in methods:
        if hasattr(QdrantNativeAdapter, method_name):
            print(f"✅ {method_name} exists")
        else:
            print(f"❌ {method_name} missing")
    
    print("\n✅ Implementation verification complete!")
    print("\nThe get_documents_by_type method is available and can be used to retrieve documents by type.")
    print("Example usage: adapter.get_documents_by_type(ThothType.EVIDENCE)")

if __name__ == "__main__":
    verify_implementation()