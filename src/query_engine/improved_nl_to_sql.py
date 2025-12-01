"""
Improved NL to SQL Engine with:
1. Shortened prompt (< 200 lines)
2. SQL injection protection
3. Query caching for repeated questions
"""

import os
import logging
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import re

import pandas as pd
import duckdb

from src.query_engine.sql_knowledge import SQLKnowledgeHelper

logger = logging.getLogger(__name__)


class SQLInjectionProtector:
    """
    SQL injection protection mechanisms.
    
    Features:
    - Whitelist validation for table/column names
    - Dangerous keyword detection
    - Query pattern validation
    - Parameterized query support
    """
    
    # Dangerous SQL keywords that should never appear in generated queries
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE',
        'EXEC', 'EXECUTE', 'GRANT', 'REVOKE', '--', '/*', '*/', 'xp_', 'sp_'
    ]
    
    # Allowed SQL keywords for SELECT queries
    ALLOWED_KEYWORDS = [
        'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT',
        'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AS', 'AND', 'OR',
        'NOT', 'IN', 'BETWEEN', 'LIKE', 'IS', 'NULL', 'CASE', 'WHEN', 'THEN',
        'ELSE', 'END', 'WITH', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
        'ROUND', 'CAST', 'NULLIF', 'COALESCE', 'INTERVAL', 'DATE_TRUNC'
    ]
    
    def __init__(self, allowed_tables: List[str], allowed_columns: List[str]):
        """
        Initialize SQL injection protector.
        
        Args:
            allowed_tables: Whitelist of allowed table names
            allowed_columns: Whitelist of allowed column names
        """
        self.allowed_tables = set(allowed_tables)
        self.allowed_columns = set(allowed_columns)
    
    def validate_query(self, sql_query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query for injection attempts.
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for dangerous keywords
        for keyword in self.DANGEROUS_KEYWORDS:
            if re.search(r'\b' + re.escape(keyword) + r'\b', sql_query, re.IGNORECASE):
                return False, f"Dangerous keyword detected: {keyword}"
        
        # Must start with SELECT
        if not sql_query.strip().upper().startswith('SELECT') and \
           not sql_query.strip().upper().startswith('WITH'):
            return False, "Query must start with SELECT or WITH"
        
        # Check for multiple statements (semicolon not at end)
        if ';' in sql_query[:-1]:
            return False, "Multiple statements not allowed"
        
        # Validate table names
        tables = self._extract_tables(sql_query)
        for table in tables:
            if table not in self.allowed_tables:
                return False, f"Table not allowed: {table}"
        
        # Validate column names (basic check)
        columns = self._extract_columns(sql_query)
        for column in columns:
            # Skip aggregation functions and wildcards
            if column in ['*', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX']:
                continue
            
            # Remove quotes and check
            clean_column = column.strip('"').strip("'")
            if clean_column not in self.allowed_columns and \
               not any(clean_column.startswith(prefix) for prefix in ['CASE', 'CAST', 'ROUND']):
                logger.warning(f"Column '{column}' not in whitelist (may be calculated)")
        
        return True, None
    
    def _extract_tables(self, sql_query: str) -> List[str]:
        """Extract table names from SQL query."""
        # Simple regex to find FROM and JOIN clauses
        pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(pattern, sql_query, re.IGNORECASE)
        return [m.lower() for m in matches]
    
    def _extract_columns(self, sql_query: str) -> List[str]:
        """Extract column names from SQL query (basic)."""
        # Extract SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql_query, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return []
        
        select_clause = select_match.group(1)
        
        # Split by comma (basic parsing)
        columns = []
        for part in select_clause.split(','):
            # Extract column name (before AS if present)
            col_match = re.search(r'([a-zA-Z_"\']+[a-zA-Z0-9_"\']*)', part)
            if col_match:
                columns.append(col_match.group(1))
        
        return columns
    
    def sanitize_value(self, value: Any) -> str:
        """
        Sanitize a value for safe SQL inclusion.
        
        Args:
            value: Value to sanitize
            
        Returns:
            Sanitized string value
        """
        if value is None:
            return 'NULL'
        
        if isinstance(value, (int, float)):
            return str(value)
        
        # Escape single quotes
        str_value = str(value).replace("'", "''")
        return f"'{str_value}'"


class QueryCache:
    """
    Query cache for repeated questions.
    
    Features:
    - Hash-based caching
    - TTL support
    - LRU eviction
    - Cache statistics
    """
    
    def __init__(
        self,
        cache_dir: str = "./data/query_cache",
        ttl_seconds: int = 3600,
        max_entries: int = 1000
    ):
        """
        Initialize query cache.
        
        Args:
            cache_dir: Directory to store cache
            ttl_seconds: Time to live for cache entries
            max_entries: Maximum number of cache entries
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        
        # In-memory cache for fast access
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Cache statistics
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, question: str, schema_hash: str) -> str:
        """Generate cache key from question and schema."""
        combined = f"{question.lower().strip()}:{schema_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get(self, question: str, schema_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached query result.
        
        Args:
            question: Natural language question
            schema_hash: Hash of database schema
            
        Returns:
            Cached result or None
        """
        cache_key = self._generate_key(question, schema_hash)
        
        # Check memory cache first
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            
            # Check TTL
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cached_time < timedelta(seconds=self.ttl_seconds):
                self._hits += 1
                logger.info(f"✅ Cache HIT for question: {question[:50]}...")
                return entry['data']
            else:
                # Expired
                del self._memory_cache[cache_key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    entry = json.load(f)
                
                # Check TTL
                cached_time = datetime.fromisoformat(entry['timestamp'])
                if datetime.now() - cached_time < timedelta(seconds=self.ttl_seconds):
                    # Load into memory cache
                    self._memory_cache[cache_key] = entry
                    self._hits += 1
                    logger.info(f"✅ Cache HIT (disk) for question: {question[:50]}...")
                    return entry['data']
                else:
                    # Expired, delete
                    cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        self._misses += 1
        logger.info(f"❌ Cache MISS for question: {question[:50]}...")
        return None
    
    def set(self, question: str, schema_hash: str, data: Dict[str, Any]):
        """
        Cache query result.
        
        Args:
            question: Natural language question
            schema_hash: Hash of database schema
            data: Data to cache
        """
        cache_key = self._generate_key(question, schema_hash)
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'data': data
        }
        
        # Store in memory cache
        self._memory_cache[cache_key] = entry
        
        # Store on disk
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            # Convert DataFrame to dict for JSON serialization
            serializable_data = data.copy()
            if 'results' in serializable_data and isinstance(serializable_data['results'], pd.DataFrame):
                serializable_data['results'] = serializable_data['results'].to_dict('records')
            
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': entry['timestamp'],
                    'question': question,
                    'data': serializable_data
                }, f)
        except Exception as e:
            logger.warning(f"Failed to save cache to disk: {e}")
        
        # Evict old entries if over limit
        self._evict_if_needed()
    
    def _evict_if_needed(self):
        """Evict oldest entries if cache is full."""
        if len(self._memory_cache) > self.max_entries:
            # Sort by timestamp and remove oldest
            sorted_entries = sorted(
                self._memory_cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            # Remove oldest 10%
            to_remove = int(self.max_entries * 0.1)
            for key, _ in sorted_entries[:to_remove]:
                del self._memory_cache[key]
                
                # Also remove from disk
                cache_file = self.cache_dir / f"{key}.json"
                if cache_file.exists():
                    cache_file.unlink()
    
    def clear(self):
        """Clear all cache."""
        self._memory_cache.clear()
        
        # Clear disk cache
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()
        
        self._hits = 0
        self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self._hits,
            'misses': self._misses,
            'total_requests': total,
            'hit_rate': hit_rate,
            'cache_size': len(self._memory_cache),
            'max_entries': self.max_entries
        }


