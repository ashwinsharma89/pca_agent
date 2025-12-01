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
        
        query = "SELECT * FROM campaigns; DROP TABLE campaigns;"
        is_valid, error = protector.validate_query(query)
        
        assert is_valid is False
        assert "Multiple statements" in error
    
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
        cache = QueryCache(cache_dir=str(tmp_path), ttl=3600)
        
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
        cache = QueryCache(cache_dir=str(tmp_path), ttl=0)  # Immediate expiration
        
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
    
    @patch('src.query_engine.improved_nl_to_sql.OpenAI')
    def test_generate_sql_with_mock(self, mock_openai_class, sample_campaign_data):
        """Test SQL generation with mocked OpenAI."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "SELECT SUM(Spend) AS total_spend FROM campaigns"
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create engine
        engine = ImprovedNLToSQLEngine(df=sample_campaign_data, enable_cache=False)
        
        # Generate SQL
        result = engine.generate_sql("What is the total spend?")
        
        assert result is not None
        assert "SELECT" in result.upper()
        assert mock_client.chat.completions.create.called
    
    def test_ask_with_cache(self, sample_campaign_data, tmp_path):
        """Test ask method with caching."""
        with patch('src.query_engine.improved_nl_to_sql.OpenAI') as mock_openai_class:
            # Setup mock
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "SELECT SUM(Spend) AS total_spend FROM campaigns"
            mock_openai_class.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_response
            
            # Create engine with cache
            engine = ImprovedNLToSQLEngine(
                df=sample_campaign_data,
                enable_cache=True,
                cache_dir=str(tmp_path)
            )
            
            question = "What is the total spend?"
            
            # First call - should call LLM
            result1 = engine.ask(question)
            assert result1['success'] is True
            assert result1['from_cache'] is False
            call_count_1 = mock_client.chat.completions.create.call_count
            
            # Second call - should use cache
            result2 = engine.ask(question)
            assert result2['success'] is True
            assert result2['from_cache'] is True
            call_count_2 = mock_client.chat.completions.create.call_count
            
            # LLM should not be called again
            assert call_count_2 == call_count_1
    
    def test_sql_injection_protection(self, sample_campaign_data):
        """Test that SQL injection is blocked."""
        engine = ImprovedNLToSQLEngine(df=sample_campaign_data, enable_cache=False)
        
        # Manually set a malicious SQL query
        malicious_sql = "DROP TABLE campaigns"
        
        # Validate should fail
        is_valid, error = engine.protector.validate_query(malicious_sql)
        assert is_valid is False
        assert "Dangerous keyword" in error
    
    def test_prompt_length_reduction(self, sample_campaign_data):
        """Test that prompt is significantly shorter."""
        engine = ImprovedNLToSQLEngine(df=sample_campaign_data)
        
        # Generate prompt
        prompt = engine._build_prompt("What is the total spend?")
        
        # Count lines
        line_count = len(prompt.split('\n'))
        
        # Should be under 200 lines (vs 767 in old version)
        assert line_count < 200, f"Prompt has {line_count} lines, should be < 200"
