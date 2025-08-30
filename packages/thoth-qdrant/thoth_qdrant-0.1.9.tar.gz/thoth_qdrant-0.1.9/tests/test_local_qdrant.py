#!/usr/bin/env python3
# Copyright (c) 2025 Marco Pancotti
# This file is part of ThothAI and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""Test script for local Qdrant instance."""

import os
import sys
from typing import List

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from thoth_qdrant import VectorStoreFactory
from thoth_qdrant.core.base import (
    ColumnNameDocument,
    SqlDocument,
    EvidenceDocument,
    ThothType,
)


def test_connection():
    """Test connection to local Qdrant."""
    print("Testing connection to Qdrant at localhost:6333...")
    
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections()
        print(f"✅ Connected successfully! Found {len(collections.collections)} collections")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nMake sure Qdrant is running:")
        print("  docker run -p 6333:6333 qdrant/qdrant")
        return False


def test_crud_operations():
    """Test CRUD operations."""
    print("\n" + "="*50)
    print("Testing CRUD Operations")
    print("="*50)
    
    # Create store
    print("\n1. Creating vector store...")
    store = VectorStoreFactory.create(
        backend="qdrant",
        collection="test_thoth",
        host="localhost",
        port=6333,
        embedding_provider=os.environ.get("EMBEDDING_PROVIDER", "openai"),
        embedding_model=os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    )
    print("✅ Vector store created")
    
    # Add column document
    print("\n2. Adding column document...")
    column_doc = ColumnNameDocument(
        table_name="users",
        column_name="email",
        original_column_name="email_address",
        column_description="User's email address for authentication",
        value_description="Valid email format (e.g., user@example.com)"
    )
    col_id = store.add_column_description(column_doc)
    print(f"✅ Added column document with ID: {col_id}")
    
    # Add SQL document
    print("\n3. Adding SQL document...")
    sql_doc = SqlDocument(
        question="How to find users registered in the last 30 days?",
        sql="SELECT * FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)",
        evidence="Filter by registration date using DATE_SUB"
    )
    sql_id = store.add_sql(sql_doc)
    print(f"✅ Added SQL document with ID: {sql_id}")
    
    # Add evidence document
    print("\n4. Adding evidence document...")
    evidence_doc = EvidenceDocument(
        evidence="Always use indexed columns in WHERE clauses for better performance"
    )
    ev_id = store.add_evidence(evidence_doc)
    print(f"✅ Added evidence document with ID: {ev_id}")
    
    # Get document
    print("\n5. Retrieving document by ID...")
    retrieved = store.get_document(col_id)
    if retrieved and isinstance(retrieved, ColumnNameDocument):
        print(f"✅ Retrieved column document: {retrieved.column_name}")
    else:
        print("❌ Failed to retrieve document")
    
    # Search similar
    print("\n6. Searching similar column documents...")
    results = store.search_similar(
        query="user authentication email",
        doc_type=ThothType.COLUMN_NAME,
        top_k=3,
        score_threshold=0.5
    )
    print(f"✅ Found {len(results)} similar documents")
    for i, doc in enumerate(results, 1):
        if isinstance(doc, ColumnNameDocument):
            print(f"   {i}. {doc.table_name}.{doc.column_name}")
    
    # Collection info
    print("\n7. Getting collection info...")
    info = store.get_collection_info()
    print(f"✅ Collection info:")
    print(f"   - Backend: {info.get('backend')}")
    print(f"   - Points count: {info.get('points_count')}")
    print(f"   - Embedding provider: {info.get('embedding_provider')}")
    
    # Delete document
    print("\n8. Deleting document...")
    store.delete_document(ev_id)
    deleted_check = store.get_document(ev_id)
    if deleted_check is None:
        print("✅ Document deleted successfully")
    else:
        print("❌ Failed to delete document")
    
    return True


def test_bulk_operations():
    """Test bulk operations."""
    print("\n" + "="*50)
    print("Testing Bulk Operations")
    print("="*50)
    
    store = VectorStoreFactory.create(
        backend="qdrant",
        collection="test_bulk",
        host="localhost",
        port=6333,
        embedding_provider=os.environ.get("EMBEDDING_PROVIDER", "openai"),
        embedding_model=os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    )
    
    # Create multiple documents
    documents = [
        ColumnNameDocument(
            table_name="products",
            column_name="price",
            original_column_name="product_price",
            column_description="Product price in USD",
            value_description="Decimal with 2 places"
        ),
        SqlDocument(
            question="Find top selling products",
            sql="SELECT product_id, COUNT(*) as sales FROM orders GROUP BY product_id ORDER BY sales DESC LIMIT 10",
            evidence="Group by product and count sales"
        ),
        EvidenceDocument(
            evidence="Use EXPLAIN to analyze query performance"
        )
    ]
    
    print(f"\n1. Bulk adding {len(documents)} documents...")
    doc_ids = store.bulk_add_documents(documents)
    print(f"✅ Added {len(doc_ids)} documents")
    
    # Get all documents by type
    print("\n2. Getting all documents by type...")
    columns = store.get_all_column_documents()
    sqls = store.get_all_sql_documents()
    evidences = store.get_all_evidence_documents()
    
    print(f"✅ Found:")
    print(f"   - {len(columns)} column documents")
    print(f"   - {len(sqls)} SQL documents")
    print(f"   - {len(evidences)} evidence documents")
    
    # Delete by type
    print("\n3. Deleting all evidence documents...")
    store.delete_collection(ThothType.EVIDENCE)
    evidences_after = store.get_all_evidence_documents()
    print(f"✅ Evidence documents after deletion: {len(evidences_after)}")
    
    return True


def main():
    """Main test function."""
    print("🚀 ThothAI Qdrant Native Implementation Test")
    print("=" * 60)
    
    # Check environment
    provider = os.environ.get("EMBEDDING_PROVIDER", "openai")
    model = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    api_key_set = bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("EMBEDDING_API_KEY"))
    
    print(f"Embedding Provider: {provider}")
    print(f"Embedding Model: {model}")
    print(f"API Key Set: {'✅ Yes' if api_key_set else '❌ No'}")
    
    if not api_key_set:
        print("\n⚠️  Warning: No API key found!")
        print("Set one of the following environment variables:")
        print("  - OPENAI_API_KEY (for OpenAI)")
        print("  - EMBEDDING_API_KEY (generic)")
        return 1
    
    # Test connection
    if not test_connection():
        return 1
    
    try:
        # Run tests
        test_crud_operations()
        test_bulk_operations()
        
        print("\n" + "="*60)
        print("✅ All tests passed successfully!")
        print("="*60)
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())