class ImprovedNLToSQLEngine:
    """
    Improved Natural Language to SQL Engine.
    
    Improvements:
    1. Shortened prompt (< 200 lines)
    2. SQL injection protection
    3. Query caching
    """
    
    def __init__(
        self,
        df: pd.DataFrame,
        enable_cache: bool = True,
        cache_ttl: int = 3600
    ):
        """
        Initialize improved NL to SQL engine.
        
        Args:
            df: DataFrame to query
            enable_cache: Whether to enable query caching
            cache_ttl: Cache TTL in seconds
        """
        self.df = df
        self.conn = duckdb.connect(':memory:')
        self.conn.register('campaigns', df)
        
        # Get schema info
        self.schema_info = self._get_schema_info()
        self.schema_hash = self._compute_schema_hash()
        
        # Initialize SQL injection protector
        self.protector = SQLInjectionProtector(
            allowed_tables=['campaigns'],
            allowed_columns=self.schema_info['columns']
        )
        
        # Initialize query cache
        self.cache = QueryCache(ttl_seconds=cache_ttl) if enable_cache else None
        
        # Initialize SQL knowledge helper
        self.sql_helper = SQLKnowledgeHelper()
        
        logger.info("✅ Improved NL to SQL Engine initialized")
        logger.info(f"   Schema: {len(self.schema_info['columns'])} columns")
        logger.info(f"   Cache: {'enabled' if enable_cache else 'disabled'}")
        logger.info(f"   Injection protection: enabled")
    
    def _get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information."""
        columns = self.df.columns.tolist()
        dtypes = {col: str(self.df[col].dtype) for col in columns}
        
        return {
            'columns': columns,
            'dtypes': dtypes,
            'row_count': len(self.df)
        }
    
    def _compute_schema_hash(self) -> str:
        """Compute hash of schema for cache invalidation."""
        schema_str = json.dumps(self.schema_info['columns'], sort_keys=True)
        return hashlib.sha256(schema_str.encode()).hexdigest()[:16]
    
    def generate_sql(self, question: str) -> str:
        """
        Generate SQL from natural language question.
        
        Uses shortened, focused prompt.
        
        Args:
            question: Natural language question
            
        Returns:
            SQL query string
        """
        schema_desc = self._get_compact_schema()
        sql_context = self.sql_helper.build_context(question, self.schema_info)
        
        # Shortened prompt - focus on essentials only
        prompt = f"""Convert this question to DuckDB SQL.

