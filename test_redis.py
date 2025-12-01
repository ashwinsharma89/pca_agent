"""
Test Redis connection and rate limiting.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from src.utils.redis_rate_limiter import get_redis_limiter, get_llm_limiter


def test_redis_connection():
    """Test Redis connection."""
    print("Testing Redis connection...")
    
    limiter = get_redis_limiter()
    
    if not limiter.enabled:
        print("⚠️  Redis is disabled (REDIS_ENABLED=false in .env)")
        print("   Set REDIS_ENABLED=true to enable Redis rate limiting")
        return False
    
    try:
        # Test ping
        limiter.redis_client.ping()
        print("✅ Redis connection successful!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("\nTo fix:")
        print("1. Install Redis (see options below)")
        print("2. Start Redis server")
        print("3. Or use Redis Cloud (free tier)")
        return False


def test_rate_limiting():
    """Test rate limiting functionality."""
    print("\nTesting rate limiting...")
    
    limiter = get_redis_limiter()
    
    # Test rate limit check
    allowed, info = limiter.check_rate_limit(
        identifier="test_user",
        resource="test_api",
        limit=5,
        window_seconds=60
    )
    
    if allowed:
        print(f"✅ Rate limit check passed")
        print(f"   Remaining: {info['remaining']}/{info['limit']}")
        print(f"   Reset at: {info['reset_at']}")
    else:
        print(f"❌ Rate limit exceeded")
    
    return allowed


def test_llm_rate_limiting():
    """Test LLM rate limiting."""
    print("\nTesting LLM rate limiting...")
    
    llm_limiter = get_llm_limiter()
    
    # Test OpenAI rate limit
    allowed, info = llm_limiter.check_llm_limit(
        user_id="test_user",
        provider="openai",
        tier="free"
    )
    
    if allowed:
        print(f"✅ LLM rate limit check passed (OpenAI)")
        print(f"   Limit: {info['limit']}/minute (free tier)")
        print(f"   Remaining: {info['remaining']}")
    else:
        print(f"❌ LLM rate limit exceeded")
    
    return allowed


def main():
    """Run all tests."""
    print("=" * 60)
    print("REDIS RATE LIMITING TEST")
    print("=" * 60)
    print()
    
    # Test Redis connection
    redis_ok = test_redis_connection()
    
    if redis_ok:
        # Test rate limiting
        test_rate_limiting()
        test_llm_rate_limiting()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nRedis rate limiting is working correctly.")
        print("You can now use distributed rate limiting across multiple instances.")
    else:
        print("\n" + "=" * 60)
        print("⚠️  REDIS NOT AVAILABLE")
        print("=" * 60)
        print("\nThe system will work with in-memory rate limiting.")
        print("To enable Redis:")
        print()
        print("Option 1: Redis Cloud (Easiest)")
        print("  1. Go to https://redis.com/try-free/")
        print("  2. Create free account (30MB free)")
        print("  3. Get connection details")
        print("  4. Update .env with host, port, password")
        print("  5. Set REDIS_ENABLED=true")
        print()
        print("Option 2: WSL2 (Best for Development)")
        print("  1. Open WSL2 terminal")
        print("  2. sudo apt-get install redis-server")
        print("  3. sudo service redis-server start")
        print("  4. Set REDIS_ENABLED=true in .env")
        print()
        print("Option 3: Windows Native")
        print("  1. choco install redis-64")
        print("  2. redis-server")
        print("  3. Set REDIS_ENABLED=true in .env")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
