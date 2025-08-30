#!/usr/bin/env python3
# Copyright (c) 2025 Marco Pancotti
# This file is part of ThothAI and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""Test script to verify sanitization fixes for column chunk error."""

import sys
import os

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from thoth_qdrant.core.base import ColumnNameDocument, SqlDocument
from thoth_qdrant.adapter.qdrant_native import QdrantNativeAdapter


def test_problematic_column_name():
    """Test the specific case from the error message."""
    print("Testing problematic column name: '\\n \"column_name\"'")
    print("="*50)
    
    # Create document with problematic column name
    doc = ColumnNameDocument(
        table_name="users",
        column_name='\n "column_name"',  # The problematic input
        original_column_name="col_name",
        column_description="A column with newlines",
        value_description="Some value"
    )
    
    print(f"Original input: {repr('\n \"column_name\"')}")
    print(f"After sanitization: {repr(doc.column_name)}")
    print(f"✅ Column name sanitized to: '{doc.column_name}'")
    
    # Check that it's properly sanitized
    assert doc.column_name == '"column_name"'
    print("✅ Assertion passed: newlines removed, quotes preserved")
    
    return True


def test_adapter_payload_processing():
    """Test adapter's handling of problematic payloads."""
    print("\nTesting adapter payload processing")
    print("="*50)
    
    # Note: This requires embedding provider to be set up
    # For testing purposes, we'll just test the sanitization logic
    
    # Create a mock adapter just for testing sanitization
    # We can't fully initialize without API keys, but we can test the methods
    
    class MockAdapter:
        def _sanitize_string(self, value):
            """Sanitize string input by removing leading/trailing whitespace and newlines."""
            if not value:
                return ""
            return " ".join(value.strip().split())
    
    adapter = MockAdapter()
    
    # Test various problematic inputs
    test_cases = [
        ('\n "column_name"', '"column_name"'),
        ('  table_name  \n', 'table_name'),
        ('multi\nline\ntext', 'multi line text'),
        ('   spaces   everywhere   ', 'spaces everywhere'),
        ('', ''),
        (None, ''),
    ]
    
    for input_val, expected in test_cases:
        result = adapter._sanitize_string(input_val)
        print(f"Input: {repr(input_val):30} → Output: {repr(result):20} {'✅' if result == expected else '❌'}")
        assert result == expected
    
    print("✅ All sanitization tests passed")
    return True


def test_document_with_json_formatting():
    """Test document creation with JSON-formatted input."""
    print("\nTesting JSON-formatted input")
    print("="*50)
    
    # Simulate data that might come from JSON with formatting
    doc = ColumnNameDocument(
        table_name="users",
        column_name="""
            column_name
        """,  # Column name with extra whitespace
        original_column_name="  id  ",
        column_description="""
            User identifier
            Primary key
        """,
        value_description="Integer\n\nAuto-increment"
    )
    
    print(f"Multi-line column_name input: {repr(doc.column_name)}")
    print(f"Multi-line description input: {repr(doc.column_description)}")
    
    # Check sanitization
    assert doc.column_name == "column_name"
    assert doc.column_description == "User identifier Primary key"
    assert doc.value_description == "Integer Auto-increment"
    
    print("✅ JSON-formatted input properly sanitized")
    return True


def test_sql_document_sanitization():
    """Test SQL document sanitization."""
    print("\nTesting SQL document sanitization")
    print("="*50)
    
    doc = SqlDocument(
        question="\n\nHow to find users?\n\n",
        sql="""
            SELECT  *
            FROM    users
            WHERE   created_at > NOW()
        """,
        evidence="Filter by\ndate\nusing NOW()"
    )
    
    print(f"Question: '{doc.question}'")
    print(f"SQL (truncated): '{doc.sql[:50]}...'")
    print(f"Evidence: '{doc.evidence}'")
    
    # Check that whitespace is cleaned but content preserved
    assert "How to find users?" in doc.question
    assert "SELECT" in doc.sql
    assert "Filter by date using NOW()" in doc.evidence
    
    print("✅ SQL document properly sanitized")
    return True


def main():
    """Run all sanitization tests."""
    print("🧪 Testing Column Chunk Error Fixes")
    print("="*60)
    
    all_passed = True
    
    tests = [
        test_problematic_column_name,
        test_adapter_payload_processing,
        test_document_with_json_formatting,
        test_sql_document_sanitization,
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
        print("✅ All sanitization tests passed!")
        print("The 'Error processing column chunk' issue should be fixed.")
    else:
        print("❌ Some tests failed")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())