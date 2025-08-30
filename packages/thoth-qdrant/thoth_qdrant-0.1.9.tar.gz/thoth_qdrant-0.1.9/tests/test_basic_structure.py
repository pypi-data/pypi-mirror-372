#!/usr/bin/env python3
# Copyright (c) 2025 Marco Pancotti
# This file is part of ThothAI and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""Test basic structure without real embeddings."""

import os
import sys

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from thoth_qdrant.core.base import (
    ColumnNameDocument,
    SqlDocument,
    EvidenceDocument,
    ThothType,
)


def test_document_models():
    """Test that document models work correctly."""
    print("Testing Document Models")
    print("="*50)
    
    # Test ColumnNameDocument
    print("\n1. Testing ColumnNameDocument...")
    column_doc = ColumnNameDocument(
        table_name="users",
        column_name="email",
        original_column_name="email_address",
        column_description="User's email address",
        value_description="Valid email format"
    )
    print(f"✅ Created ColumnNameDocument with ID: {column_doc.id}")
    print(f"   Type: {column_doc.thoth_type}")
    assert column_doc.thoth_type == ThothType.COLUMN_NAME
    
    # Test SqlDocument
    print("\n2. Testing SqlDocument...")
    sql_doc = SqlDocument(
        question="How to find recent users?",
        sql="SELECT * FROM users WHERE created_at > NOW() - INTERVAL '30 days'",
        evidence="Filter by date"
    )
    print(f"✅ Created SqlDocument with ID: {sql_doc.id}")
    print(f"   Type: {sql_doc.thoth_type}")
    assert sql_doc.thoth_type == ThothType.SQL
    
    # Test EvidenceDocument
    print("\n3. Testing EvidenceDocument...")
    evidence_doc = EvidenceDocument(
        evidence="Use indexes for better performance"
    )
    print(f"✅ Created EvidenceDocument with ID: {evidence_doc.id}")
    print(f"   Type: {evidence_doc.thoth_type}")
    assert evidence_doc.thoth_type == ThothType.EVIDENCE
    
    print("\n✅ All document models working correctly!")
    return True


def test_factory_import():
    """Test that factory can be imported."""
    print("\nTesting Factory Import")
    print("="*50)
    
    from thoth_qdrant import VectorStoreFactory
    
    print("✅ VectorStoreFactory imported successfully")
    
    # List available backends
    backends = VectorStoreFactory.list_backends()
    print(f"✅ Available backends: {backends}")
    assert "qdrant" in backends
    
    return True


def test_embedding_manager_structure():
    """Test embedding manager structure."""
    print("\nTesting Embedding Manager Structure")
    print("="*50)
    
    from thoth_qdrant.core.embedding_manager import (
        EmbeddingProvider,
        EmbeddingProviderFactory,
        EmbeddingCache,
        ExternalEmbeddingManager,
    )
    
    print("✅ All embedding manager components imported")
    
    # Test cache
    cache = EmbeddingCache(max_size=100)
    test_key = cache.get_cache_key("test text", "test-model")
    print(f"✅ Cache key generation works: {test_key[:10]}...")
    
    return True


def test_qdrant_connection():
    """Test direct Qdrant connection."""
    print("\nTesting Qdrant Connection")
    print("="*50)
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections()
        print(f"✅ Connected to Qdrant")
        print(f"   Existing collections: {[c.name for c in collections.collections]}")
        
        # Try to create a test collection
        test_collection = "test_structure_collection"
        try:
            client.delete_collection(test_collection)
        except:
            pass
        
        client.create_collection(
            collection_name=test_collection,
            vectors_config=VectorParams(
                size=1536,  # OpenAI embedding size
                distance=Distance.COSINE
            )
        )
        print(f"✅ Created test collection: {test_collection}")
        
        # Clean up
        client.delete_collection(test_collection)
        print(f"✅ Deleted test collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        print("\nMake sure Qdrant is running:")
        print("  docker run -p 6333:6333 qdrant/qdrant")
        return False


def main():
    """Main test function."""
    print("🚀 Testing ThothAI Qdrant Basic Structure")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    tests = [
        test_document_models,
        test_factory_import,
        test_embedding_manager_structure,
        test_qdrant_connection,
    ]
    
    for test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"\n❌ {test_func.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All structure tests passed!")
        print("\nNote: To test with real embeddings, set OPENAI_API_KEY environment variable")
    else:
        print("❌ Some tests failed")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())