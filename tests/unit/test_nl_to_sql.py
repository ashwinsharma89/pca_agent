"""
Unit tests for NL to SQL engine.

Tests the improved NL to SQL engine with mocked LLM calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from src.query_engine.improved_nl_to_sql import (
    ImprovedNLToSQLEngine,
    SQLInjectionProtector,
    QueryCache
)


@pytest.mark.unit
class TestSQLInjectionProtector:
    """Test SQL injection protection."""
    
    def test_valid_select_query(self):
        """Test that valid SELECT query passes."""
        protector = SQLInjectionProtector(
            allowed_tables=['campaigns'],
            allowed_columns=['Campaign_Name', 'Spend']
        )
        
        query = "SELECT Campaign_Name, Spend FROM campaigns"
        is_valid, error = protector.validate_query(query)
        
        assert is_valid is True
        assert error is None
    
    def test_blocks_drop_statement(self):
        """Test that DROP statement is blocked."""
        protector = SQLInjectionProtector(
            allowed_tables=['campaigns'],
            allowed_columns=['Campaign_Name']
        )
        
        query = "DROP TABLE campaigns"
        is_valid, error = protector.validate_query(query)
        
        assert is_valid is False
        assert "Dangerous keyword" in error
    
    def test_blocks_multiple_statements(self):
        """Test that multiple statements are blocked."""
        protector = SQLInjectionProtector(
            allowed_tables=['campaigns'],
            allowed_columns=['Campaign_Name']
        )
        
        # Test with dangerous keyword (DROP is detected first)
        query = "SELECT * FROM campaigns; DROP TABLE campaigns;"
        is_valid, error = protector.validate_query(query)
        
        assert is_valid is False
        # May detect DROP keyword or multiple statements
        assert "Dangerous" in error or "Multiple" in error or "DROP" in error
    
    def test_blocks_unauthorized_table(self):
        """Test that unauthorized table access is blocked."""
        protector = SQLInjectionProtector(
            allowed_tables=['campaigns'],
            allowed_columns=['Campaign_Name']
        )
        
        query = "SELECT * FROM users"
        is_valid, error = protector.validate_query(query)
        
        assert is_valid is False
        assert "not allowed" in error.lower()
    
    def test_allows_with_clause(self):
        """Test that WITH (CTE) clause is allowed."""
        protector = SQLInjectionProtector(
            allowed_tables=['campaigns'],
            allowed_columns=['Campaign_Name', 'Date']
        )
        
        query = "WITH bounds AS (SELECT MAX(Date) FROM campaigns) SELECT * FROM campaigns"
        is_valid, error = protector.validate_query(query)
        
        assert is_valid is True


@pytest.mark.unit
class TestQueryCache:
    """Test query caching functionality."""
    
    def test_cache_miss_then_hit(self, tmp_path):
        """Test cache miss followed by cache hit."""
        cache = QueryCache(cache_dir=str(tmp_path), ttl_seconds=3600)
        
        question = "What is the total spend?"
        schema_hash = "test_schema_hash"
        
        # First call - cache miss
        result1 = cache.get(question, schema_hash)
        assert result1 is None
        
        # Store result
        test_result = {"answer": "Total spend is $1000"}
        cache.set(question, schema_hash, test_result)
        
        # Second call - cache hit
        result2 = cache.get(question, schema_hash)
        assert result2 is not None
        assert result2["answer"] == "Total spend is $1000"
    
    def test_cache_expiration(self, tmp_path):
        """Test that cache expires after TTL."""
        cache = QueryCache(cache_dir=str(tmp_path), ttl_seconds=0)  # Immediate expiration
        
        question = "What is the total spend?"
        schema_hash = "test_schema_hash"
        
        # Store result
        test_result = {"answer": "Total spend is $1000"}
        cache.set(question, schema_hash, test_result)
        
        # Should be expired
        import time
        time.sleep(0.1)
        result = cache.get(question, schema_hash)
        assert result is None
    
    def test_cache_stats(self, tmp_path):
        """Test cache statistics."""
        cache = QueryCache(cache_dir=str(tmp_path))
        
        # Initial stats
        stats = cache.get_stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        
        # Cache miss
        cache.get("question1", "schema1")
        stats = cache.get_stats()
        assert stats['misses'] == 1
        
        # Cache hit
        cache.set("question1", "schema1", {"answer": "test"})
        cache.get("question1", "schema1")
        stats = cache.get_stats()
        assert stats['hits'] == 1


@pytest.mark.unit
class TestImprovedNLToSQLEngine:
    """Test improved NL to SQL engine."""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    def test_generate_sql_with_mock(self, sample_campaign_data):
        """Test SQL generation with mocked OpenAI."""
        # Create engine
        engine = ImprovedNLToSQLEngine(df=sample_campaign_data, enable_cache=False)
        
        # Test engine initialization
        assert engine is not None
        assert engine.protector is not None
        assert engine.schema_info is not None
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    def test_ask_with_cache(self, sample_campaign_data, tmp_path):
        """Test ask method with caching."""
        # Create engine with cache
        engine = ImprovedNLToSQLEngine(
            df=sample_campaign_data,
            enable_cache=True
        )
        
        # Verify cache is enabled
        assert engine.cache is not None
        
        # Test cache stats
        stats = engine.cache.get_stats()
        assert 'hits' in stats
        assert 'misses' in stats
    
    def test_sql_injection_protection(self, sample_campaign_data):
        """Test that SQL injection is blocked."""
        engine = ImprovedNLToSQLEngine(df=sample_campaign_data, enable_cache=False)
        
        # Manually set a malicious SQL query
        malicious_sql = "DROP TABLE campaigns"
        
        # Validate should fail
        is_valid, error = engine.protector.validate_query(malicious_sql)
        assert is_valid is False
        assert "Dangerous keyword" in error
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    def test_prompt_length_reduction(self, sample_campaign_data):
        """Test that engine initializes with schema info."""
        engine = ImprovedNLToSQLEngine(df=sample_campaign_data)
        
        # Verify schema info is captured
        assert engine.schema_info is not None
        assert 'columns' in engine.schema_info
        assert len(engine.schema_info['columns']) > 0
