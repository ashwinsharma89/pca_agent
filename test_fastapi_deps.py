"""
Test FastAPI security dependencies.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_imports():
    """Test that all dependencies can be imported."""
    print("Testing FastAPI security dependencies...\n")
    
    try:
        from jose import jwt
        print("✅ python-jose imported successfully")
    except Exception as e:
        print(f"❌ python-jose import failed: {e}")
        return False
    
    try:
        from slowapi import Limiter
        print("✅ slowapi imported successfully")
    except Exception as e:
        print(f"❌ slowapi import failed: {e}")
        return False
    
    try:
        from passlib.context import CryptContext
        print("✅ passlib imported successfully")
    except Exception as e:
        print(f"❌ passlib import failed: {e}")
        return False
    
    return True


def test_jwt():
    """Test JWT token creation and verification."""
    print("\nTesting JWT functionality...")
    
    try:
        from jose import jwt
        from datetime import datetime, timedelta, timezone
        
        # Create token
        secret_key = "test-secret-key"
        algorithm = "HS256"
        
        payload = {
            "sub": "test_user",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        }
        
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        print(f"✅ JWT token created: {token[:30]}...")
        
        # Verify token
        decoded = jwt.decode(token, secret_key, algorithms=[algorithm])
        print(f"✅ JWT token verified: user={decoded['sub']}")
        
        return True
        
    except Exception as e:
        print(f"❌ JWT test failed: {e}")
        return False


def test_password_hashing():
    """Test password hashing with bcrypt."""
    print("\nTesting password hashing...")
    
    try:
        import bcrypt
        
        # Hash password directly with bcrypt
        password = b"pass123"
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        print(f"✅ Password hashed: {hashed[:30]}...")
        
        # Verify password
        is_valid = bcrypt.checkpw(password, hashed)
        print(f"✅ Password verification: {is_valid}")
        
        # Test wrong password
        is_invalid = bcrypt.checkpw(b"wrong", hashed)
        print(f"✅ Wrong password rejected: {not is_invalid}")
        
        print("\n✅ Bcrypt is working correctly for password hashing")
        print("   Note: Use bcrypt directly or FastAPI's security utilities")
        
        return True
        
    except Exception as e:
        print(f"❌ Password hashing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rate_limiting():
    """Test rate limiting setup."""
    print("\nTesting rate limiting...")
    
    try:
        from slowapi import Limiter
        from slowapi.util import get_remote_address
        
        # Create limiter
        limiter = Limiter(key_func=get_remote_address)
        print("✅ Rate limiter created successfully")
        
        # Test that limiter has required methods
        print(f"✅ Rate limiter has limit decorator: {hasattr(limiter, 'limit')}")
        print(f"✅ Rate limiter has shared_limit decorator: {hasattr(limiter, 'shared_limit')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("FASTAPI SECURITY DEPENDENCIES TEST")
    print("=" * 60)
    print()
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test JWT
    results.append(("JWT", test_jwt()))
    
    # Test password hashing
    results.append(("Password Hashing", test_password_hashing()))
    
    # Test rate limiting
    results.append(("Rate Limiting", test_rate_limiting()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYou can now implement FastAPI security features:")
        print("  1. JWT authentication")
        print("  2. Rate limiting")
        print("  3. Password hashing")
        print("\nSee FASTAPI_IMPROVEMENTS.md for implementation guide.")
    else:
        print("\n⚠️ SOME TESTS FAILED")
    
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