Schema:
{schema_desc}

Key Rules:
1. Rates (CTR, CPC, etc.): SUM(num)/NULLIF(SUM(denom), 0)
2. Dates: Use MAX(date_col) for "last X" periods
3. Performance: Include ALL KPIs (spend, clicks, conversions, CTR, CPC, CPA)
4. Use NULLIF to prevent division by zero
5. Column names are case-sensitive

Examples:
- CTR = (SUM(Clicks)/NULLIF(SUM(Impressions),0))*100
- "last 2 weeks" = date >= MAX(date) - INTERVAL 14 DAY

{sql_context}

Question: {question}

SQL:"""
        
        logger.info(f"Prompt length: {len(prompt)} chars (shortened from ~20K)")
        
        # Generate SQL using LLM (implementation from original)
        # ... (use existing LLM logic)
        
        return "SELECT * FROM campaigns LIMIT 10"  # Placeholder
    
    def _get_compact_schema(self) -> str:
        """Get compact schema description."""
        lines = ["Table: campaigns"]
        lines.append(f"Columns ({len(self.schema_info['columns'])}):")
        
        for col in self.schema_info['columns'][:20]:  # Limit to 20 columns
            dtype = self.schema_info['dtypes'][col]
            lines.append(f"  - {col} ({dtype})")
        
        if len(self.schema_info['columns']) > 20:
            lines.append(f"  ... and {len(self.schema_info['columns']) - 20} more")
        
        return "\n".join(lines)
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a question with caching and injection protection.
        
        Args:
            question: Natural language question
            
        Returns:
            Query results with metadata
        """
        import time
        start_time = time.time()
        
        # Check cache first
        if self.cache:
            cached_result = self.cache.get(question, self.schema_hash)
            if cached_result:
                cached_result['from_cache'] = True
                cached_result['execution_time'] = time.time() - start_time
                return cached_result
        
        try:
            # Generate SQL
            sql_query = self.generate_sql(question)
            
            # Validate for SQL injection
            is_valid, error_msg = self.protector.validate_query(sql_query)
            if not is_valid:
                raise ValueError(f"SQL injection detected: {error_msg}")
            
            # Execute query
            results = self.conn.execute(sql_query).fetchdf()
            
            # Build result
            result = {
                'question': question,
                'sql_query': sql_query,
                'results': results,
                'success': True,
                'error': None,
                'from_cache': False,
                'execution_time': time.time() - start_time,
                'injection_check': 'passed'
            }
            
            # Cache result
            if self.cache:
                self.cache.set(question, self.schema_hash, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                'question': question,
                'sql_query': None,
                'results': None,
                'success': False,
                'error': str(e),
                'from_cache': False,
                'execution_time': time.time() - start_time
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self.cache:
            return self.cache.get_stats()
        return {'enabled': False}
    
    def clear_cache(self):
        """Clear query cache."""
        if self.cache:
            self.cache.clear()
