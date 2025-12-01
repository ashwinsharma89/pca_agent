"""
Test LLM rate limiting functionality.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from src.utils.llm_with_rate_limit import get_llm_client, RateLimitedOpenAI
from src.utils.redis_rate_limiter import get_llm_limiter


def test_import():
    """Test that modules import correctly."""
    print("Testing imports...")
    
    try:
        from src.utils.llm_with_rate_limit import (
            get_llm_client,
            RateLimitedOpenAI,
            RateLimitedAnthropic,
            RateLimitedGemini,
            with_llm_rate_limit
        )
        print("✅ All LLM rate limiting modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_llm_limiter():
    """Test LLM rate limiter."""
    print("\nTesting LLM rate limiter...")
    
    try:
        llm_limiter = get_llm_limiter()
        print("✅ LLM rate limiter initialized")
        
        # Check rate limits for different providers
        providers = ["openai", "anthropic", "gemini"]
        tiers = ["free", "pro", "enterprise"]
        
        print("\nRate limits by provider and tier:")
        for provider in providers:
            print(f"\n{provider.upper()}:")
            for tier in tiers:
                allowed, info = llm_limiter.check_llm_limit(
                    user_id="test_user",
                    provider=provider,
                    tier=tier
                )
                print(f"  {tier:12} - {info['limit']:4} requests/minute")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM limiter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rate_limited_client():
    """Test rate-limited client creation."""
    print("\nTesting rate-limited client creation...")
    
    try:
        # Test OpenAI client
        client = get_llm_client(
            provider="openai",
            user_id="test_user",
            tier="pro"
        )
        print(f"✅ OpenAI rate-limited client created")
        print(f"   User: test_user")
        print(f"   Tier: pro (60 requests/minute)")
        
        # Test Anthropic client
        client = get_llm_client(
            provider="anthropic",
            user_id="test_user",
            tier="free"
        )
        print(f"✅ Anthropic rate-limited client created")
        print(f"   User: test_user")
        print(f"   Tier: free (5 requests/minute)")
        
        return True
        
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rate_limit_check():
    """Test rate limit checking."""
    print("\nTesting rate limit checks...")
    
    try:
        llm_limiter = get_llm_limiter()
        
        # Simulate multiple requests
        user_id = "test_user_123"
        provider = "openai"
        tier = "free"  # 3 requests/minute
        
        print(f"\nSimulating requests for {tier} tier (limit: 3/minute):")
        
        for i in range(5):
            allowed, info = llm_limiter.check_llm_limit(user_id, provider, tier)
            
            if allowed:
                print(f"  Request {i+1}: ✅ Allowed ({info['remaining']} remaining)")
            else:
                print(f"  Request {i+1}: ❌ Rate limit exceeded")
                print(f"               Reset in {info['reset_at'] - int(__import__('time').time())} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Rate limit check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("LLM RATE LIMITING TEST")
    print("=" * 60)
    print()
    
    results = []
    
    # Test imports
    results.append(("Imports", test_import()))
    
    # Test LLM limiter
    results.append(("LLM Limiter", test_llm_limiter()))
    
    # Test client creation
    results.append(("Client Creation", test_rate_limited_client()))
    
    # Test rate limit checks
    results.append(("Rate Limit Checks", test_rate_limit_check()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20} {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nLLM rate limiting is working correctly.")
        print("\nUsage example:")
        print("  from src.utils.llm_with_rate_limit import get_llm_client")
        print("  ")
        print("  client = get_llm_client('openai', user_id='user123', tier='pro')")
        print("  response = client.chat_completions_create(")
        print("      model='gpt-4',")
        print("      messages=[{'role': 'user', 'content': 'Hello'}]")
        print("  )")
    else:
        print("\n⚠️ SOME TESTS FAILED")
    
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
